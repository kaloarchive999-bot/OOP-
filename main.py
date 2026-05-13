# -*- coding: utf-8 -*-
"""
무의식 재판소 - 드림 인젝터 (Dream Injector)
Streamlit 전용 버전
"""

import streamlit as st
from abc import ABC, abstractmethod
import random
import hashlib
import datetime

# ================================================================
# [UI 디자인] Neo-Clinical / Lucid Dream 스타일 주입
# ================================================================
st.set_page_config(page_title="무의식 재판소", page_icon="🧠", layout="centered")

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%) fixed;
        font-family: 'Noto Sans KR', sans-serif;
    }
    .main-title {
        text-align: center;
        color: #4a4e69;
        font-weight: 900;
        font-size: 2.5rem;
        text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.8);
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #5a189a;
        margin-bottom: 30px;
    }
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid #c8b6ff !important;
        border-radius: 8px !important;
    }
    .result-box {
        background: rgba(255, 255, 255, 0.85);
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #9d4edd;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)


# ================================================================
# [SECTION A] 사용자 정의 예외
# ================================================================
class DreamInjectorError(Exception):
    pass

class UnprocessableDreamError(DreamInjectorError):
    pass

# ================================================================
# [SECTION B] Dream 데이터 클래스
# ================================================================
class Dream:
    MIN_LENGTH = 10

    def __init__(self, raw_text: str):
        if not isinstance(raw_text, str):
            raise UnprocessableDreamError("꿈 데이터는 텍스트 형식이어야 합니다.")
        cleaned = raw_text.strip()
        if len(cleaned) < self.MIN_LENGTH:
            raise UnprocessableDreamError(
                f"⚠ 무의식 단편이 너무 짧습니다. 최소 {self.MIN_LENGTH}자 이상의 꿈 조각이 필요합니다. (현재 {len(cleaned)}자)"
            )
        self.raw_text = cleaned
        self.citizen_id = hashlib.sha256(cleaned.encode("utf-8")).hexdigest()[:8].upper()
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __len__(self):
        return len(self.raw_text)

# ================================================================
# [SECTION C & D] Interpreter 부모 및 자식 클래스
# ================================================================
class Interpreter(ABC):
    def __init__(self, name: str, title: str, options: list):
        self.name = name
        self.title = title
        self.options = options

    @abstractmethod
    def process(self, dream_text: str, option: str) -> dict:
        raise NotImplementedError

class ProfessorInterpreter(Interpreter):
    def __init__(self):
        super().__init__("이동현 교수", "SSAI 사회과학 분석가", ["정치/권력 관점", "자본/경제 관점", "사회/문화 관점", "기술/AI 관점"])

    def process(self, dream_text: str, option: str) -> dict:
        temps = {
            "정치/권력 관점": f"이 꿈 '{dream_text[:15]}...'은 국가 통제에 대한 무의식적 저항의 발현입니다.",
            "자본/경제 관점": f"명백하군요. '{dream_text[:15]}...'는 자본주의 무한 경쟁이 주는 극도의 스트레스입니다.",
            "사회/문화 관점": f"현대인의 소외감이 투영되었습니다. '{dream_text[:15]}...'에서 그 단절감이 느껴지네요.",
            "기술/AI 관점": f"AI 알고리즘 지배에 따른 인지 과부하 현상입니다. '{dream_text[:15]}...'이 그 증거죠."
        }
        return {"verdict": temps[option], "risk": "HIGH"}

class MBTIInterpreter(Interpreter):
    def __init__(self):
        super().__init__("MBTI 전문가 미나", "대중 심리 분석관", ["ST (감각-사고)", "SF (감각-감정)", "NT (직관-사고)", "NF (직관-감정)"])

    def process(self, dream_text: str, option: str) -> dict:
        temps = {
            "ST (감각-사고)": f"현실의 스트레스가 논리적으로 재구성된 결과입니다. '{dream_text[:15]}...'",
            "SF (감각-감정)": f"인간관계의 피로감이 감정적으로 폭발했네요. '{dream_text[:15]}...'",
            "NT (직관-사고)": f"미래의 변수들을 뇌가 고차원적으로 시뮬레이션 중입니다. '{dream_text[:15]}...'",
            "NF (직관-감정)": f"억압된 자아가 해방을 요구하는 예술적 기질의 발현입니다. '{dream_text[:15]}...'"
        }
        return {"verdict": temps[option], "risk": "MEDIUM"}

class TherapistInterpreter(Interpreter):
    def __init__(self):
        super().__init__("닥터 프로이트", "전통 수면 치료사", ["유년기 트라우마", "현실 도피 및 퇴행", "억압된 무의식", "자아 통합 과정"])

    def process(self, dream_text: str, option: str) -> dict:
        temps = {
            "유년기 트라우마": f"'{dream_text[:15]}...'는 어릴 적 부모님과의 애착 관계 상실을 의미합니다.",
            "현실 도피 및 퇴행": f"무거운 책임을 회피하고 싶은 유아기적 퇴행 심리입니다. '{dream_text[:15]}...'",
            "억압된 무의식": f"사회적 체면에 짓눌린 본능적 욕구가 비틀려 폭발했습니다. '{dream_text[:15]}...'",
            "자아 통합 과정": f"분열된 정신이 스스로를 치유해 가는 긍정적인 과정입니다. '{dream_text[:15]}...'"
        }
        return {"verdict": temps[option], "risk": "LOW"}

# 전역 객체 생성
interpreters = {
    "professor": ProfessorInterpreter(),
    "mbti": MBTIInterpreter(),
    "therapist": TherapistInterpreter()
}

# ================================================================
# [SECTION E] Streamlit 화면 렌더링 (프론트엔드 역할)
# ================================================================
def main():
    st.markdown("<h1 class='main-title'>UNCONSCIOUS COURT</h1>", unsafe_allow_html=True)
    st.markdown("<h4 class='sub-title'>Dream Injector v2077.11.13</h4>", unsafe_allow_html=True)

    # 1. 꿈 입력
    st.subheader("[ STEP 1 ] 원시 꿈 입고")
    dream_input = st.text_area("시민의 무의식 단편을 최소 10자 이상 입력해 주십시오.", height=120)

    # 2. 해석가 선택
    st.subheader("[ STEP 2 ] 해석가 배정")
    interp_keys = list(interpreters.keys())
    interp_names = [interpreters[k].name for k in interp_keys]
    
    selected_name = st.radio("어떤 해석가에게 꿈을 맡기시겠습니까?", interp_names, horizontal=True)
    selected_key = interp_keys[interp_names.index(selected_name)]
    selected_interp = interpreters[selected_key]

    # 3. 가공 방식 선택
    st.subheader(f"[ STEP 3 ] {selected_interp.name}의 가공 방식 선택")
    selected_opt = st.selectbox("적용할 분석 렌즈를 선택하세요:", selected_interp.options)

    # 4. 실행 버튼
    st.write("---")
    if st.button("▶ INJECT DREAM (꿈 검열 및 주입)", use_container_width=True):
        try:
            # OOP 로직 실행
            dream = Dream(dream_input)
            result = selected_interp.process(dream.raw_text, selected_opt)
            
            # 결과 출력
            st.markdown(f"""
            <div class='result-box'>
                <h3 style='color: #3a0ca3; margin-top: 0;'>[ 검열 완료 리포트 ]</h3>
                <p><b>CITIZEN ID:</b> CITIZEN-{dream.citizen_id}</p>
                <p><b>LENGTH:</b> {len(dream)} 자</p>
                <p><b>RISK LEVEL:</b> {result['risk']}</p>
                <hr>
                <p style='font-size: 1.1rem; line-height: 1.6; color: #333;'>{result['verdict']}</p>
                <p style='color: #198754; font-weight: bold; margin-bottom: 0;'>✓ 시민의 뇌에 안전하게 주입되었습니다.</p>
            </div>
            """, unsafe_allow_html=True)
            
        except UnprocessableDreamError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"시스템 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()
