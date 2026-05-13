# -*- coding: utf-8 -*-
"""
무의식 재판소 - 드림 인젝터 (Dream Injector)
[키워드 기반 동적 분석 시스템 적용 버전]
"""

import streamlit as st
from abc import ABC, abstractmethod
import random
import hashlib
import datetime
import re

# ================================================================
# [UI 디자인] Neo-Clinical / Lucid Dream 스타일 주입
# ================================================================
st.set_page_config(page_title="무의식 재판소", page_icon="🧠", layout="centered")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f3e8ff 0%, #e0c3fc 100%) fixed; font-family: 'Noto Sans KR', sans-serif; }
    .main-title { text-align: center; color: #3a0ca3; font-weight: 900; font-size: 2.5rem; text-shadow: 2px 2px 4px rgba(255,255,255,0.8); margin-bottom: 5px; }
    .sub-title { text-align: center; color: #7b2cbf; margin-bottom: 30px; font-weight: bold;}
    .keyword-badge { background-color: #4cc9f0; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold; margin-right: 5px; }
    .result-box { background: rgba(255, 255, 255, 0.9); padding: 25px; border-radius: 12px; border-left: 6px solid #7b2cbf; box-shadow: 0 8px 20px rgba(0,0,0,0.1); margin-top: 20px; }
    .stTextArea textarea { background: rgba(255, 255, 255, 0.9) !important; border: 2px solid #b5179e !important; }
</style>
""", unsafe_allow_html=True)


# ================================================================
# [SECTION A] 예외 처리 및 Dream 클래스 (키워드 추출 포함)
# ================================================================
class UnprocessableDreamError(Exception):
    pass

class Dream:
    MIN_LENGTH = 10

    def __init__(self, raw_text: str):
        cleaned = raw_text.strip()
        if len(cleaned) < self.MIN_LENGTH:
            raise UnprocessableDreamError(f"⚠ 무의식 단편이 너무 짧습니다. (최소 {self.MIN_LENGTH}자)")
        
        self.raw_text = cleaned
        self.citizen_id = hashlib.sha256(cleaned.encode("utf-8")).hexdigest()[:6].upper()
        self.keywords = self._extract_keywords(cleaned)
        
    def _extract_keywords(self, text):
        """간단한 공백/조사 분리를 통한 키워드 추출 (단어 2글자 이상)"""
        words = re.findall(r'\b[가-힣]{2,}\b', text)
        # 의미 없는 흔한 조사/어미 필터링
        stop_words = ["있는", "없다", "너무", "정말", "그리고", "그래서", "나는", "내가"]
        keywords = [w for w in words if w not in stop_words]
        
        # 키워드가 너무 적으면 임의의 단어 추가 (시스템 안정성)
        if len(keywords) < 2:
            keywords.extend(["이_장면", "이_감각"])
        
        # 랜덤하게 최대 3개의 핵심 키워드만 선정
        random.shuffle(keywords)
        return keywords[:3]

    def __len__(self):
        return len(self.raw_text)

# ================================================================
# [SECTION B] Interpreter 클래스 (키워드 매핑 다형성)
# ================================================================
class Interpreter(ABC):
    def __init__(self, name: str, title: str, options: list):
        self.name = name
        self.title = title
        self.options = options

    @abstractmethod
    def process(self, dream: Dream, option: str) -> dict:
        raise NotImplementedError
        
    def _format_keywords(self, keywords):
        return " ".join([f"<span class='keyword-badge'>{kw}</span>" for kw in keywords])

class ProfessorInterpreter(Interpreter):
    def __init__(self):
        super().__init__("이동현 교수", "SSAI 사회과학 분석가", ["권력/통제 관점", "자본/경쟁 관점", "기술/AI 관점"])

    def process(self, dream: Dream, option: str) -> dict:
        kws = dream.keywords
        # 키워드 동적 매핑
        if option == "권력/통제 관점":
            analysis = f"'{kws[0]}' 현상은 현대 사회의 억압적 시스템을 은유하며, '{kws[1]}'에서 보이는 징후는 통제에 대한 시민의 무의식적 저항을 뜻합니다."
        elif option == "자본/경쟁 관점":
            analysis = f"자본주의의 폐해가 여실히 드러납니다. '{kws[0]}'는 성과주의의 압박을, '{kws[1]}'는 물질적 결핍에서 오는 극도의 스트레스를 상징하죠."
        else: # 기술/AI 관점
            analysis = f"알고리즘의 과부하군요. '{kws[0]}'라는 이미지는 정보의 홍수 속에서 인지 능력을 상실해가는 뇌의 파편화 과정을 보여줍니다."
            
        verdict = f"<b>[논문 초록 발췌]</b><br>이 꿈의 핵심 요소인 {self._format_keywords(kws)}를 분석한 결과:<br><br>{analysis}<br>따라서 이 데이터는 사회 구조적 불안정성을 시사합니다."
        return {"verdict": verdict, "risk": "HIGH"}

class MBTIInterpreter(Interpreter):
    def __init__(self):
        super().__init__("MBTI 전문가 미나", "인지기능 심리 분석관", ["ST (현실/논리)", "NF (직관/감정)", "NT (직관/사고)"])

    def process(self, dream: Dream, option: str) -> dict:
        kws = dream.keywords
        if option == "ST (현실/논리)":
            analysis = f"ST 유형의 뇌는 '{kws[0]}'라는 구체적인 현실의 스트레스를 '{kws[1]}'라는 인과 관계로 묶어서 시뮬레이션하고 있어요. 매우 실용적인 뇌 활동입니다."
        elif option == "NF (직관/감정)":
            analysis = f"NF의 풍부한 감수성이 폭발했네요! '{kws[0]}'는 내면의 이상을, '{kws[1]}'는 타인과 연결되고 싶은 깊은 갈망(Fi)을 아름답게 표현하고 있어요."
        else: # NT
            analysis = f"NT 유형답게 뇌가 아직 일어나지 않은 미래를 계산 중입니다. '{kws[0]}' 변수를 넣고 '{kws[1]}' 상황을 예측하는 고차원적 사고 과정이죠."
            
        verdict = f"<b>[인지 기능 진단]</b><br>추출된 심상 {self._format_keywords(kws)}를 인지 기능으로 뜯어볼게요:<br><br>{analysis}<br>당신의 뇌는 지금 아주 바쁘게 일하고 있네요!"
        return {"verdict": verdict, "risk": "MEDIUM"}

class TherapistInterpreter(Interpreter):
    def __init__(self):
        super().__init__("닥터 융/프로이트", "전통 수면 치료사", ["그림자 원형 (융)", "억압된 욕망 (프로이트)", "자아 통합 과정"])

    def process(self, dream: Dream, option: str) -> dict:
        kws = dream.keywords
        if option == "그림자 원형 (융)":
            analysis = f"'{kws[0]}'는 당신이 인정하고 싶지 않은 내면의 어두운 '그림자(Shadow)'입니다. '{kws[1]}'를 통해 그 그림자가 수면 위로 올라오려 하고 있습니다."
        elif option == "억압된 욕망 (프로이트)":
            analysis = f"'{kws[0]}'는 사회적 도덕에 의해 억눌린 당신의 가장 원초적인 욕구입니다. 이것이 '{kws[1]}'라는 형태로 치환되어 꿈에 발현된 것입니다."
        else:
            analysis = f"'{kws[0]}'의 혼란은 치유의 시작입니다. 결국 '{kws[1]}'를 거치며 분열된 당신의 자아가 온전하게 통합되어 갈 것입니다."
            
        verdict = f"<b>[무의식 심층 상담]</b><br>무의식의 조각 {self._format_keywords(kws)}를 심리학적으로 접근해 봅시다:<br><br>{analysis}<br>이 과정을 두려워하지 마세요. 치유의 일부입니다."
        return {"verdict": verdict, "risk": "LOW"}

# 전역 객체
interpreters = {
    "professor": ProfessorInterpreter(),
    "mbti": MBTIInterpreter(),
    "therapist": TherapistInterpreter()
}

# ================================================================
# [SECTION C] Streamlit 렌더링
# ================================================================
def main():
    st.markdown("<h1 class='main-title'>UNCONSCIOUS COURT</h1>", unsafe_allow_html=True)
    st.markdown("<h4 class='sub-title'>Dream Injector : 키워드 동적 분석 시스템</h4>", unsafe_allow_html=True)

    # 1. 꿈 입력
    st.write("### [ STEP 1 ] 원시 꿈 입고")
    dream_input = st.text_area("시민의 무의식 단편을 입력해 주십시오. (최소 10자 이상, 명사/동사 위주로 쓰면 분석이 정교해집니다.)", height=100)

    # 2. 해석가 선택
    st.write("---")
    st.write("### [ STEP 2 ] 해석가 배정")
    interp_keys = list(interpreters.keys())
    interp_names = [f"{interpreters[k].name} ({interpreters[k].title})" for k in interp_keys]
    
    selected_name_full = st.radio("어떤 해석가에게 꿈의 키워드 분석을 맡기시겠습니까?", interp_names)
    selected_idx = interp_names.index(selected_name_full)
    selected_key = interp_keys[selected_idx]
    selected_interp = interpreters[selected_key]

    # 3. 가공 방식 선택
    st.write("---")
    st.write(f"### [ STEP 3 ] {selected_interp.name}의 가공 방식 선택")
    selected_opt = st.selectbox("적용할 분석 알고리즘을 선택하세요:", selected_interp.options)

    # 4. 실행 버튼
    st.write("")
    if st.button("▶ INJECT DREAM (키워드 분석 및 주입)", use_container_width=True):
        try:
            # OOP 로직 실행 (키워드 추출됨)
            dream = Dream(dream_input)
            result = selected_interp.process(dream, selected_opt)
            
            # 결과 출력
            st.markdown(f"""
            <div class='result-box'>
                <h3 style='color: #4a044e; margin-top: 0;'>[ 검열 완료 리포트 ]</h3>
                <p><b>CITIZEN ID:</b> CITIZEN-{dream.citizen_id}</p>
                <p><b>추출된 핵심 키워드:</b> {selected_interp._format_keywords(dream.keywords)}</p>
                <p><b>RISK LEVEL:</b> {result['risk']}</p>
                <hr style='border-color: #e0aaff;'>
                <p style='font-size: 1.1rem; line-height: 1.8; color: #1f2937;'>{result['verdict']}</p>
            </div>
            """, unsafe_allow_html=True)
            
        except UnprocessableDreamError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"시스템 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()
