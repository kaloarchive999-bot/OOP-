"""
OOP-
꿈 해석 거래소: Dream Decoder Marketplace
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
당신의 무의식을 거래하세요. 예산에 맞는 최고의 해석사를 매칭해 드립니다.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Author: 재민
"""

from abc import ABC, abstractmethod

try:
    import streamlit as st
except ModuleNotFoundError:
    st = None


# ==================== CUSTOM EXCEPTIONS ====================


class DreamException(Exception):
    """꿈 거래소의 기본 예외 클래스"""


class UninterpretableDreamError(DreamException):
    """해석 불가능한 헛소리 꿈 입력"""


class InvalidMBTIError(DreamException):
    """MBTI 분기 선택 시 잘못된 입력"""


class InsufficientFundsError(DreamException):
    """예산 부족으로 모델 호출 불가"""


# ==================== DATA CLASSES ====================


class Dream:
    """사용자의 꿈 데이터를 담는 객체"""

    def __init__(self, content: str):
        self.content = content.strip()

        if len(self.content) < 10:
            raise UninterpretableDreamError(
                "분석할 데이터가 부족합니다. 최소 10글자 이상의 꿈을 입력해주세요."
            )

        self.keywords = self._extract_keywords()
        self.emotion_tag = self._detect_emotion()

    def _extract_keywords(self):
        """꿈 내용에서 주요 키워드 추출"""
        stop_words = {
            "이",
            "그",
            "저",
            "그것",
            "게",
            "것",
            "는",
            "다",
            "나",
            "가",
            "를",
            "으로",
            "로",
        }
        words = [
            word.strip(".,!?~…")
            for word in self.content.split()
            if len(word.strip(".,!?~…")) > 1 and word.strip(".,!?~…") not in stop_words
        ]
        return words[:5]

    def _detect_emotion(self):
        """꿈에서 감정 태그 감지"""
        negative_words = ["죽", "쫓", "빠", "떨어", "무서", "절망", "슬픔", "외로", "불안"]
        positive_words = ["즐거", "행복", "설렘", "희망", "성공", "기쁨"]

        if any(word in self.content for word in negative_words):
            return "🔴 부정적"
        if any(word in self.content for word in positive_words):
            return "🟢 긍정적"
        return "🟡 중립적"

    def __len__(self):
        """꿈 텍스트의 길이"""
        return len(self.content)

    def __str__(self):
        """꿈을 예쁜 일기 포맷으로 출력"""
        keywords = ", ".join(self.keywords) if self.keywords else "(없음)"
        return (
            "\n🌙 [꿈 일기]\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"내용: {self.content}\n"
            f"감정: {self.emotion_tag}\n"
            f"주요 키워드: {keywords}\n"
            f"글자 수: {len(self.content)}자\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )


class Interpreter(ABC):
    """모든 해석가의 부모 클래스"""

    def __init__(self, name: str, price: int):
        self.name = name
        self.price = price
        self.reputation = 100

    def __le__(self, budget: int):
        """사용자의 예산으로 고용 가능한가?"""
        return self.price <= budget

    def __lt__(self, other):
        """평판순 정렬 시 사용"""
        return self.reputation > other.reputation

    def __str__(self):
        """해석가 정보 출력"""
        return f"{self.name} ({self.price}원) | 평판: ⭐ {self.reputation}"

    @abstractmethod
    def interpret(self, dream: Dream, **kwargs) -> str:
        """꿈을 해석하는 추상 메서드"""


# ==================== CONCRETE INTERPRETERS ====================


class MBTIInterpreter(Interpreter):
    """
    일반 모델: MBTI 기반 꿈 해석 (500원)
    S/N → T/F 순차 선택으로 4가지 결과 제공
    """

    def __init__(self):
        super().__init__("MBTI 일반 해석사", 500)

    def interpret(self, dream: Dream, **kwargs) -> str:
        """MBTI 분기를 통한 해석"""
        choice_sn = kwargs.get("choice_sn", "").strip().upper()
        choice_tf = kwargs.get("choice_tf", "").strip().upper()

        if choice_sn not in ["S", "N"]:
            raise InvalidMBTIError("S 또는 N만 선택해주세요.")
        if choice_tf not in ["T", "F"]:
            raise InvalidMBTIError("T 또는 F만 선택해주세요.")

        mbti_type = choice_sn + choice_tf
        interpretations = {
            "ST": (
                "당신의 유형: [ST - 현실 논리형]\n\n"
                "📊 해석:\n"
                "이 꿈은 최근 겪은 현실의 스트레스나 일상 속 문제가\n"
                "뇌의 논리적 처리 메커니즘에 의해 재구성된 결과입니다.\n"
                "당신은 꿈속에서도 'WHY'를 찾으려 했던 거네요.\n\n"
                "💡 조언: 현실의 문제를 직시하고 단계별로 해결해 나가세요."
            ),
            "SF": (
                "당신의 유형: [SF - 현실 감정형]\n\n"
                "❤️ 해석:\n"
                "현실에서 느낀 인간관계의 피로감, 서운함, 따뜻함이\n"
                "무의식중에 감정적으로 발현된 꿈입니다.\n"
                "당신의 감정 센서가 매우 민감하다는 증거입니다.\n\n"
                "💡 조언: 사람들과의 관계를 되짚어보고 감정을 표현하세요."
            ),
            "NT": (
                "당신의 유형: [NT - 직관 논리형]\n\n"
                "🧠 해석:\n"
                "당신의 뇌가 아직 일어나지 않은 미래의 복잡한 변수들을\n"
                "고차원적으로 시뮬레이션하고 있습니다.\n"
                "당신은 자신도 모르게 앞날을 예측하려는 존재군요.\n\n"
                "💡 조언: 논리적 사고를 바탕으로 미래를 계획하세요."
            ),
            "NF": (
                "당신의 유형: [NF - 직관 감정형]\n\n"
                "✨ 해석:\n"
                "내면 깊은 곳의 이상적인 자아가 현실의 억압을 뚫고\n"
                "감정적인 해소와 표현을 간절히 요구하고 있습니다.\n"
                "당신은 꿈꾸는 성향의 예술가 기질을 가진 사람이네요.\n\n"
                "💡 조언: 창의성을 발휘하고 진정한 감정을 표현하세요."
            ),
        }

        return interpretations[mbti_type]


class ProfessorInterpreter(Interpreter):
    """
    고급 모델: 교수님 학과 전공 지식 기반 해석 (1000원)
    Social Science & AI 관점에서 고급 분석 제공
    """

    def __init__(self):
        super().__init__("🎓 사회과학&AI 교수님", 1000)

    def interpret(self, dream: Dream, **kwargs) -> str:
        """전공 지식 기반 고급 해석"""
        dream_len = len(dream)
        keyword_count = len(dream.keywords)

        if dream_len > 100 and keyword_count >= 3:
            analysis_level = "심화"
        elif dream_len >= 50:
            analysis_level = "중급"
        else:
            analysis_level = "기초"

        if "부정" in dream.emotion_tag:
            social_analysis = (
                "📍 PESTEL 분석 관점:\n"
                "  - Social: 현대 사회의 구조적 불안감\n"
                "  - Political: 통제와 억압에 대한 무의식적 저항\n"
                "  - Economic: 자본주의 시대의 경쟁 스트레스"
            )
        else:
            social_analysis = (
                "📍 PESTEL 분석 관점:\n"
                "  - Social: 인간관계와 소속감의 욕구\n"
                "  - Technological: 미래 가능성에 대한 기대감\n"
                "  - Economic: 성장과 성공에 대한 동기"
            )

        keywords = ", ".join(dream.keywords) if dream.keywords else "(시스템 추출 중)"
        return (
            f"🎓 [사회과학&AI 교수님의 {analysis_level} 분석]\n\n"
            "아, 자네 꿈 말이야... 아주 흥미로운 '데이터'군.\n"
            "Social Science 렌즈로 분석해 보니 말이지.\n\n"
            f"{social_analysis}\n\n"
            "🔬 AI 모델링 제안:\n"
            "  → 이 꿈을 NLP와 감정 분석 알고리즘으로 벡터화하면\n"
            "     현대인의 심리 패턴을 파악할 수 있겠네.\n"
            f"  → 키워드: {keywords}\n\n"
            "📋 과제: 다음 주까지 이 꿈을 기반으로\n"
            "        AI 감정 분석 레포트를 제출하게!\n\n"
            "다시 한 번 말이야, 자네 무의식은\n"
            "현대 사회의 구조를 정확히 반영한 훌륭한 데이터야.\n"
            "이 지점이 바로 우리 학과의 가치 있는 연구 주제지!"
        )


# ==================== MARKETPLACE SYSTEM ====================


class Marketplace:
    """
    꿈 거래를 중개하는 플랫폼 시스템
    사용자 예산과 해석가 가격을 비교하여 매칭
    """

    def __init__(self, user_budget: int = 0):
        self.interpreters = [MBTIInterpreter(), ProfessorInterpreter()]
        self.user_budget = 0
        self.transactions = []
        self.set_user_budget(user_budget)

    def set_user_budget(self, budget: int):
        """사용자의 예산 설정"""
        self.user_budget = max(0, int(budget))

    def get_available_interpreters(self) -> list:
        """사용자의 예산으로 고용 가능한 해석가 목록"""
        return [interp for interp in self.interpreters if interp <= self.user_budget]

    def hire_interpreter(self, interpreter_name: str, dream: Dream, **kwargs) -> str:
        """해석가 선택 및 결제 처리"""
        available = self.get_available_interpreters()

        if not available:
            raise InsufficientFundsError("고용 가능한 해석가가 없습니다.")

        selected_interpreter = next(
            (interp for interp in available if interp.name == interpreter_name),
            None,
        )
        if selected_interpreter is None:
            raise ValueError("올바른 해석가를 선택해주세요.")

        self.user_budget -= selected_interpreter.price
        result = selected_interpreter.interpret(dream, **kwargs)

        self.transactions.append(
            {
                "interpreter": selected_interpreter.name,
                "dream": dream.content[:30] + ("..." if len(dream.content) > 30 else ""),
                "cost": selected_interpreter.price,
                "remaining_budget": self.user_budget,
            }
        )

        return result


# ==================== STREAMLIT APP ====================


def init_session_state():
    """Streamlit 재실행 사이에 거래 이력을 유지한다."""
    if st is None:
        raise RuntimeError("Streamlit이 설치되어 있지 않습니다. `python -m pip install streamlit`을 실행해주세요.")

    if "transactions" not in st.session_state:
        st.session_state.transactions = []


def render_interpreter_selector(available):
    """고용 가능한 해석가 선택 UI"""
    options = [interp.name for interp in available]
    labels = {interp.name: f"{interp.name} - {interp.price}원" for interp in available}

    return st.radio(
        "고용할 해석가를 선택하세요:",
        options=options,
        format_func=lambda name: labels[name],
    )


def main():
    """Streamlit용 메인 화면"""
    st.set_page_config(page_title="꿈 해석 거래소", page_icon="🌙")
    init_session_state()

    st.title("🌙 꿈 해석 거래소 (Dream Decoder Marketplace)")
    st.write("당신의 무의식을 거래하세요. 예산에 맞는 최고의 해석사를 매칭해 드립니다.")

    interpret_tab, history_tab = st.tabs(["새 꿈 해석", "거래 이력"])

    with interpret_tab:
        dream_input = st.text_area("어젯밤 꾼 꿈을 입력하세요 (10자 이상):", height=160)
        budget = st.number_input(
            "꿈 해석에 얼마를 지불하시겠습니까? (원):",
            min_value=0,
            step=100,
            value=500,
        )

        marketplace = Marketplace(budget)
        available = marketplace.get_available_interpreters()

        if not available:
            st.warning("예산이 부족합니다. 최소 500원 이상의 예산이 필요합니다.")
            selected_name = None
        else:
            st.subheader("💰 고용 가능한 해석가")
            selected_name = render_interpreter_selector(available)

        mbti_kwargs = {}
        if selected_name == "MBTI 일반 해석사":
            st.subheader("🔮 MBTI 꿈 성향 선택")
            mbti_kwargs["choice_sn"] = st.radio(
                "꿈의 성향은 어땠나요?",
                options=["S", "N"],
                format_func=lambda value: {
                    "S": "S - 현실적이고 구체적인 일상 같았다",
                    "N": "N - 판타지적이고 추상적이었다",
                }[value],
            )
            mbti_kwargs["choice_tf"] = st.radio(
                "깼을 때 어떤 느낌이 더 강했나요?",
                options=["T", "F"],
                format_func=lambda value: {
                    "T": "T - 인과관계와 원인이 궁금했다",
                    "F": "F - 감정적인 여운이 남았다",
                }[value],
            )

        if st.button("해석 의뢰하기", type="primary", disabled=selected_name is None):
            try:
                dream = Dream(dream_input)
                result = marketplace.hire_interpreter(selected_name, dream, **mbti_kwargs)
                st.session_state.transactions.extend(marketplace.transactions)

                keywords = ", ".join(dream.keywords) if dream.keywords else "(없음)"
                st.info(f"감지된 감정: {dream.emotion_tag} | 키워드: {keywords}")
                st.success(f"해석 완료! 남은 예산: {marketplace.user_budget}원")

                st.markdown("### 🌙 꿈 정보")
                st.code(str(dream), language="text")

                st.markdown("### 🧾 해석 결과")
                st.code(result, language="text")

            except DreamException as error:
                st.error(str(error))
            except ValueError as error:
                st.error(str(error))

    with history_tab:
        st.subheader("📜 거래 이력")

        if not st.session_state.transactions:
            st.info("아직 거래 이력이 없습니다.")
        else:
            for idx, transaction in enumerate(st.session_state.transactions, 1):
                st.write(
                    f"{idx}. {transaction['interpreter']} "
                    f"(비용: {transaction['cost']}원, "
                    f"남은 예산: {transaction['remaining_budget']}원)"
                )
                st.caption(f"꿈: {transaction['dream']}")

            if st.button("거래 이력 초기화"):
                st.session_state.transactions = []
                st.rerun()


if __name__ == "__main__":
    main()
