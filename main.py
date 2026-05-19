# -*- coding: utf-8 -*-
"""
================================================================
 무의식 재판소 - 드림 인젝터 (Dream Injector)
 Streamlit 배포용 단일 파일 버전
----------------------------------------------------------------
 [OOP 핵심 요구사항 체크리스트]
  1) 클래스 3개 이상: Interpreter 부모 + 3개 자식 + Dream + DreamInjectionCourt
  2) 다형성: process(dream_text, injection_text) 오버라이딩
  3) 매직 메소드: __str__, __len__, __repr__, __call__
  4) 사용자 정의 예외: UnprocessableDreamError, InvalidInterpreterError, InvalidInjectionTextError

 실행:
  streamlit run streamlit_app.py

 Streamlit Cloud:
  - 이 파일을 streamlit_app.py로 업로드
  - requirements.txt에 streamlit만 작성
================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import hashlib
import random
import re
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


class InvalidInjectionTextError(DreamInjectorError):
    """주입 텍스트가 비어 있거나 유효하지 않을 때 발생."""


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
        return f"[{self.citizen_id}] 원시 꿈: {preview}"

    def __repr__(self) -> str:
        """매직 메소드 ③: 디버깅용 정식 표현."""
        return f"Dream(citizen_id={self.citizen_id!r}, length={len(self)})"


# ================================================================
# [SECTION C] Interpreter 부모 클래스
# ================================================================
class Interpreter(ABC):
    """모든 꿈 해석가가 상속해야 하는 추상 부모 클래스."""

    def __init__(self, name: str, title: str, perspective: str):
        self.name = name
        self.title = title
        self.perspective = perspective

    @abstractmethod
    def process(self, dream_text: str, injection_text: str) -> dict:
        """
        다형성의 핵심.
        같은 꿈과 주입 텍스트를 받더라도 해석가마다 다른 방식으로 판별한다.
        """
        raise NotImplementedError

    def _extract_keywords(self, text: str) -> List[str]:
        """꿈 텍스트와 주입 텍스트에서 핵심 키워드를 간단히 추출."""
        words = re.findall(r"[가-힣A-Za-z0-9]{2,}", text)
        stopwords = {
            "그리고", "그래서", "하지만", "나는", "내가", "꿈에서",
            "있었다", "같았다", "너무", "계속", "무언가", "누군가",
        }

        keywords = []
        for word in words:
            if word not in stopwords and word not in keywords:
                keywords.append(word)

        return keywords[:6] if keywords else ["불안", "기억", "욕망"]

    def _risk_level(self, dream_text: str, injection_text: str) -> str:
        """부정 키워드와 강한 감정 표현을 기준으로 위험도를 산정."""
        target_text = f"{dream_text} {injection_text}"

        high_words = [
            "죽음", "살해", "피", "추락", "감금", "도망", "공포",
            "악몽", "절망", "폭발", "위협", "사라짐",
        ]
        medium_words = [
            "불안", "울음", "상실", "혼란", "어둠", "실패",
            "고립", "압박", "쫓김", "갈등",
        ]

        high_score = sum(word in target_text for word in high_words)
        medium_score = sum(word in target_text for word in medium_words)

        if high_score >= 1 or medium_score >= 3:
            return "HIGH"
        if medium_score >= 1:
            return "MEDIUM"
        return "LOW"

    def _base_result(
        self,
        keywords: List[str],
        positive_view: str,
        negative_view: str,
        risk_level: str,
        injected_sentence: str,
    ) -> dict:
        return {
            "interpreter": self.name,
            "title": self.title,
            "keywords": keywords,
            "positive_view": positive_view,
            "negative_view": negative_view,
            "risk_level": risk_level,
            "injected_sentence": injected_sentence,
        }

    def __str__(self) -> str:
        return f"해석가 [{self.name}] - {self.title} | 관점: {self.perspective}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"

    def __call__(self, dream_text: str, injection_text: str) -> dict:
        """매직 메소드 ④: interpreter(dream_text, injection_text) 형태로 호출 가능."""
        return self.process(dream_text, injection_text)


# ================================================================
# [SECTION D] 3명의 자식 해석가
# ================================================================
class LeeDongHyunInterpreter(Interpreter):
    """이동현 교수님 관점의 꿈 해석가."""

    def __init__(self):
        super().__init__(
            name="이동현 교수님",
            title="무의식 서사 분석 담당 교수",
            perspective="키워드 중심의 긍정/부정 양면 판별",
        )

    def process(self, dream_text: str, injection_text: str) -> dict:
        keywords = self._extract_keywords(f"{dream_text} {injection_text}")
        risk_level = self._risk_level(dream_text, injection_text)

        positive = (
            f"핵심 키워드 {', '.join(keywords[:3])}는 단순한 불안의 흔적이 아니라, "
            "사용자가 현재 상황을 해석하고 다시 통제하려는 시도로 볼 수 있습니다. "
            "주입 텍스트는 꿈의 흐름에 새로운 의미를 부여해 감정의 방향을 바꾸는 장치로 작동합니다."
        )
        negative = (
            f"반대로 {', '.join(keywords[:3])}는 억눌린 긴장이나 회피하고 싶은 문제를 드러낼 수 있습니다. "
            "주입 텍스트가 지나치게 강하면 원래 꿈의 감정을 덮어버려 부자연스러운 왜곡이 생길 수 있습니다."
        )
        injected = (
            f"주입 문장: {injection_text.strip()} "
            "이 문장은 꿈속 장면에 삽입되어 사용자의 무의식적 판단을 재구성합니다."
        )

        return self._base_result(keywords, positive, negative, risk_level, injected)


class MBTIInterpreter(Interpreter):
    """성격유형 관점에서 꿈을 해석하는 해석가."""

    def __init__(self):
        super().__init__(
            name="MBTI 큐레이터 미나",
            title="시민 성격유형 적합도 분석관",
            perspective="성향 기반의 긍정/부정 양면 판별",
        )

    def process(self, dream_text: str, injection_text: str) -> dict:
        keywords = self._extract_keywords(f"{dream_text} {injection_text}")
        risk_level = self._risk_level(dream_text, injection_text)

        positive = (
            f"{', '.join(keywords[:3])} 키워드는 사용자의 성향과 욕구가 선명해지는 지점입니다. "
            "주입 텍스트는 선택, 가능성, 관계 회복 같은 긍정적 방향으로 꿈의 해석을 유도할 수 있습니다."
        )
        negative = (
            "다만 성향 중심 해석은 꿈을 지나치게 유형화할 위험이 있습니다. "
            f"{', '.join(keywords[:3])}를 고정된 성격의 증거로 단정하면 꿈의 복합적인 감정을 놓칠 수 있습니다."
        )
        injected = (
            f"주입 문장: {injection_text.strip()} "
            "이 문장은 꿈속 선택지를 확장하는 심리적 신호로 삽입됩니다."
        )

        return self._base_result(keywords, positive, negative, risk_level, injected)


class TherapistInterpreter(Interpreter):
    """심리치료사 관점에서 꿈을 부드럽게 해석하는 해석가."""

    def __init__(self):
        super().__init__(
            name="닥터 소피아 림",
            title="국가공인 임상 무의식 치료사",
            perspective="정서 안정 중심의 긍정/부정 양면 판별",
        )

    def process(self, dream_text: str, injection_text: str) -> dict:
        keywords = self._extract_keywords(f"{dream_text} {injection_text}")
        risk_level = self._risk_level(dream_text, injection_text)

        positive = (
            f"{', '.join(keywords[:3])}는 마음이 보내는 신호로 볼 수 있습니다. "
            "주입 텍스트는 불안을 억누르기보다 안전한 의미로 다시 바라보게 만드는 완충 장치가 됩니다."
        )
        negative = (
            "그러나 주입 텍스트가 감정을 너무 빠르게 안정시키는 방향으로만 작동하면, "
            "사용자가 실제로 느낀 불안이나 상실감을 충분히 마주하지 못할 수 있습니다."
        )
        injected = (
            f"주입 문장: {injection_text.strip()} "
            "이 문장은 꿈의 정서를 완화하고 안전한 해석으로 연결하는 문장으로 삽입됩니다."
        )

        return self._base_result(keywords, positive, negative, risk_level, injected)


# ================================================================
# [SECTION E] 무의식 주입소 컨트롤러
# ================================================================
class DreamInjectionCourt:
    """플레이어가 사용하는 꿈 주입 시스템 본부."""

    def __init__(self):
        self.interpreters: Dict[str, Interpreter] = {
            "lee": LeeDongHyunInterpreter(),
            "mbti": MBTIInterpreter(),
            "therapist": TherapistInterpreter(),
        }
        self.history: List[dict] = []

    def get_interpreter(self, key: str) -> Interpreter:
        normalized_key = (key or "").lower().strip()
        if normalized_key not in self.interpreters:
            raise InvalidInterpreterError(
                f"'{key}'라는 해석가는 등록되어 있지 않습니다. "
                f"등록된 해석가: {', '.join(self.interpreters.keys())}"
            )
        return self.interpreters[normalized_key]

    def validate_injection_text(self, injection_text: str) -> str:
        cleaned = (injection_text or "").strip()
        if len(cleaned) < 2:
            raise InvalidInjectionTextError("주입할 텍스트를 2자 이상 입력해 주세요.")
        if len(cleaned) > 300:
            raise InvalidInjectionTextError("주입 텍스트는 최대 300자까지만 입력할 수 있습니다.")
        return cleaned

    def inject(self, raw_text: str, interpreter_key: str, injection_text: str) -> dict:
        dream = Dream(raw_text)
        cleaned_injection = self.validate_injection_text(injection_text)
        interpreter = self.get_interpreter(interpreter_key)

        result = interpreter(dream.raw_text, cleaned_injection)
        result.update(
            {
                "dream_meta": {
                    "citizen_id": dream.citizen_id,
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
        """매직 메소드: 주입소에 누적된 처리 건수."""
        return len(self.history)

    def __str__(self) -> str:
        return f"무의식 주입소 | 등록 해석가 {len(self.interpreters)}명 | 누적 주입 {len(self)}건"


# ================================================================
# [SECTION F] Streamlit UI
# ================================================================
def get_court() -> DreamInjectionCourt:
    """Streamlit rerun에도 history가 유지되도록 session_state 사용."""
    if "court" not in st.session_state:
        st.session_state.court = DreamInjectionCourt()
    return st.session_state.court


def render_sidebar(court: DreamInjectionCourt) -> None:
    st.sidebar.title("무의식 주입소")
    st.sidebar.caption(str(court))
    st.sidebar.divider()

    st.sidebar.subheader("OOP 체크리스트")
    st.sidebar.markdown(
        """
        - 추상 부모 클래스: `Interpreter`
        - 자식 클래스 3개
        - 다형성: `process()` 오버라이딩
        - 매직 메소드: `__str__`, `__len__`, `__repr__`, `__call__`
        - 사용자 정의 예외 3개
        """
    )

    if st.sidebar.button("주입 기록 초기화"):
        court.reset_history()
        st.sidebar.success("기록이 초기화되었습니다.")
        st.rerun()


def render_history(court: DreamInjectionCourt) -> None:
    with st.expander(f"주입 기록 보기 ({len(court)}건)", expanded=False):
        if not court.history:
            st.info("아직 주입된 꿈이 없습니다.")
            return

        for idx, item in enumerate(reversed(court.history), start=1):
            st.markdown(f"**#{idx} | {item['interpreter']}**")
            st.write(item["injected_sentence"])
            st.caption(f"위험도: {item['risk_level']} | 시민 ID: {item['dream_meta']['citizen_id']}")
            st.divider()


def main() -> None:
    st.set_page_config(
        page_title="무의식 주입소 - Dream Injector",
        page_icon="🧠",
        layout="centered",
    )

    court = get_court()
    render_sidebar(court)

    st.title("🧠 무의식 주입소")
    st.caption("꿈을 입력하고, 해석가를 선택한 뒤, 직접 주입할 텍스트를 넣어 무의식을 재구성합니다.")

    dream_text = st.text_area(
        "원시 꿈 데이터 입력",
        placeholder="예: 어두운 복도를 걷고 있는데 문 너머에서 누군가 나를 부르는 꿈을 꾸었다...",
        height=150,
        max_chars=Dream.MAX_LENGTH,
    )

    interpreter_labels = {
        "lee": "이동현 교수님",
        "mbti": "MBTI 큐레이터 미나",
        "therapist": "닥터 소피아 림",
    }

    interpreter_key = st.selectbox(
        "해석가 선택",
        options=list(court.interpreters.keys()),
        format_func=lambda key: interpreter_labels[key],
    )

    injection_text = st.text_area(
        "직접 주입할 텍스트 입력",
        placeholder="예: 이 장면은 실패가 아니라 새로운 선택을 시작하는 신호다.",
        height=100,
        max_chars=300,
    )

    submitted = st.button("꿈 주입하기", type="primary", use_container_width=True)

    if submitted:
        try:
            result = court.inject(dream_text, interpreter_key, injection_text)

            st.success("주입이 완료되었습니다.")
            st.subheader("주입 결과")

            st.markdown(f"### {result['interpreter']}")
            st.caption(result["title"])

            st.markdown("#### 판별 키워드")
            st.write(", ".join(result["keywords"]))

            st.markdown("#### 긍정 측면")
            st.write(result["positive_view"])

            st.markdown("#### 부정 측면")
            st.write(result["negative_view"])

            st.metric("위험도", result["risk_level"])

            st.markdown("#### 주입된 텍스트")
            st.write(result["injected_sentence"])

        except DreamInjectorError as error:
            st.error(error.message)
        except Exception as error:
            st.error("예상하지 못한 오류가 발생했습니다.")
            st.exception(error)

    render_history(court)


if __name__ == "__main__":
    main()
