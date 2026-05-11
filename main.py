"""
OOP-
꿈 해석 거래소: Dream Decoder Marketplace
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
당신의 무의식을 거래하세요. 예산에 맞는 최고의 해석사를 매칭해 드립니다.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Author: 재민
"""
import streamlit as st
from abc import ABC, abstractmethod
from enum import Enum


# ==================== CUSTOM EXCEPTIONS ====================

class DreamException(Exception):
    """꿈 거래소의 기본 예외 클래스"""
    pass


class UninterpretableDreamError(DreamException):
    """해석 불가능한 헛소리 꿈 입력"""
    pass


class InvalidMBTIError(DreamException):
    """MBTI 분기 선택 시 잘못된 입력"""
    pass


class InsufficientFundsError(DreamException):
    """예산 부족으로 모델 호출 불가"""
    pass


# ==================== DATA CLASSES ====================

class Dream:
    """사용자의 꿈 데이터를 담는 객체"""
    
    def __init__(self, content: str):
        if len(content.strip()) < 10:
            raise UninterpretableDreamError(
                "❌ [거래소 시스템] 분석할 데이터가 부족합니다.\\n"
                "   최소 10글자 이상의 꿈을 입력해주세요."
            )
        
        # 키워드 자동 추출 (간단한 예시)
        self.content = content
        self.keywords = self._extract_keywords()
        self.emotion_tag = self._detect_emotion()
    
    def _extract_keywords(self):
        """꿈 내용에서 주요 키워드 추출"""
        stop_words = {'이', '그', '저', '그것', '게', '것', '는', '다', '나', '가', '를', '를', '으로', '로'}
        words = [w for w in self.content.split() if len(w) > 1 and w not in stop_words]
        return words[:5]  # 상위 5개 키워드
    
    def _detect_emotion(self):
        """꿈에서 감정 태그 감지"""
        negative_words = ['죽', '쫓', '빠', '떨어', '무서', '절망', '슬픔', '외로', '불안']
        positive_words = ['즐거', '행복', '설렘', '희망', '성공', '기쁨']
        
        if any(word in self.content for word in negative_words):
            return "🔴 부정적"
        elif any(word in self.content for word in positive_words):
            return "🟢 긍정적"
        else:
            return "🟡 중립적"
    
    def __len__(self):
        """꿈 텍스트의 길이"""
        return len(self.content)
    
    def __str__(self):
        """꿈을 예쁜 일기 포맷으로 출력"""
        return (
            f"\\n🌙 [꿈 일기]\\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n"
            f"내용: {self.content}\\n"
            f"감정: {self.emotion_tag}\\n"
            f"주요 키워드: {', '.join(self.keywords) if self.keywords else '(없음)'}\\n"
            f"글자 수: {len(self.content)}자\\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n"
        )


class Interpreter(ABC):
    """모든 해석가의 부모 클래스"""
    
    def __init__(self, name: str, price: int):
        self.name = name
        self.price = price
        self.reputation = 100  # 초기 평판 점수
    
    def __le__(self, budget: int):
        """사용자의 예산으로 고용 가능한가? (매직 메소드)"""
        return self.price <= budget
    
    def __lt__(self, other):
        """평판순 정렬 시 사용 (매직 메소드)"""
        return self.reputation > other.reputation
    
    def __str__(self):
        """해석가 정보 출력"""
        return f"{self.name} ({self.price}원) | 평판: ⭐ {self.reputation}"
    
    @abstractmethod
    def interpret(self, dream: Dream) -> str:
        """꿈을 해석하는 추상 메서드"""
        pass


# ==================== CONCRETE INTERPRETERS ====================

class MBTIInterpreter(Interpreter):
    """
    일반 모델: MBTI 기반 꿈 해석 (500원)
    S/N → T/F 순차 선택으로 4가지 결과 제공
    """
    
    def __init__(self):
        super().__init__("MBTI 일반 해석사", 500)
    
    def interpret(self, dream: Dream) -> str:
        """MBTI 분기를 통한 인터랙티브 해석"""
        print("\\n" + "="*50)
        print("🔮 [MBTI 일반 해석사의 분석]")
        print("="*50)
        
        # 1차 질문: S/N (감각/직관)
        while True:
            print("\\n[1단계] 꿈의 성향을 선택하세요:")
            print("  S - 현실적이고 구체적인 일상 같았다")
            print("  N - 판타지적이고 추상적이었다")
            choice_sn = input("👉 선택 (S/N): ").strip().upper()
            
            if choice_sn not in ['S', 'N']:
                try:
                    raise InvalidMBTIError("❌ S 또는 N만 입력해주세요!")
                except InvalidMBTIError as e:
                    print(f"{e}\\n")
                    continue
            break
        
        # 2차 질문: T/F (사고/감정)
        while True:
            print("\\n[2단계] 깼을 때의 느낌을 선택하세요:")
            print("  T - 인과관계와 원인이 궁금했다 (논리적)")
            print("  F - 감정적인 여운이 남았다 (감정적)")
            choice_tf = input("👉 선택 (T/F): ").strip().upper()
            
            if choice_tf not in ['T', 'F']:
                try:
                    raise InvalidMBTIError("❌ T 또는 F만 입력해주세요!")
                except InvalidMBTIError as e:
                    print(f"{e}\\n")
                    continue
            break
        
        # 결과 판정
        mbti_type = choice_sn + choice_tf
        interpretations = {
            'ST': (
                "당신의 유형: [ST - 현실 논리형]\\n\\n"
                "📊 해석:\\n"
                "이 꿈은 최근 겪은 현실의 스트레스나 일상 속 문제가\\n"
                "뇌의 논리적 처리 메커니즘에 의해 재구성된 결과입니다.\\n"
                "당신은 꿈 속에서도 'WHY'를 찾으려 했던 거네요.\\n\\n"
                "💡 조언: 현실의 문제를 직시하고 단계별로 해결해 나가세요."
            ),
            'SF': (
                "당신의 유형: [SF - 현실 감정형]\\n\\n"
                "❤️ 해석:\\n"
                "현실에서 느낀 인간관계의 피로감, 서운함, 따뜻함이\\n"
                "무의식중에 감정적으로 발현된 꿈입니다.\\n"
                "당신의 감정 센서가 매우 민감하다는 증거입니다.\\n\\n"
                "💡 조언: 사람들과의 관계를 되짚어보고 감정을 표현하세요."
            ),
            'NT': (
                "당신의 유형: [NT - 직관 논리형]\\n\\n"
                "🧠 해석:\\n"
                "당신의 뇌가 아직 일어나지 않은 미래의 복잡한 변수들을\\n"
                "고차원적으로 시뮬레이션하고 있습니다.\\n"
                "당신은 자신도 모르게 앞날을 예측하려는 존재군요.\\n\\n"
                "💡 조언: 논리적 사고를 바탕으로 미래를 계획하세요."
            ),
            'NF': (
                "당신의 유형: [NF - 직관 감정형]\\n\\n"
                "✨ 해석:\\n"
                "내면 깊은 곳의 이상적인 자아가 현실의 억압을 뚫고\\n"
                "감정적인 해소와 표현을 간절히 요구하고 있습니다.\\n"
                "당신은 꿈꾸는 성향의 예술가 기질을 가진 사람이네요.\\n\\n"
                "💡 조언: 창의성을 발휘하고 진정한 감정을 표현하세요."
            )
        }
        
        return f"\\n{interpretations[mbti_type]}"


class ProfessorInterpreter(Interpreter):
    """
    고급 모델: 교수님 학과 전공 지식 기반 해석 (1000원)
    Social Science & AI 관점에서 고급 분석 제공
    """
    
    def __init__(self):
        super().__init__("🎓 사회과학&AI 교수님", 1000)
    
    def interpret(self, dream: Dream) -> str:
        """전공 지식 기반 고급 해석"""
        dream_len = len(dream)
        keyword_count = len(dream.keywords)
        
        # 꿈의 길이와 키워드 개수에 따라 분석 깊이 결정
        if dream_len > 100 and keyword_count >= 3:
            analysis_level = "심화"
        elif dream_len >= 50:
            analysis_level = "중급"
        else:
            analysis_level = "기초"
        
        # 감정 태그에 따른 관점 선택
        if "부정" in dream.emotion_tag:
            social_analysis = (
                "📍 PESTEL 분석 관점:\\n"
                "  - Social: 현대 사회의 구조적 불안감\\n"
                "  - Political: 통제와 억압에 대한 무의식적 저항\\n"
                "  - Economic: 자본주의 시대의 경쟁 스트레스"
            )
        else:
            social_analysis = (
                "📍 PESTEL 분석 관점:\\n"
                "  - Social: 인간관계와 소속감의 욕구\\n"
                "  - Technological: 미래 가능성에 대한 기대감\\n"
                "  - Economic: 성장과 성공에 대한 동기"
            )
        
        result = (
            f"\\n{'='*60}\\n"
            f"🎓 [사회과학&AI 교수님의 {analysis_level} 분석]\\n"
            f"{'='*60}\\n\\n"
            f"아, 자네 꿈 말이야... 아주 흥미로운 '데이터'군.\\n"
            f"Social Science 렌즈로 분석해 보니 말이지.\\n\\n"
            f"{social_analysis}\\n\\n"
            f"🔬 AI 모델링 제안:\\n"
            f"  → 이 꿈을 NLP와 감정 분석 알고리즘으로 벡터화하면\\n"
            f"     현대인의 심리 패턴을 파악할 수 있겠네.\\n"
            f"  → 키워드: {', '.join(dream.keywords) if dream.keywords else '(시스템 추출 중)'}\\n\\n"
            f"📋 과제: 다음 주까지 이 꿈을 기반으로\\n"
            f"        AI 감정 분석 레포트를 제출하게!\\n\\n"
            f"다시 한 번 말이야, 자네 무의식은\\n"
            f"현대 사회의 구조를 정확히 반영한 훌륭한 데이터야.\\n"
            f"이 지점이 바로 우리 학과의 가치 있는 연구 주제지!\\n"
            f"{'='*60}\\n"
        )
        
        return result


# ==================== MARKETPLACE SYSTEM ====================

class Marketplace:
    """
    꿈 거래를 중개하는 플랫폼 시스템
    사용자 예산과 해석가 가격을 비교하여 매칭
    """
    
    def __init__(self):
        self.interpreters = [
            MBTIInterpreter(),
            ProfessorInterpreter()
        ]
        self.user_budget = 0
        self.transactions = []
    
    def set_user_budget(self, budget: int):
        """사용자의 예산 설정"""
        if budget < 0:
            self.user_budget = 0
        else:
            self.user_budget = budget
    
    def get_available_interpreters(self) -> list:
        """사용자의 예산으로 고용 가능한 해석가 목록"""
        available = [interp for interp in self.interpreters if interp <= self.user_budget]
        return available
    
    def display_marketplace(self):
        """거래소 메인 화면"""
        available = self.get_available_interpreters()
        
        print("\\n" + "="*60)
        print("💰 [꿈 해석 거래소 - 모델 선택]")
        print("="*60)
        print(f"현재 예산: {self.user_budget}원\\n")
        
        if not available:
            print("❌ 예산이 부족하여 모델을 고용할 수 없습니다.")
            print("   최소 500원 이상의 예산이 필요합니다.\\n")
            return None
        
        print("📌 고용 가능한 해석가:\\n")
        
        for idx, interp in enumerate(available, 1):
            status = "🔓 [이용 가능]" if interp.price <= self.user_budget else "🔒 [예산 부족]"
            print(f"  {idx}. {interp.name}")
            print(f"     가격: {interp.price}원 {status}\\n")
        
        # 이용 불가능한 해석가 표시
        unavailable = [interp for interp in self.interpreters if interp > self.user_budget]
        if unavailable:
            print("🔒 [예산 부족으로 이용 불가]:\\n")
            for interp in unavailable:
                shortfall = interp.price - self.user_budget
                print(f"  • {interp.name}")
                print(f"    필요 예산: {interp.price}원 (부족분: {shortfall}원)\\n")
        
        return available
    
    def hire_interpreter(self, choice_idx: int, dream: Dream) -> str:
        """해석가 선택 및 결제 처리"""
        available = self.get_available_interpreters()
        
        if not available:
            raise InsufficientFundsError("❌ 고용 가능한 해석가가 없습니다.")
        
        if choice_idx < 1 or choice_idx > len(available):
            raise ValueError("❌ 올바른 번호를 선택해주세요.")
        
        selected_interpreter = available[choice_idx - 1]
        
        # 결제 처리
        print(f"\\n💳 {selected_interpreter.name}에게 {selected_interpreter.price}원 결제 중...")
        self.user_budget -= selected_interpreter.price
        
        # 해석 실행
        result = selected_interpreter.interpret(dream)
        
        # 거래 기록
        self.transactions.append({
            'interpreter': selected_interpreter.name,
            'dream': dream.content[:30] + '...',
            'cost': selected_interpreter.price
        })
        
        return result
    
    def show_history(self):
        """거래 이력 표시"""
        if not self.transactions:
            print("\\n📜 거래 이력이 없습니다.")
            return
        
        print("\\n" + "="*60)
        print("📜 [거래 이력]")
        print("="*60)
        for idx, trans in enumerate(self.transactions, 1):
            print(f"{idx}. {trans['interpreter']} (비용: {trans['cost']}원)")
            print(f"   꿈: {trans['dream']}\\n")


# ==================== MAIN GAME FLOW ====================

def main():
    """게임 메인 루프"""
    print("\n" + "="*60)
    print("🌙 꿈 해석 거래소 (Dream Decoder Marketplace) 🌙")
    print("="*60)
    print("당신의 무의식을 거래하세요.")
    print("예산에 맞는 최고의 해석사를 매칭해 드립니다.\n")
    
    marketplace = Marketplace()
    
    while True:
        print("\n" + "="*60)
        print("[메뉴]")
        print("="*60)
        print("1. 새 꿈 입력 및 해석 시작")
        print("2. 거래 이력 보기")
        print("3. 게임 종료")
        
        menu_choice = input("\n선택 (1-3): ").strip()
        
        if menu_choice == '1':
            try:
                # 꿈 입력
                print("\n📝 [꿈 입력]")
                print("-" * 40)
                dream_input = input("어젯밤 꾼 꿈을 입력하세요 (10자 이상): ").strip()
                
                try:
                    dream = Dream(dream_input)
                except UninterpretableDreamError as e:
                    print(f"\n{e}\n")
                    continue
                
                # 꿈 정보 표시
                print(dream)
                
                # 예산 입력
                print("💰 [예산 설정]")
                print("-" * 40)
                try:
                    budget = int(input("꿈 해석에 얼마를 지불하시겠습니까? (원): "))
                    if budget < 0:
                        budget = 0
                except ValueError:
                    print("❌ 숫자를 입력해주세요.")
                    continue
                
                marketplace.set_user_budget(budget)
                
                # 거래소 메인 화면
                available = marketplace.display_marketplace()
                
                if available is None:
                    print("💬 예산을 충전하고 다시 시도해주세요.")
                    continue
                
                # 해석가 선택
                try:
                    choice_str = input("\n해석가 번호를 선택하세요 (1-{}): ".format(len(available)))
                    choice_idx = int(choice_str)
                    
                    # 해석 실행
                    interpretation = marketplace.hire_interpreter(choice_idx, dream)
                    print(interpretation)
                    
                    print(f"\n✅ 해석 완료! 남은 예산: {marketplace.user_budget}원")
                
                except InsufficientFundsError as e:
                    print(f"\n{e}\n")
                except ValueError as e:
                    print(f"\n❌ {e}\n")
                
            except Exception as e:
                print(f"\n⚠️ 오류 발생: {e}\n")
        
        elif menu_choice == '2':
            marketplace.show_history()
        
        elif menu_choice == '3':
            print("\n" + "="*60)
            print("🌙 꿈 해석 거래소를 종료합니다.")
            print(f"   총 거래 횟수: {len(marketplace.transactions)}")
            print(f"   남은 예산: {marketplace.user_budget}원")
            print("="*60)
            print("\n고마워요! 즐거운 꿈의 세계를 경험하셨기를 바랍니다. 🌙\n")
            break
        
        else:
            print("\n❌ 올바른 선택을 입력해주세요.\n")


# ==================== PROGRAM ENTRY POINT ====================

if __name__ == "__main__":
    main()
