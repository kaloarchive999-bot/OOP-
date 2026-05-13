# -*- coding: utf-8 -*-
"""
무의식 재판소 - 드림 인젝터 (Dream Injector)
[해석가별 다형성 극대화 및 MBTI SF 추가 완료 버전]
"""

import streamlit as st
from abc import ABC, abstractmethod
import random
import hashlib
import re

# ================================================================
# [UI 디자인] Neo-Clinical / Lucid Dream 스타일
# ================================================================
st.set_page_config(page_title="무의식 재판소", page_icon="🧠", layout="centered")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f3e8ff 0%, #e0c3fc 100%) fixed; font-family: 'Noto Sans KR', sans-serif; }
    .main-title { text-align: center; color: #3a0ca3; font-weight: 900; font-size: 2.5rem; text-shadow: 2px 2px 4px rgba(255,255,255,0.8); margin-bottom: 5px; }
    .sub-title { text-align: center; color: #7b2cbf; margin-bottom: 30px; font-weight: bold;}
    .keyword-badge { background-color: #4cc9f0; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; margin-right: 5px; }
    .result-box { background: rgba(255, 255, 255, 0.95); padding: 25px; border-radius: 12px; border-left: 6px solid #7b2cbf; box-shadow: 0 8px 20px rgba(0,0,0,0.15); margin-top: 20px; }
    .stTextArea textarea { background: rgba(255, 255, 255, 0.9) !important; border: 2px solid #b5179e !important; }
</style>
""", unsafe_allow_html=True)


# ================================================================
# [SECTION A] 예외 처리 및 Dream 클래스 (키워드 자동 패딩 보완)
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
        """키워드 추출 및 무조건 3개 맞추기 로직"""
        words = re.findall(r'\b[가-힣]{2,}\b', text)
        stop_words = ["있는", "없다", "너무", "정말", "그리고", "그래서", "나는", "내가", "꿈을", "꿨어"]
        keywords = [w for w in words if w not in stop_words]
        
        # 키워드가 3개 미만일 경우, 분석이 깨지지 않도록 가상의 무의식 단어 추가
        fallback_words = ["무의식", "잔상", "충동", "심상", "파편", "감각"]
        while len(keywords) < 3:
            keywords.append(random.choice(fallback_words))
            
        random.shuffle(keywords)
        return keywords[:3] # 무조건 3개만 반환

    def __len__(self):
        return len(self.raw_text)


# ================================================================
# [SECTION B] Interpreter 부모 클래스
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


# ================================================================
# [SECTION C] 자식 클래스 (다형성 및 다양한 텍스트 생성 로직 극대화)
# ================================================================
class ProfessorInterpreter(Interpreter):
    def __init__(self):
        super().__init__("이동현 교수", "SSAI 사회과학 분석가", ["권력/감시 (푸코)", "자본/계급 (마르크스)", "기호/소비 (보드리야르)"])

    def process(self, dream: Dream, option: str) -> dict:
        kws = dream.keywords
        if option == "권력/감시 (푸코)":
            analysis = f"'{kws[0]}' 현상은 판옵티콘적 통제 사회를 은유합니다. 시스템이 부여한 '{kws[1]}'라는 규율에 순응하면서도, 내면에서는 '{kws[2]}'의 형태로 무의식적 일탈을 꾀하고 있는 것이죠."
        elif option == "자본/계급 (마르크스)":
            analysis = f"'{kws[0]}'는 자본주의의 물신주의적 욕망을 상징합니다. 당신의 뇌는 '{kws[1]}'라는 착취적 구조 속에서 생산 수단을 빼앗긴 소외감을 '{kws[2]}'라는 이미지로 투영하여 고발하고 있습니다."
        else:
            analysis = f"우리는 파생실재(시뮬라크르) 속에 살고 있습니다. 꿈속의 '{kws[0]}'는 진짜가 아닌 미디어가 주입한 기호일 뿐입니다. '{kws[1]}'와 '{kws[2]}' 역시 현대 소비 사회가 만들어낸 가짜 욕망의 잔상입니다."
            
        verdict = f"<b>[사회과학 논문 초록 발췌]</b><br>추출된 변수 {self._format_keywords(kws)}를 분석한 결과:<br><br>{analysis}<br>이 데이터는 현대 사회의 구조적 모순을 명확히 보여줍니다."
        return {"verdict": verdict, "risk": "HIGH"}

class MBTIInterpreter(Interpreter):
    def __init__(self):
        # 누락되었던 SF 추가 및 4가지 기능으로 완벽 분리
        super().__init__("MBTI 전문가 미나", "인지기능 심리 분석관", ["ST (감각-사고)", "SF (감각-감정)", "NT (직관-사고)", "NF (직관-감정)"])

    def process(self, dream: Dream, option: str) -> dict:
        kws = dream.keywords
        if option == "ST (감각-사고)":
            analysis = f"ST 유형의 뇌는 매우 실용적이죠. '{kws[0]}'라는 구체적인 현실의 문제를 해결하기 위해, '{kws[1]}'와 '{kws[2]}' 사이의 논리적 인과관계를 수면 중에 시뮬레이션하고 있는 겁니다. 효율적인 리스크 분석이네요!"
        elif option == "SF (감각-감정)":
            analysis = f"SF 유형답게 타인과의 관계에 예민하시군요. 현실에서 겪은 '{kws[0]}'라는 구체적 사건에서 느낀 서운함이 '{kws[1]}'라는 감정으로 뭉쳤고, 결국 '{kws[2]}'의 형태로 꿈에서 터져 나온 거랍니다. 따뜻한 위로가 필요해요."
        elif option == "NT (직관-사고)":
            analysis = f"NT 유형의 무의식은 시스템 설계자입니다. 현실에 존재하지 않는 '{kws[0]}'라는 변수를 던져놓고, '{kws[1]}' 상황이 발생했을 때 '{kws[2]}'라는 결과가 나올지 거시적인 뇌내 알고리즘을 돌리는 중이군요."
        else: # NF
            analysis = f"NF의 이상주의적 감수성이 폭발한 꿈이네요! '{kws[0]}'는 당신이 잃어버린 내면의 순수함을 상징해요. 현실의 억압을 뚫고 '{kws[1]}'를 향해 나아가고자 하는 영혼의 갈망이 '{kws[2]}'라는 아름답고도 슬픈 이미지로 피어났습니다."
            
        verdict = f"<b>[인지 기능 진단 리포트]</b><br>키워드 {self._format_keywords(kws)}를 바탕으로 한 인지 처리 과정:<br><br>{analysis}"
        return {"verdict": verdict, "risk": "MEDIUM"}

class TherapistInterpreter(Interpreter):
    def __init__(self):
        super().__init__("닥터 융/프로이트", "전통 수면 치료사", ["억압된 욕망 (프로이트)", "집단 무의식 (융)", "열등감 극복 (아들러)"])

    def process(self, dream: Dream, option: str) -> dict:
        kws = dream.keywords
        if option == "억압된 욕망 (프로이트)":
            analysis = f"당신의 자아(Ego)가 숨기려 했던 파괴적이고 원초적인 리비도가 드러났습니다. '{kws[0]}'는 사회적 금기에 대한 당신의 욕망을 은유하며, '{kws[1]}'는 거세 불안의 변형입니다. '{kws[2]}'는 무의식의 노골적인 경고입니다."
        elif option == "집단 무의식 (융)":
            analysis = f"이것은 개인이 아닌 인류 보편의 상징입니다. '{kws[0]}'는 당신이 부정해 온 어두운 '그림자(Shadow)' 원형입니다. '{kws[1]}'와 맞서 싸우며 '{kws[2]}'를 거치는 과정은 곧 온전한 자기(Self)로 나아가는 영적 성장입니다."
        else: # 아들러
            analysis = f"이 꿈은 당신이 현실에서 느끼는 깊은 무력감의 반동입니다. '{kws[0]}'라는 열등감을 극복하기 위해 당신의 뇌가 '{kws[1]}'를 연출한 것이죠. '{kws[2]}'는 당신 내면에 숨겨진 '권력에의 의지'가 발현된 형태입니다."
            
        verdict = f"<b>[심층 정신분석 상담]</b><br>무의식의 징후 {self._format_keywords(kws)}를 심리학적으로 접근합니다:<br><br>{analysis}"
        return {"verdict": verdict, "risk": "LOW"}


# 전역 객체 생성
interpreters = {
    "professor": ProfessorInterpreter(),
    "mbti": MBTIInterpreter(),
    "therapist": TherapistInterpreter()
}


# ================================================================
# [SECTION D] Streamlit 화면 렌더링
# ================================================================
def main():
    st.markdown("<h1 class='main-title'>UNCONSCIOUS COURT</h1>", unsafe_allow_html=True)
    st.markdown("<h4 class='sub-title'>Dream Injector : 다형성 기반 무의식 분석 시스템</h4>", unsafe_allow_html=True)

    # 1. 꿈 입력
    st.write("### [ STEP 1 ] 원시 꿈 입고")
    dream_input = st.text_area("시민의 무의식 단편을 입력해 주십시오. (최소 10자 이상)", height=100)

    # 2. 해석가 선택
    st.write("---")
    st.write("### [ STEP 2 ] 해석가 배정")
    interp_keys = list(interpreters.keys())
    interp_names = [f"{interpreters[k].name} ({interpreters[k].title})" for k in interp_keys]
    
    selected_name_full = st.radio("어떤 해석가에게 꿈의 분석을 맡기시겠습니까?", interp_names)
    selected_idx = interp_names.index(selected_name_full)
    selected_key = interp_keys[selected_idx]
    selected_interp = interpreters[selected_key]

    # 3. 가공 방식 선택
    st.write("---")
    st.write(f"### [ STEP 3 ] {selected_interp.name}의 가공 방식 선택")
    selected_opt = st.selectbox("적용할 심층 분석 알고리즘을 선택하세요:", selected_interp.options)

    # 4. 실행 버튼
    st.write("")
    if st.button("▶ INJECT DREAM (분석 및 주입)", use_container_width=True):
        try:
            # OOP 로직 실행
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
                <p style='font-size: 1.05rem; line-height: 1.8; color: #1f2937;'>{result['verdict']}</p>
            </div>
            """, unsafe_allow_html=True)
            
        except UnprocessableDreamError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"시스템 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()
