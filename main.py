# -*- coding: utf-8 -*-
"""
================================================================
 무의식 재판소 - 드림 인젝터 (Dream Injector)
 PART 1. Python 백엔드 (Flask 기반 API)
----------------------------------------------------------------
 [OOP 핵심 요구사항 체크리스트]
  1) 클래스 3개 이상 (Interpreter 부모 + 3개 자식 + Dream + DreamCensorshipCourt)
  2) 다형성: process(dream_text, option) 오버라이딩
  3) 매직 메소드: __str__, __len__, __repr__, __call__
  4) 사용자 정의 예외: UnprocessableDreamError, InvalidInterpreterError, InvalidOptionError
================================================================
"""

from flask import Flask, request, jsonify, send_from_directory
from abc import ABC, abstractmethod
import random
import hashlib
import os
import datetime

app = Flask(__name__, static_folder='../public', static_url_path='')

# ================================================================
# [SECTION A] 사용자 정의 예외 (Custom Exceptions)
# ================================================================
class DreamInjectorError(Exception):
    """드림 인젝터 시스템 최상위 예외 클래스."""
    status_code = 400
    
    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload or {}
        
    def to_dict(self):
        return {"error": self.__class__.__name__, "message": self.message, **self.payload}

class UnprocessableDreamError(DreamInjectorError):
    """꿈 텍스트가 10자 미만일 때 발생."""
    status_code = 422

class InvalidInterpreterError(DreamInjectorError):
    """존재하지 않는 해석가를 선택했을 때 발생."""
    status_code = 404

class InvalidOptionError(DreamInjectorError):
    """해석가의 가공 옵션이 유효하지 않을 때 발생."""
    status_code = 400

# ================================================================
# [SECTION B] Dream 데이터 클래스 (원시 꿈 데이터 캡슐화)
# ================================================================
class Dream:
    """시민의 원시 꿈 데이터(Raw Dream)를 표현하는 클래스."""
    MIN_LENGTH = 10
    
    def __init__(self, raw_text: str, citizen_id: str = None):
        if not isinstance(raw_text, str):
            raise UnprocessableDreamError("꿈 데이터는 텍스트 형식이어야 합니다.")
            
        cleaned = raw_text.strip()
        if len(cleaned) < self.MIN_LENGTH:
            raise UnprocessableDreamError(
                f"무의식 단편이 너무 짧습니다. 최소 {self.MIN_LENGTH}자 이상의 꿈 조각이 필요합니다. (현재 {len(cleaned)}자)"
            )
            
        self.raw_text = cleaned
        self.citizen_id = citizen_id or self._generate_citizen_id(cleaned)
        self.timestamp = datetime.datetime.utcnow().isoformat()
        
    @staticmethod
    def _generate_citizen_id(text: str) -> str:
        h = hashlib.sha256(text.encode("utf-8")).hexdigest()[:8].upper()
        return f"CITIZEN-{h}"
        
    # ---- 매직 메소드 ----
    def __len__(self):
        """매직메소드 ①: len(dream)으로 꿈 텍스트 길이를 반환."""
        return len(self.raw_text)
        
    def __str__(self):
        """매직메소드 ②: 꿈 데이터의 사용자 친화적 표현."""
        return f"[{self.citizen_id}] 원시 꿈({len(self)}자): {self.raw_text[:30]}..."
        
    def __repr__(self):
        """매직메소드 ③: 디버깅용 정식 표현."""
        return f"Dream(citizen_id={self.citizen_id!r}, length={len(self)})"

# ================================================================
# [SECTION C] Interpreter 부모 클래스 (추상 베이스)
# ================================================================
class Interpreter(ABC):
    """
    모든 꿈 해석가가 반드시 상속해야 하는 추상 부모 클래스.
    다형성을 강제하기 위해 process()를 추상 메소드로 선언.
    """
    def __init__(self, name: str, title: str, options: list):
        self.name = name
        self.title = title
        self.options = options # 각 해석가는 4가지 가공방식을 보유
        
    @abstractmethod
    def process(self, dream_text: str, option: str) -> dict:
        """
        다형성(Polymorphism)의 핵심.
        부모는 시그니처만 정의하고, 자식이 각자의 방식으로 오버라이딩한다.
        """
        raise NotImplementedError
        
    def validate_option(self, option: str):
        if option not in self.options:
            raise InvalidOptionError(
                f"'{self.name}' 해석가는 '{option}' 가공 방식을 모릅니다. "
                f"사용 가능: {self.options}"
            )
            
    # ---- 매직 메소드 ----
    def __str__(self):
        return f"해석가 [{self.name}] - {self.title} | 가공방식: {self.options}"
        
    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"
        
    def __call__(self, dream_text, option):
        """매직메소드 ④: interpreter(dream_text, option) 호출 가능하게 함."""
        return self.process(dream_text, option)

# ================================================================
# [SECTION D] 3명의 자식 해석가 (다형성 구현)
# ================================================================
class ProfessorInterpreter(Interpreter):
    """학술적·논리적 관점에서 꿈을 해석하는 교수형 해석가."""
    def __init__(self):
        super().__init__(
            name="프로페서 K. 융그",
            title="국립 무의식 연구소 명예교수",
            options=["프로이트식 분석", "융의 원형 해석", "라캉식 기호해석", "구조주의 분해"]
        )
        
    def process(self, dream_text: str, option: str) -> dict:
        self.validate_option(option)
        templates = {
            "프로이트식 분석": (
                f"'{dream_text[:20]}...' 이 꿈은 명백한 억압된 욕망의 발현이오. "
                "유년기의 미해결 갈등이 상징적 이미지로 치환되어 표면화된 것이지."
            ),
            "융의 원형 해석": (
                f"자네의 꿈에는 '그림자(Shadow)' 원형이 강하게 드러나는군. "
                f"'{dream_text[:15]}...'의 장면은 집단무의식 깊은 곳의 자기실현 충동이오."
            ),
            "라캉식 기호해석": (
                f"이 꿈은 '실재계'의 균열을 보여주오. 기표와 기의의 어긋남이 "
                f"'{dream_text[:15]}...' 구조 속에서 미끄러지고 있음."
            ),
            "구조주의 분해": (
                f"꿈을 이항대립으로 분해하면: [상승/하강], [추격자/피추격자]. "
                f"이는 사회적 권력 구조의 내면화된 투영이오."
            ),
        }
        verdict = templates[option]
        return {
            "interpreter": self.name,
            "title": self.title,
            "option": option,
            "verdict": verdict,
            "risk_level": random.choice(["LOW", "MEDIUM", "HIGH"]),
            "tag": "ACADEMIC"
        }

class MBTIInterpreter(Interpreter):
    """성격유형(MBTI) 관점에서 꿈을 해석하는 해석가."""
    def __init__(self):
        super().__init__(
            name="MBTI 큐레이터 미나",
            title="시민 성격유형 적합도 분석관",
            options=["INTJ 전략형", "ENFP 활동가형", "ISFJ 수호자형", "ESTP 사업가형"]
        )
        
    def process(self, dream_text: str, option: str) -> dict:
        self.validate_option(option)
        templates = {
            "INTJ 전략형": (
                f"'{dream_text[:15]}...' — INTJ 시민에게 이 꿈은 '미완의 마스터플랜'을 의미해요. "
                "전략적 좌절감이 무의식에 누적된 신호입니다."
            ),
            "ENFP 활동가형": (
                f"ENFP에게 '{dream_text[:15]}...'는 '새로운 가능성의 문'을 열어주는 꿈! "
                "직관(Ne)이 폭발하기 직전이에요."
            ),
            "ISFJ 수호자형": (
                f"ISFJ 시민에게 이 꿈은 '소중한 사람을 잃을까 두려운 마음'의 표현. "
                f"'{dream_text[:15]}...'은 헌신의 그림자랍니다."
            ),
            "ESTP 사업가형": (
                f"ESTP에게 '{dream_text[:15]}...'는 '지루한 일상에 대한 반란'. "
                "현실에서 더 큰 모험이 필요하다는 사인이에요."
            ),
        }
        return {
            "interpreter": self.name,
            "title": self.title,
            "option": option,
            "verdict": templates[option],
            "risk_level": random.choice(["LOW", "MEDIUM"]),
            "tag": "PERSONALITY"
        }

class TherapistInterpreter(Interpreter):
    """심리치료사 관점에서 꿈을 부드럽게 가공하는 해석가."""
    def __init__(self):
        super().__init__(
            name="닥터 소피아 림",
            title="국가공인 임상 무의식 치료사",
            options=["인지행동치료(CBT)", "정신역동 치료", "마음챙김 가공", "EMDR 안구재처리"]
        )
        
    def process(self, dream_text: str, option: str) -> dict:
        self.validate_option(option)
        templates = {
            "인지행동치료(CBT)": (
                f"'{dream_text[:15]}...' 이 꿈에서 떠오른 두려움은 '인지 왜곡'일 수 있어요. "
                "현실 검증을 통해 안전한 형태로 재가공했습니다."
            ),
            "정신역동 치료": (
                f"무의식 속에 자리 잡은 '{dream_text[:15]}...'의 정서는 "
                "어린 시절의 미해결 감정과 연결되어 있어요. 따뜻하게 통합해드릴게요."
            ),
            "마음챙김 가공": (
                f"호흡과 함께 '{dream_text[:15]}...'의 이미지를 흘려보내세요. "
                "지금 이 순간, 당신은 안전합니다."
            ),
            "EMDR 안구재처리": (
                f"'{dream_text[:15]}...'의 외상 기억을 좌우 자극으로 재처리합니다. "
                "이제 이 장면은 '단순한 회상'으로 가공되었어요."
            ),
        }
        return {
            "interpreter": self.name,
            "title": self.title,
            "option": option,
            "verdict": templates[option],
            "risk_level": "LOW",
            "tag": "THERAPEUTIC"
        }

# ================================================================
# [SECTION E] 무의식 재판소 (전체 시스템을 관장하는 컨트롤러)
# ================================================================
class DreamCensorshipCourt:
    """플레이어(검열관)가 사용하는 재판소 본부."""
    def __init__(self):
        self.interpreters = {
            "professor": ProfessorInterpreter(),
            "mbti": MBTIInterpreter(),
            "therapist": TherapistInterpreter(),
        }
        self.history = []
        
    def get_interpreter(self, key: str) -> Interpreter:
        key = (key or "").lower().strip()
        if key not in self.interpreters:
            raise InvalidInterpreterError(
                f"'{key}'라는 해석가는 재판소에 등록되어 있지 않습니다. "
                f"등록된 해석가: {list(self.interpreters.keys())}"
            )
        return self.interpreters[key]
        
    def interpret(self, raw_text: str, interpreter_key: str, option: str) -> dict:
        dream = Dream(raw_text) # __len__ + UnprocessableDreamError 트리거 지점
        interpreter = self.get_interpreter(interpreter_key)
        
        # __call__ 매직메소드 활용 → 다형성(process) 호출
        result = interpreter(dream.raw_text, option)
        
        # 결과 메타데이터 추가
        result.update({
            "dream_meta": {
                "citizen_id": dream.citizen_id,
                "length": len(dream), # __len__ 사용
                "timestamp": dream.timestamp,
                "summary": str(dream), # __str__ 사용
            }
        })
        self.history.append(result)
        return result
        
    def __len__(self):
        """매직메소드: 재판소에 누적된 처리 건수."""
        return len(self.history)
        
    def __str__(self):
        return f"무의식 재판소 | 등록 해석가 {len(self.interpreters)}명 | 누적 처리 {len(self)}건"

# 전역 재판소 인스턴스
COURT = DreamCensorshipCourt()

# ================================================================
# [SECTION F] Flask API 엔드포인트
# ================================================================
@app.errorhandler(DreamInjectorError)
def handle_dream_error(e: DreamInjectorError):
    return jsonify(e.to_dict()), e.status_code

@app.route("/api/interpreters", methods=["GET"])
def list_interpreters():
    """등록된 3명의 해석가 및 각자의 4가지 가공옵션 목록 반환."""
    data = []
    for key, itp in COURT.interpreters.items():
        data.append({
            "key": key,
            "name": itp.name,
            "title": itp.title,
            "options": itp.options,
            "display": str(itp), # __str__
        })
    return jsonify({"interpreters": data, "court": str(COURT)})

@app.route("/api/interpret", methods=["POST"])
def interpret_dream():
    """
    꿈을 해석/가공하는 메인 엔드포인트.
    body: { "dream": "...", "interpreter": "professor|mbti|therapist", "option": "..." }
    """
    body = request.get_json(silent=True) or {}
    dream_text = body.get("dream", "")
    interpreter_key = body.get("interpreter", "")
    option = body.get("option", "")
    
    if not interpreter_key:
        raise InvalidInterpreterError("해석가를 선택해 주세요.")
    if not option:
        raise InvalidOptionError("가공 방식을 선택해 주세요.")
        
    result = COURT.interpret(dream_text, interpreter_key, option)
    return jsonify({"ok": True, "result": result})

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "court": str(COURT), "processed": len(COURT)})

@app.route("/", methods=["GET"])
def index():
    """Vercel 환경에서 정적 index.html 서빙."""
    public_dir = os.path.join(os.path.dirname(__file__), "..", "public")
    return send_from_directory(public_dir, "index.html")

# ================================================================
# [SECTION G] 로컬 실행 진입점
# ================================================================
if __name__ == "__main__":
    print(COURT)
    for k, itp in COURT.interpreters.items():
        print(" -", itp)
    app.run(host="0.0.0.0", port=5000, debug=True)
