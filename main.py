# -*- coding: utf-8 -*-
"""
================================================================
 무의식 재판소 - 드림 인젝터 (Dream Injector)
 Flask 기반 API 백엔드
----------------------------------------------------------------
 [OOP 핵심 요구사항]
  1) 클래스 3개 이상: Interpreter 부모 + 3개 자식 + Dream + DreamCensorshipCourt
  2) 다형성: process(dream_text, option) 오버라이딩
  3) 매직 메소드: __str__, __len__, __repr__, __call__
  4) 사용자 정의 예외: UnprocessableDreamError, InvalidInterpreterError, InvalidOptionError
================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import hashlib
import os
import random
from typing import Any, Optional

from flask import Flask, jsonify, request, send_from_directory


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "public"))

app = Flask(__name__, static_folder=PUBLIC_DIR, static_url_path="")


# ================================================================
# [SECTION A] 사용자 정의 예외
# ================================================================
class DreamInjectorError(Exception):
    """드림 인젝터 시스템 최상위 예외 클래스."""

    status_code = 400

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        payload: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code or self.status_code
        self.payload = payload or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": False,
            "error": self.__class__.__name__,
            "message": self.message,
            **self.payload,
        }


class UnprocessableDreamError(DreamInjectorError):
    """꿈 텍스트가 처리 가능한 조건을 만족하지 못할 때 발생."""

    status_code = 422


class InvalidInterpreterError(DreamInjectorError):
    """존재하지 않는 해석가를 선택했을 때 발생."""

    status_code = 404


class InvalidOptionError(DreamInjectorError):
    """해석가의 가공 옵션이 유효하지 않을 때 발생."""

    status_code = 400


# ================================================================
# [SECTION B] Dream 데이터 클래스
# ================================================================
class Dream:
    """시민의 원시 꿈 데이터(Raw Dream)를 표현하는 클래스."""

    MIN_LENGTH = 10
    MAX_LENGTH = 1000

    def __init__(self, raw_text: str, citizen_id: Optional[str] = None) -> None:
        if not isinstance(raw_text, str):
            raise UnprocessableDreamError("꿈 데이터는 텍스트 형식이어야 합니다.")

        cleaned = raw_text.strip()
        length = len(cleaned)

        if length < self.MIN_LENGTH:
            raise UnprocessableDreamError(
                f"무의식 단편이 너무 짧습니다. 최소 {self.MIN_LENGTH}자 이상의 꿈 조각이 필요합니다.",
                payload={"current_length": length, "min_length": self.MIN_LENGTH},
            )

        if length > self.MAX_LENGTH:
            raise UnprocessableDreamError(
                f"꿈 데이터가 너무 깁니다. 최대 {self.MAX_LENGTH}자까지만 입력할 수 있습니다.",
                payload={"current_length": length, "max_length": self.MAX_LENGTH},
            )

        self.raw_text = cleaned
        self.citizen_id = citizen_id or self._generate_citizen_id(cleaned)
        self.timestamp = datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _generate_citizen_id(text: str) -> str:
        hashed_text = hashlib.sha256(text.encode("utf-8")).hexdigest()[:8].upper()
        return f"CITIZEN-{hashed_text}"

    def preview(self, limit: int = 30) -> str:
        """긴 꿈 텍스트를 화면 표시용으로 안전하게 줄인다."""
        suffix = "..." if len(self.raw_text) > limit else ""
        return f"{self.raw_text[:limit]}{suffix}"

    # ---- 매직 메소드 ----
    def __len__(self) -> int:
        return len(self.raw_text)

    def __str__(self) -> str:
        return f"[{self.citizen_id}] 원시 꿈({len(self)}자): {self.preview()}"

    def __repr__(self) -> str:
        return f"Dream(citizen_id={self.citizen_id!r}, length={len(self)})"


# ================================================================
# [SECTION C] Interpreter 부모 클래스
# ================================================================
class Interpreter(ABC):
    """모든 꿈 해석가가 반드시 상속해야 하는 추상 부모 클래스."""

    def __init__(self, name: str, title: str, options: list[str]) -> None:
        self.name = name
        self.title = title
        self.options = options

    @abstractmethod
    def process(self, dream_text: str, option: str) -> dict[str, Any]:
        """다형성의 핵심: 자식 클래스에서 각자의 방식으로 오버라이딩한다."""
        raise NotImplementedError

    def validate_option(self, option: str) -> None:
        if option not in self.options:
            raise InvalidOptionError(
                f"'{self.name}' 해석가는 '{option}' 가공 방식을 지원하지 않습니다.",
                payload={"available_options": self.options},
            )

    def _base_result(self, option: str, verdict: str, risk_level: str, tag: str) -> dict[str, Any]:
        """자식 클래스들의 중복 반환 구조를 줄이기 위한 공통 메서드."""
        return {
            "interpreter": self.name,
            "title": self.title,
            "option": option,
            "verdict": verdict,
            "risk_level": risk_level,
            "tag": tag,
        }

    # ---- 매직 메소드 ----
    def __str__(self) -> str:
        return f"해석가 [{self.name}] - {self.title} | 가공방식: {', '.join(self.options)}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, options={len(self.options)})"

    def __call__(self, dream_text: str, option: str) -> dict[str, Any]:
        return self.process(dream_text, option)


# ================================================================
# [SECTION D] 3명의 자식 해석가
# ================================================================
class ProfessorInterpreter(Interpreter):
    """학술적·논리적 관점에서 꿈을 해석하는 교수형 해석가."""

    def __init__(self) -> None:
        super().__init__(
            name="프로페서 K. 융그",
            title="국립 무의식 연구소 명예교수",
            options=["프로이트식 분석", "융의 원형 해석", "라캉식 기호해석", "구조주의 분해"],
        )

    def process(self, dream_text: str, option: str) -> dict[str, Any]:
        self.validate_option(option)
        templates = {
            "프로이트식 분석": (
                f"'{dream_text[:20]}...' 이 꿈은 억압된 욕망이 상징적 이미지로 치환되어 "
                "표면화된 사례로 해석할 수 있소."
            ),
            "융의 원형 해석": (
                f"'{dream_text[:15]}...'의 장면에는 그림자(Shadow) 원형이 강하게 드러나오. "
                "이는 자기실현을 향한 무의식의 신호일 수 있소."
            ),
            "라캉식 기호해석": (
                f"'{dream_text[:15]}...' 구조 속에서 기표와 기의의 어긋남이 관찰되오. "
                "이 꿈은 실재계의 균열을 암시하오."
            ),
            "구조주의 분해": (
                "꿈을 이항대립으로 분해하면 [상승/하강], [추격자/피추격자]의 구조가 보이오. "
                "이는 내면화된 권력 관계의 투영일 수 있소."
            ),
        }
        return self._base_result(
            option=option,
            verdict=templates[option],
            risk_level=random.choice(["LOW", "MEDIUM", "HIGH"]),
            tag="ACADEMIC",
        )


class MBTIInterpreter(Interpreter):
    """성격유형 관점에서 꿈을 해석하는 해석가."""

    def __init__(self) -> None:
        super().__init__(
            name="MBTI 큐레이터 미나",
            title="시민 성격유형 적합도 분석관",
            options=["INTJ 전략형", "ENFP 활동가형", "ISFJ 수호자형", "ESTP 사업가형"],
        )

    def process(self, dream_text: str, option: str) -> dict[str, Any]:
        self.validate_option(option)
        templates = {
            "INTJ 전략형": (
                f"'{dream_text[:15]}...' — 이 꿈은 미완의 마스터플랜을 상징해요. "
                "전략적 좌절감이 무의식에 누적된 신호일 수 있습니다."
            ),
            "ENFP 활동가형": (
                f"ENFP에게 '{dream_text[:15]}...'는 새로운 가능성의 문을 여는 이미지예요. "
                "직관과 호기심이 강하게 작동하고 있습니다."
            ),
            "ISFJ 수호자형": (
                f"'{dream_text[:15]}...'은 소중한 사람을 지키고 싶은 마음과 연결돼요. "
                "헌신의 그림자가 꿈으로 나타난 모습입니다."
            ),
            "ESTP 사업가형": (
                f"ESTP에게 '{dream_text[:15]}...'는 지루한 일상에 대한 반란이에요. "
                "현실에서 더 큰 자극과 도전이 필요하다는 신호일 수 있습니다."
            ),
        }
        return self._base_result(
            option=option,
            verdict=templates[option],
            risk_level=random.choice(["LOW", "MEDIUM"]),
            tag="PERSONALITY",
        )


class TherapistInterpreter(Interpreter):
    """심리치료사 관점에서 꿈을 부드럽게 가공하는 해석가."""

    def __init__(self) -> None:
        super().__init__(
            name="닥터 소피아 림",
            title="국가공인 임상 무의식 치료사",
            options=["인지행동치료(CBT)", "정신역동 치료", "마음챙김 가공", "EMDR 안구재처리"],
        )

    def process(self, dream_text: str, option: str) -> dict[str, Any]:
        self.validate_option(option)
        templates = {
            "인지행동치료(CBT)": (
                f"'{dream_text[:15]}...'에서 느낀 두려움은 인지 왜곡과 연결될 수 있어요. "
                "현실 검증을 통해 안전한 방식으로 재해석했습니다."
            ),
            "정신역동 치료": (
                f"'{dream_text[:15]}...'의 정서는 오래된 미해결 감정과 닿아 있을 수 있어요. "
                "그 감정을 천천히 인식하고 통합하는 과정이 필요합니다."
            ),
            "마음챙김 가공": (
                f"호흡과 함께 '{dream_text[:15]}...'의 이미지를 흘려보내세요. "
                "지금 이 순간의 안전감에 주의를 돌려봅니다."
            ),
            "EMDR 안구재처리": (
                f"'{dream_text[:15]}...'의 강렬한 장면을 안전한 거리에서 바라보도록 재처리합니다. "
                "이제 이 장면은 단순한 회상으로 분리됩니다."
            ),
        }
        return self._base_result(
            option=option,
            verdict=templates[option],
            risk_level="LOW",
            tag="THERAPEUTIC",
        )


# ================================================================
# [SECTION E] 무의식 재판소 컨트롤러
# ================================================================
class DreamCensorshipCourt:
    """플레이어가 사용하는 재판소 본부."""

    def __init__(self) -> None:
        self.interpreters: dict[str, Interpreter] = {
            "professor": ProfessorInterpreter(),
            "mbti": MBTIInterpreter(),
            "therapist": TherapistInterpreter(),
        }
        self.history: list[dict[str, Any]] = []

    def get_interpreter(self, key: str) -> Interpreter:
        normalized_key = (key or "").lower().strip()
        if normalized_key not in self.interpreters:
            raise InvalidInterpreterError(
                f"'{normalized_key}'라는 해석가는 재판소에 등록되어 있지 않습니다.",
                payload={"available_interpreters": list(self.interpreters.keys())},
            )
        return self.interpreters[normalized_key]

    def interpret(self, raw_text: str, interpreter_key: str, option: str) -> dict[str, Any]:
        dream = Dream(raw_text)
        interpreter = self.get_interpreter(interpreter_key)
        normalized_option = (option or "").strip()

        # __call__ 매직 메소드 활용 → 다형성 process() 호출
        result = interpreter(dream.raw_text, normalized_option)
        result.update(
            {
                "dream_meta": {
                    "citizen_id": dream.citizen_id,
                    "length": len(dream),
                    "timestamp": dream.timestamp,
                    "summary": str(dream),
                }
            }
        )
        self.history.append(result)
        return result

    def get_recent_history(self, limit: int = 5) -> list[dict[str, Any]]:
        """최근 처리 내역 일부만 반환한다."""
        return self.history[-limit:]

    def __len__(self) -> int:
        return len(self.history)

    def __str__(self) -> str:
        return f"무의식 재판소 | 등록 해석가 {len(self.interpreters)}명 | 누적 처리 {len(self)}건"

    def __repr__(self) -> str:
        return f"DreamCensorshipCourt(interpreters={list(self.interpreters.keys())!r}, processed={len(self)})"


COURT = DreamCensorshipCourt()


# ================================================================
# [SECTION F] Flask API 엔드포인트
# ================================================================
@app.errorhandler(DreamInjectorError)
def handle_dream_error(error: DreamInjectorError):
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({"ok": False, "error": "NotFound", "message": "요청한 API 경로를 찾을 수 없습니다."}), 404


@app.errorhandler(500)
def handle_internal_error(error):
    return jsonify({"ok": False, "error": "InternalServerError", "message": "서버 내부 오류가 발생했습니다."}), 500


@app.get("/api/interpreters")
def list_interpreters():
    """등록된 해석가 및 각자의 가공 옵션 목록 반환."""
    data = [
        {
            "key": key,
            "name": interpreter.name,
            "title": interpreter.title,
            "options": interpreter.options,
            "display": str(interpreter),
        }
        for key, interpreter in COURT.interpreters.items()
    ]
    return jsonify({"ok": True, "interpreters": data, "court": str(COURT)})


@app.post("/api/interpret")
def interpret_dream():
    """
    꿈을 해석/가공하는 메인 엔드포인트.
    body: { "dream": "...", "interpreter": "professor|mbti|therapist", "option": "..." }
    """
    body = request.get_json(silent=True)
    if body is None:
        raise UnprocessableDreamError("JSON 형식의 요청 본문이 필요합니다.")

    dream_text = body.get("dream", "")
    interpreter_key = body.get("interpreter", "")
    option = body.get("option", "")

    if not interpreter_key:
        raise InvalidInterpreterError("해석가를 선택해 주세요.")
    if not option:
        raise InvalidOptionError("가공 방식을 선택해 주세요.")

    result = COURT.interpret(dream_text, interpreter_key, option)
    return jsonify({"ok": True, "result": result}), 201


@app.get("/api/history")
def get_history():
    """최근 꿈 해석 기록 반환. GitHub 시연용 보조 API."""
    limit = request.args.get("limit", default=5, type=int)
    limit = max(1, min(limit, 20))
    return jsonify({"ok": True, "count": len(COURT), "history": COURT.get_recent_history(limit)})


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "status": "healthy", "court": str(COURT), "processed": len(COURT)})


@app.get("/")
def index():
    """public/index.html이 있으면 서빙하고, 없으면 API 안내 문구를 반환한다."""
    index_path = os.path.join(PUBLIC_DIR, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(PUBLIC_DIR, "index.html")

    return jsonify(
        {
            "ok": True,
            "service": "Dream Injector API",
            "endpoints": ["GET /api/health", "GET /api/interpreters", "POST /api/interpret", "GET /api/history"],
        }
    )


# ================================================================
# [SECTION G] 로컬 실행 진입점
# ================================================================
if __name__ == "__main__":
    print(COURT)
    for key, interpreter in COURT.interpreters.items():
        print(f" - {key}: {interpreter}")

    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
