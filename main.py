# -*- coding: utf-8 -*-
"""
================================================================
 무의식 재판소 - 드림 인젝터 (Dream Injector)
 Streamlit 배포용 단일 파일 버전
----------------------------------------------------------------
 [OOP 핵심 요구사항 체크리스트]
  1) 클래스 3개 이상: Interpreter 부모 + 3개 자식 + Dream + DreamCensorshipCourt
  2) 다형성: process(dream_text, option) 오버라이딩
  3) 매직 메소드: __str__, __len__, __repr__, __call__
  4) 사용자 정의 예외: UnprocessableDreamError, InvalidInterpreterError, InvalidOptionError

 실행:
  streamlit run streamlit_app.py

 Streamlit Cloud:
  - 이 파일을 app.py 또는 streamlit_app.py로 업로드
  - requirements.txt에 streamlit만 작성
================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import random
from typing import Dict, List, Optional

import streamlit as st


# ================================================================
# [SECTION A] 사용자 정의 예외
# ================================================================
class DreamInjectorError(Exception):
    """드림 인젝터 시스템 최상위 예외 클래스."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def to_dict(self) -> dict:
        return {
            "error": self.__class__.__name__,
            "message": self.message,
        }


class UnprocessableDreamError(DreamInjectorError):
    """꿈 텍스트가 너무 짧거나 처리 불가능할 때 발생."""


class InvalidInterpreterError(DreamInjectorError):
    """존재하지 않는 해석가를 선택했을 때 발생."""


class InvalidOptionError(DreamInjectorError):
    """해석가의 가공 옵션이 유효하지 않을 때 발생."""


# ================================================================
# [SECTION B] Dream 데이터 클래스
# ================================================================
class Dream:
    """시민의 원시 꿈 데이터(Raw Dream)를 표현하는 클래스."""

    MIN_LENGTH = 10
    MAX_LENGTH = 1000

    def __init__(self, raw_text: str, citizen_id: Optional[str] = None):
        if not isinstance(raw_text, str):
            raise UnprocessableDreamError("꿈 데이터는 텍스트 형식이어야 합니다.")

        cleaned = raw_text.strip()

        if len(cleaned) < self.MIN_LENGTH:
            raise UnprocessableDreamError(
                f"무의식 단편이 너무 짧습니다. 최소 {self.MIN_LENGTH}자 이상의 꿈 조각이 필요합니다. "
                f"(현재 {len(cleaned)}자)"
            )

        if len(cleaned) > self.MAX_LENGTH:
            raise UnprocessableDreamError(
                f"꿈 데이터가 너무 깁니다. 최대 {self.MAX_LENGTH}자까지만 입력할 수 있습니다. "
                f"(현재 {len(cleaned)}자)"
            )

        self.raw_text = cleaned
        self.citizen_id = citizen_id or self._generate_citizen_id(cleaned)
        self.timestamp = datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _generate_citizen_id(text: str) -> str:
        hashed = hashlib.sha256(text.encode("utf-8")).hexdigest()[:8].upper()
        return f"CITIZEN-{hashed}"

    def __len__(self) -> int:
        """매직 메소드 ①: len(dream)으로 꿈 텍스트 길이를 반환."""
        return len(self.raw_text)

    def __str__(self) -> str:
        """매직 메소드 ②: 사용자 친화적 문자열 표현."""
        preview = self.raw_text[:30] + ("..." if len(self.raw_text) > 30 else "")
        return f"[{self.citizen_id}] 원시 꿈({len(self)}자): {preview}"

    def __repr__(self) -> str:
        """매직 메소드 ③: 디버깅용 정식 표현."""
        return f"Dream(citizen_id={self.citizen_id!r}, length={len(self)})"


# ================================================================
# [SECTION C] Interpreter 부모 클래스
# ================================================================
class Interpreter(ABC):
    """모든 꿈 해석가가 상속해야 하는 추상 부모 클래스."""

    def __init__(self, name: str, title: str, options: List[str]):
        self.name = name
        self.title = title
        self.options = options

    @abstractmethod
    def process(self, dream_text: str, option: str) -> dict:
        """다형성의 핵심: 자식 클래스에서 각자 다른 방식으로 오버라이딩."""
        raise NotImplementedError

    def validate_option(self, option: str) -> None:
        if option not in self.options:
            raise InvalidOptionError(
                f"'{self.name}' 해석가는 '{option}' 가공 방식을 모릅니다. "
                f"사용 가능: {', '.join(self.options)}"
            )

    def _base_result(self, option: str, verdict: str, risk_level: str, tag: str) -> dict:
        """자식 클래스들의 공통 반환 구조를 통일."""
        return {
            "interpreter": self.name,
            "title": self.title,
            "option": option,
            "verdict": verdict,
            "risk_level": risk_level,
            "tag": tag,
        }

    def __str__(self) -> str:
        return f"해석가 [{self.name}] - {self.title} | 가공방식: {', '.join(self.options)}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"

    def __call__(self, dream_text: str, option: str) -> dict:
        """매직 메소드 ④: interpreter(dream_text, option) 형태로 호출 가능."""
        return self.process(dream_text, option)


# ================================================================
# [SECTION D] 3명의 자식 해석가
# ================================================================
class ProfessorInterpreter(Interpreter):
    """학술적·논리적 관점에서 꿈을 해석하는 교수형 해석가."""

    def __init__(self):
        super().__init__(
            name="프로페서 K. 융그",
            title="국립 무의식 연구소 명예교수",
            options=["프로이트식 분석", "융의 원형 해석", "라캉식 기호해석", "구조주의 분해"],
        )

    def process(self, dream_text: str, option: str) -> dict:
        self.validate_option(option)
        templates = {
            "프로이트식 분석": (
                f"'{dream_text[:20]}...' 이 꿈은 억압된 욕망이 상징적 이미지로 치환된 결과입니다. "
                "유년기의 미해결 갈등이 표면으로 올라온 것으로 해석됩니다."
            ),
            "융의 원형 해석": (
                f"'{dream_text[:15]}...' 장면에는 그림자(Shadow) 원형이 강하게 드러납니다. "
                "집단무의식 깊은 곳의 자기실현 충동이 반영된 꿈입니다."
            ),
            "라캉식 기호해석": (
                f"'{dream_text[:15]}...' 구조는 기표와 기의의 어긋남을 보여줍니다. "
                "이 꿈은 실재계의 균열이 언어적 상징으로 드러난 사례입니다."
            ),
            "구조주의 분해": (
                "꿈을 이항대립으로 분해하면 [상승/하강], [추격자/피추격자], [검열/욕망]의 구조가 보입니다. "
                "이는 사회적 권력 구조가 내면화된 결과로 해석됩니다."
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

    def __init__(self):
        super().__init__(
            name="MBTI 큐레이터 미나",
            title="시민 성격유형 적합도 분석관",
            options=["INTJ 전략형", "ENFP 활동가형", "ISFJ 수호자형", "ESTP 사업가형"],
        )

    def process(self, dream_text: str, option: str) -> dict:
        self.validate_option(option)
        templates = {
            "INTJ 전략형": (
                f"'{dream_text[:15]}...'는 미완성된 계획과 통제 욕구를 상징합니다. "
                "전략적 좌절감이 무의식에 누적된 신호일 수 있습니다."
            ),
            "ENFP 활동가형": (
                f"'{dream_text[:15]}...'는 새로운 가능성의 문을 여는 이미지입니다. "
                "직관과 호기심이 확장되기 직전의 상태로 해석됩니다."
            ),
            "ISFJ 수호자형": (
                f"'{dream_text[:15]}...'는 소중한 사람을 지키고 싶은 마음의 표현입니다. "
                "헌신과 불안이 함께 드러난 꿈입니다."
            ),
            "ESTP 사업가형": (
                f"'{dream_text[:15]}...'는 지루한 일상에 대한 반란을 의미합니다. "
                "현실에서 더 직접적인 자극과 모험을 원하고 있을 수 있습니다."
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

    def __init__(self):
        super().__init__(
            name="닥터 소피아 림",
            title="국가공인 임상 무의식 치료사",
            options=["인지행동치료(CBT)", "정신역동 치료", "마음챙김 가공", "EMDR 안구재처리"],
        )

    def process(self, dream_text: str, option: str) -> dict:
        self.validate_option(option)
        templates = {
            "인지행동치료(CBT)": (
                f"'{dream_text[:15]}...'에서 느껴지는 두려움은 인지 왜곡의 형태일 수 있습니다. "
                "현실 검증을 통해 안전한 의미로 재구성했습니다."
            ),
            "정신역동 치료": (
                f"'{dream_text[:15]}...'의 정서는 과거의 미해결 감정과 연결되어 있을 수 있습니다. "
                "이 감정을 천천히 통합하는 과정이 필요합니다."
            ),
            "마음챙김 가공": (
                f"'{dream_text[:15]}...'의 이미지를 억누르지 말고 흘려보내세요. "
                "지금 이 순간의 감각으로 돌아오면 꿈의 압박감은 약해집니다."
            ),
            "EMDR 안구재처리": (
                f"'{dream_text[:15]}...' 장면을 안전한 거리에서 바라보며 재처리합니다. "
                "이제 이 이미지는 위협이 아니라 단순한 기억 조각으로 정리됩니다."
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

    def __init__(self):
        self.interpreters: Dict[str, Interpreter] = {
            "professor": ProfessorInterpreter(),
            "mbti": MBTIInterpreter(),
            "therapist": TherapistInterpreter(),
        }
        self.history: List[dict] = []

    def get_interpreter(self, key: str) -> Interpreter:
        normalized_key = (key or "").lower().strip()
        if normalized_key not in self.interpreters:
            raise InvalidInterpreterError(
                f"'{key}'라는 해석가는 재판소에 등록되어 있지 않습니다. "
                f"등록된 해석가: {', '.join(self.interpreters.keys())}"
            )
        return self.interpreters[normalized_key]

    def interpret(self, raw_text: str, interpreter_key: str, option: str) -> dict:
        dream = Dream(raw_text)
        interpreter = self.get_interpreter(interpreter_key)

        result = interpreter(dream.raw_text, option)
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

    def reset_history(self) -> None:
        self.history.clear()

    def __len__(self) -> int:
        """매직 메소드: 재판소에 누적된 처리 건수."""
        return len(self.history)

    def __str__(self) -> str:
        return f"무의식 재판소 | 등록 해석가 {len(self.interpreters)}명 | 누적 처리 {len(self)}건"


# ================================================================
# [SECTION F] Streamlit UI
# ================================================================
def get_court() -> DreamCensorshipCourt:
    """Streamlit rerun에도 history가 유지되도록 session_state 사용."""
    if "court" not in st.session_state:
        st.session_state.court = DreamCensorshipCourt()
    return st.session_state.court


def render_sidebar(court: DreamCensorshipCourt) -> None:
    st.sidebar.title("무의식 재판소")
    st.sidebar.caption(str(court))
    st.sidebar.divider()

    st.sidebar.subheader("OOP 체크리스트")
    st.sidebar.markdown(
        """
        - 추상 부모 클래스: `Interpreter`
        - 자식 클래스 3개
        - 다형성: `process()` 오버라이딩
        - 매직 메소드 4개 이상
        - 사용자 정의 예외 3개
        """
    )

    if st.sidebar.button("처리 기록 초기화"):
        court.reset_history()
        st.sidebar.success("기록이 초기화되었습니다.")
        st.rerun()


def render_history(court: DreamCensorshipCourt) -> None:
    with st.expander(f"처리 기록 보기 ({len(court)}건)", expanded=False):
        if not court.history:
            st.info("아직 처리된 꿈이 없습니다.")
            return

        for idx, item in enumerate(reversed(court.history), start=1):
            st.markdown(f"**#{idx} | {item['interpreter']} | {item['option']}**")
            st.write(item["verdict"])
            st.caption(
                f"위험도: {item['risk_level']} | 태그: {item['tag']} | "
                f"시민 ID: {item['dream_meta']['citizen_id']}"
            )
            st.divider()


def main() -> None:
    st.set_page_config(
        page_title="무의식 재판소 - Dream Injector",
        page_icon="🧠",
        layout="centered",
    )

    court = get_court()
    render_sidebar(court)

    st.title("🧠 무의식 재판소")
    st.caption("꿈을 입력하면 해석가가 무의식을 재가공합니다.")

    dream_text = st.text_area(
        "원시 꿈 데이터 입력",
        placeholder="예: 어두운 복도를 걷고 있는데 문 너머에서 누군가 나를 부르는 꿈을 꾸었다...",
        height=160,
        max_chars=Dream.MAX_LENGTH,
    )

    interpreter_labels = {
        "professor": "프로페서 K. 융그 - 학술 분석",
        "mbti": "MBTI 큐레이터 미나 - 성격유형 분석",
        "therapist": "닥터 소피아 림 - 심리치료 분석",
    }

    interpreter_key = st.selectbox(
        "해석가 선택",
        options=list(court.interpreters.keys()),
        format_func=lambda key: interpreter_labels[key],
    )

    selected_interpreter = court.get_interpreter(interpreter_key)
    option = st.selectbox("가공 방식 선택", options=selected_interpreter.options)

    submitted = st.button("꿈 해석하기", type="primary", use_container_width=True)

    if submitted:
        try:
            result = court.interpret(dream_text, interpreter_key, option)

            st.success("무의식 재판이 완료되었습니다.")
            st.subheader("판결문")
            st.markdown(f"### {result['interpreter']}")
            st.caption(f"{result['title']} · {result['option']}")
            st.write(result["verdict"])

            col1, col2, col3 = st.columns(3)
            col1.metric("위험도", result["risk_level"])
            col2.metric("태그", result["tag"])
            col3.metric("꿈 길이", f"{result['dream_meta']['length']}자")

            with st.expander("꿈 메타데이터"):
                st.json(result["dream_meta"])

        except DreamInjectorError as error:
            st.error(error.message)
        except Exception as error:
            st.error("예상하지 못한 오류가 발생했습니다.")
            st.exception(error)

    render_history(court)


if __name__ == "__main__":
    main()
