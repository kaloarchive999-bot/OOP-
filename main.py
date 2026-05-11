# main.py
# 무의식 재판소 - Dream Injector (Streamlit 버전)
# 실행: streamlit run main.py
# 요구사항: streamlit (pip install streamlit)

import streamlit as st
import random
import copy
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable

# =====================================================================
# 0. 페이지 설정
# =====================================================================
st.set_page_config(
    page_title="무의식 재판소 - Dream Injector",
    page_icon="🌙",
    layout="wide",
)

# =====================================================================
# 1. 상수 & 데이터
# =====================================================================
KEYWORD_POOL = [
    ["바다", "유리", "어머니"],
    ["철도", "거울", "아버지"],
    ["눈물", "기계", "유년"],
    ["불꽃", "전화", "친구"],
    ["숲속", "편지", "연인"],
    ["도시", "시계", "스승"],
    ["빗물", "열쇠", "동생"],
    ["사막", "사진", "이방인"],
]

BODY_PARTS = ["심장", "눈", "혀", "귀", "손", "발", "뇌", "폐"]

APOSTLE_MOTIVES = {
    "실존주의자형": "...존재한다는 것은 결국 검열당하는 것 아닌가.",
    "유족형": "내 가족의 꿈을 당신들이 지웠어. 잊지 않았다.",
    "AI 잔여의식형": "01001000... 나는 삭제된 코드의 메아리다.",
}

EVENTS = {
    "황사 경보": "진술이 단축됩니다. (정보가 줄어듦)",
    "송신탑 노이즈": "사도가 추가로 키워드 1개를 더 잃습니다.",
    "예산 삭감": "재판장 예산 20% 회수, 보상 2배.",
    "집단 악몽": "키워드 1개가 강제 치환됩니다.",
    "검열 해제일": "이번 라운드는 모두 진실을 말합니다.",
}

# =====================================================================
# 2. Dream 객체 - __getitem__ 매직 메소드로 정보 비대칭 강제
# =====================================================================
class Dream:
    """꿈 객체. 사도가 접근하면 3번째 키워드를 '???'로 마스킹."""
    def __init__(self, keywords: List[str]):
        self._keywords = list(keywords)
        self._extra_mask: List[int] = []   # 송신탑 노이즈로 추가 마스킹

    def view_for(self, role_name: str, idx: int) -> str:
        """역할 이름 기반 안전 접근."""
        if idx < 0 or idx >= len(self._keywords):
            return "???"
        if role_name == "악몽의 사도" and idx == 2:
            return "???"
        if idx in self._extra_mask and role_name == "악몽의 사도":
            return "???"
        return self._keywords[idx]

    def full_view(self, role_name: str) -> List[str]:
        return [self.view_for(role_name, i) for i in range(len(self._keywords))]

    def real_keywords(self) -> List[str]:
        return list(self._keywords)

    def replace_keyword(self, idx: int, new_word: str):
        if 0 <= idx < len(self._keywords):
            self._keywords[idx] = new_word

    def add_mask(self, idx: int):
        if idx not in self._extra_mask:
            self._extra_mask.append(idx)

# =====================================================================
# 3. Strategy 패턴 - 직업별 화법
# =====================================================================
class SpeechStrategy(ABC):
    role_name: str = "시민"

    @abstractmethod
    def speak(self, dream: Dream, role_name_for_view: str, self_interest: str) -> str:
        ...

class HackerStrategy(SpeechStrategy):
    role_name = "무의식 해커"
    def speak(self, dream, role_name_for_view, self_interest):
        kws = dream.full_view(role_name_for_view)
        hexes = []
        for w in kws:
            if w == "???":
                hexes.append("0x????")
            else:
                # 한글/문자 → 유니코드 hex 변환 (앞 2글자)
                hx = "".join(f"{ord(c):04X}" for c in w[:2])
                hexes.append(f"0x{hx}")
        return f"[해커] 디코딩 결과: {' / '.join(hexes)} ... 사익코드={self_interest}"

class FreudStrategy(SpeechStrategy):
    role_name = "프로이트 수면치료사"
    def speak(self, dream, role_name_for_view, self_interest):
        kws = dream.full_view(role_name_for_view)
        bp = random.choice(BODY_PARTS)
        pick = random.choice([k for k in kws if k != "???"] or ["무의식"])
        return f"[치료사] 환자의 '{pick}'는 '{bp}'에 억압되어 있군요. (잠재 욕망:{self_interest})"

class LeeProfessorStrategy(SpeechStrategy):
    role_name = "이동현 교수"
    def speak(self, dream, role_name_for_view, self_interest):
        kws = dream.full_view(role_name_for_view)
        return f"[교수] 학술적으로 보면 {kws[0]}와 {kws[1]}의 상관은 0.{random.randint(60,99)}. ({self_interest})"

class ShamanStrategy(SpeechStrategy):
    role_name = "사이버 무당"
    def speak(self, dream, role_name_for_view, self_interest):
        kws = dream.full_view(role_name_for_view)
        return f"[무당] 영적 진동이… {kws[-1]} 쪽에서 강하게 느껴진다… 사익의 별자리: {self_interest}"

class YoutuberStrategy(SpeechStrategy):
    role_name = "딥다이브 유튜버"
    def speak(self, dream, role_name_for_view, self_interest):
        # 진짜 키워드 3개 의무 언급 + 가짜 1개 추가
        kws = dream.full_view(role_name_for_view)
        fake = random.choice(["악어", "네온", "오로라", "잔향"])
        return f"[유튜버] 구독자 여러분! 오늘의 키워드는 {', '.join(kws)} 그리고 사실은 '{fake}'!! ({self_interest})"

class TombRaiderStrategy(SpeechStrategy):
    role_name = "드림 도굴꾼"
    def speak(self, dream, role_name_for_view, self_interest):
        kws = dream.full_view(role_name_for_view)
        return f"[도굴꾼] 지난 라운드 누군가 '{random.choice(kws)}'을(를) 언급했지… 그게 단서다. ({self_interest})"

ROLE_STRATEGIES = {
    "무의식 해커": HackerStrategy,
    "프로이트 수면치료사": FreudStrategy,
    "이동현 교수": LeeProfessorStrategy,
    "사이버 무당": ShamanStrategy,
    "딥다이브 유튜버": YoutuberStrategy,
    "드림 도굴꾼": TombRaiderStrategy,
}

# =====================================================================
# 4. Player 클래스 (시민 / 사도)
# =====================================================================
@dataclass
class HiddenQuest:
    description: str
    achieved: bool = False
    reward: int = 20

class Player:
    def __init__(self, name: str, role_name: str, is_apostle: bool = False):
        self.name = name
        self.role_name = role_name              # 실제 직업
        self.is_apostle = is_apostle
        self.alive = True
        self.coins = 30
        self.strategy: SpeechStrategy = ROLE_STRATEGIES[role_name]()
        self.disguised_role: Optional[str] = None  # 사도 빙의용
        self.motive: Optional[str] = None          # 사도 동기
        self.hidden_quest: HiddenQuest = HiddenQuest(description="자신의 사익을 3회 진술")
        self.statement_count = 0
        self.self_interest = random.choice(
            ["승진", "복수", "재산", "사랑", "명예", "은닉", "도주"]
        )

    # ---------- 사도 화법 빙의 (Strategy 교체) ----------
    def possess(self, role_cls_name: str):
        if not self.is_apostle:
            return
        if role_cls_name in ROLE_STRATEGIES:
            self.disguised_role = role_cls_name
            self.strategy = ROLE_STRATEGIES[role_cls_name]()

    def displayed_role(self) -> str:
        """다른 플레이어에게 보이는 직업명."""
        if self.is_apostle and self.disguised_role:
            return self.disguised_role
        return self.role_name

    def speak(self, dream: Dream) -> str:
        # 사도는 본인 시점에서 키워드 마스킹된 dream을 본다
        view_role = "악몽의 사도" if self.is_apostle else self.role_name
        line = self.strategy.speak(dream, view_role, self.self_interest)
        self.statement_count += 1
        if self.statement_count >= 3 and not self.hidden_quest.achieved:
            self.hidden_quest.achieved = True
            self.coins += self.hidden_quest.reward
        return f"{self.name} ({self.displayed_role()}): {line}"

# =====================================================================
# 5. EventBus (Observer 풍) + Memento (되감기)
# =====================================================================
class EventBus:
    def __init__(self):
        self.queue: List[str] = []

    def publish(self, event_name: str):
        self.queue.append(event_name)

    def consume(self) -> List[str]:
        out = self.queue[:]
        self.queue.clear()
        return out

class Memento:
    """라운드 스냅샷."""
    def __init__(self, snapshot: Dict):
        self.snapshot = snapshot

# =====================================================================
# 6. GameRound / Game 메인
# =====================================================================
class Game:
    def __init__(self, player_names: List[str], total_rounds: int = 8):
        self.total_rounds = total_rounds
        self.current_round = 1
        self.budget = 1000
        self.initial_budget = 1000
        self.miss_streak = 0   # Bad B용
        self.executed_apostle_count = 0
        self.truth_glass_used_on_apostle = False
        self.event_bus = EventBus()
        self.history: List[str] = []
        self.mementos: List[Memento] = []
        self.ended = False
        self.ending_code: Optional[str] = None
        self.players: List[Player] = self._init_players(player_names)
        self.dream: Dream = Dream(random.choice(KEYWORD_POOL))
        # 사도 빙의: 시민 중 한 직업을 무작위로 흉내
        apostle = next(p for p in self.players if p.is_apostle)
        citizen_roles = [p.role_name for p in self.players if not p.is_apostle]
        apostle.possess(random.choice(citizen_roles))
        apostle.motive = random.choice(list(APOSTLE_MOTIVES.keys()))

    def _init_players(self, names: List[str]) -> List[Player]:
        roles = list(ROLE_STRATEGIES.keys())
        random.shuffle(roles)
        # 사도 1명 + 시민 N-1명
        players: List[Player] = []
        apostle_idx = random.randrange(len(names))
        for i, n in enumerate(names):
            role = roles[i % len(roles)]
            players.append(Player(n, role, is_apostle=(i == apostle_idx)))
        return players

    # ---------- 스냅샷 ----------
    def snapshot(self) -> Memento:
        snap = {
            "round": self.current_round,
            "budget": self.budget,
            "history_len": len(self.history),
            "miss_streak": self.miss_streak,
            "players": [
                (p.name, p.coins, p.alive, p.disguised_role, p.statement_count)
                for p in self.players
            ],
        }
        return Memento(snap)

    def restore(self, m: Memento):
        self.current_round = m.snapshot["round"]
        self.budget = m.snapshot["budget"]
        self.miss_streak = m.snapshot["miss_streak"]
        self.history = self.history[: m.snapshot["history_len"]]
        snap_players = {t[0]: t for t in m.snapshot["players"]}
        for p in self.players:
            if p.name in snap_players:
                _, c, a, d, sc = snap_players[p.name]
                p.coins = c
                p.alive = a
                p.disguised_role = d
                p.statement_count = sc

    # ---------- 진술 페이즈 ----------
    def statement_phase(self) -> List[str]:
        self.mementos.append(self.snapshot())
        lines = [f"=== 🌙 라운드 {self.current_round} 시작 ==="]
        # 이벤트 발동 (라운드 6+)
        if self.current_round >= 6 and random.random() < 0.5:
            ev = random.choice(list(EVENTS.keys()))
            self.event_bus.publish(ev)
            lines.append(f"⚡ 돌발 이벤트: **{ev}** — {EVENTS[ev]}")
            self._apply_event(ev)

        for p in self.players:
            if p.alive:
                lines.append(p.speak(self.dream))
        self.history.extend(lines)
        return lines

    def _apply_event(self, ev: str):
        if ev == "송신탑 노이즈":
            self.dream.add_mask(random.randint(0, 1))
        elif ev == "예산 삭감":
            self.budget = int(self.budget * 0.8)
        elif ev == "집단 악몽":
            self.dream.replace_keyword(
                random.randint(0, 2),
                random.choice(["환영", "잔상", "메아리", "그림자"])
            )

    # ---------- 투표/처형 ----------
    def execute(self, target_name: str) -> str:
        target = next((p for p in self.players if p.name == target_name and p.alive), None)
        if target is None:
            return "대상이 유효하지 않습니다."
        target.alive = False
        if target.is_apostle:
            self.executed_apostle_count += 1
            self.miss_streak = 0
            self.budget += 200
            msg = f"⚖ **{target.name}** 처형 — 사도였습니다! 예산 +200"
        else:
            self.miss_streak += 1
            self.budget -= 150
            msg = f"⚖ **{target.name}** 처형 — 무고한 시민이었습니다… 예산 -150"
        self.history.append(msg)
        return msg

    def skip_execution(self) -> str:
        """후반 처형 실패 누적 (Bad B 트리거)."""
        self.miss_streak += 1
        msg = f"이번 라운드 처형 없음. 미적중 누적: {self.miss_streak}"
        self.history.append(msg)
        return msg

    # ---------- 아이템 사용 ----------
    def use_item(self, buyer_name: str, item: str, target_name: Optional[str] = None) -> str:
        buyer = next((p for p in self.players if p.name == buyer_name), None)
        if buyer is None or not buyer.alive:
            return "구매자 무효."

        costs = {"진실의 안경": 30, "직업 교체권": 50, "역주입": 80,
                 "꿈 되감기": 100, "익명 투서": 20}
        if buyer.coins < costs.get(item, 9999):
            return f"코인 부족! (보유 {buyer.coins} / 필요 {costs.get(item)})"
        buyer.coins -= costs[item]

        if item == "진실의 안경":
            target = next((p for p in self.players if p.name == target_name), None)
            if target is None:
                return "대상이 필요합니다."
            real = target.role_name if not target.is_apostle else "악몽의 사도"
            if target.is_apostle:
                self.truth_glass_used_on_apostle = True
            return f"🔍 진실의 안경: {target.name}의 본명 직업 = **{real}**"
        elif item == "직업 교체권":
            # 두 시민 직업 강제 교환
            citizens = [p for p in self.players if p.alive and not p.is_apostle]
            if len(citizens) < 2:
                return "교환 불가."
            a, b = random.sample(citizens, 2)
            a.role_name, b.role_name = b.role_name, a.role_name
            a.strategy = ROLE_STRATEGIES[a.role_name]()
            b.strategy = ROLE_STRATEGIES[b.role_name]()
            return f"🔁 {a.name}과 {b.name}의 직업이 교환되었습니다."
        elif item == "역주입":
            target = next((p for p in self.players if p.name == target_name), None)
            if target is None:
                return "대상이 필요합니다."
            return f"🧠 역주입: {target.name}의 사익 = **{target.self_interest}**"
        elif item == "꿈 되감기":
            if not self.mementos:
                return "되감을 라운드가 없습니다."
            self.restore(self.mementos.pop())
            return "⏪ 직전 라운드가 무효화되었습니다."
        elif item == "익명 투서":
            non_apostles = [p.name for p in self.players if not p.is_apostle and p.alive]
            if non_apostles:
                return f"📨 익명 투서: 사도가 아닌 자 중 한 명 → **{random.choice(non_apostles)}**"
            return "정보 없음."
        return "알 수 없는 아이템."

    # ---------- 라운드 종료 / 엔딩 판정 ----------
    def advance_round(self):
        self.current_round += 1
        # 매 라운드 모든 생존 플레이어에게 코인 +10
        for p in self.players:
            if p.alive:
                p.coins += 10
        self._check_ending()

    def _check_ending(self):
        if self.budget <= 0:
            self.ended = True
            self.ending_code = "Bad A: 파산한 재판장"
            return
        if self.current_round > self.total_rounds:
            self.ended = True
            # True / Neutral / Secret 판정
            if (self.executed_apostle_count == 0
                    and self.truth_glass_used_on_apostle):
                self.ending_code = "True: 꿈의 해방자"
            elif all(p.hidden_quest.achieved for p in self.players):
                self.ending_code = "Secret: 재귀 재판"
            elif self.budget >= self.initial_budget * 0.5:
                self.ending_code = "Neutral: 체제의 충견"
            else:
                self.ending_code = "Neutral: 체제의 충견 (간신히)"
            return
        if self.current_round >= self.total_rounds - 2 and self.miss_streak >= 3:
            self.ended = True
            self.ending_code = "Bad B: 사도의 그릇"
            return

# =====================================================================
# 7. Streamlit UI
# =====================================================================
def init_state():
    if "game" not in st.session_state:
        st.session_state.game = None
    if "logs" not in st.session_state:
        st.session_state.logs = []

def reset_game(names: List[str], total_rounds: int):
    st.session_state.game = Game(names, total_rounds=total_rounds)
    st.session_state.logs = [
        f"🎮 게임 시작! 플레이어 {len(names)}명, 총 {total_rounds}라운드.",
        "당신은 '재판장'입니다. 사도를 찾아 처형하되, 예산을 지키십시오.",
    ]

def main():
    init_state()
    st.title("🌙 무의식 재판소 — Dream Injector")
    st.caption("2077. 국가가 처방한 꿈을 검열하는 자, 그 자신도 꿈일 수 있다.")

    with st.sidebar:
        st.header("⚙ 게임 설정")
        names_text = st.text_area(
            "플레이어 이름 (줄바꿈 구분, 최소 4명)",
            "도현\n수아\n민재\n예린\n태오",
            height=140,
        )
        total_rounds = st.slider("총 라운드", 5, 12, 8)
        if st.button("🔄 새 게임 시작", use_container_width=True):
            names = [n.strip() for n in names_text.splitlines() if n.strip()]
            if len(names) < 4:
                st.error("최소 4명이 필요합니다.")
            else:
                reset_game(names, total_rounds)
                st.rerun()

    game: Optional[Game] = st.session_state.game
    if game is None:
        st.info("좌측에서 새 게임을 시작하세요.")
        st.markdown("### 🎭 게임 규칙 요약")
        st.markdown("""
- **시민**은 키워드 3개를 모두 알지만, **사익**으로 진술을 왜곡합니다.
- **악몽의 사도**는 키워드 1개(3번째)를 모르며, 다른 직업의 화법을 흉내 냅니다.
- 코인으로 **진실의 안경/직업 교체권/역주입/꿈 되감기/익명 투서**를 살 수 있습니다.
- 예산이 0이면 **Bad A**, 후반 처형 실패가 누적되면 **Bad B**, 사도를 처형하지 않고 안경으로 정체를 밝히면 **True 엔딩** 입니다.
        """)
        return

    # ----- 게임 상태 패널 -----
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("라운드", f"{game.current_round} / {game.total_rounds}")
    col2.metric("재판장 예산", game.budget)
    col3.metric("사도 처형", game.executed_apostle_count)
    col4.metric("미적중 누적", game.miss_streak)

    st.divider()

    # ----- 엔딩 처리 -----
    if game.ended:
        st.success(f"🎬 엔딩: **{game.ending_code}**")
        st.balloons()
        with st.expander("📜 게임 로그 전체 보기", expanded=True):
            for line in game.history:
                st.markdown(line)
        return

    # ----- 액션 영역 -----
    left, right = st.columns([2, 1])

    with left:
        st.subheader("🗣 진술 페이즈")
        if st.button("▶ 이번 라운드 진술 진행", use_container_width=True):
            lines = game.statement_phase()
            st.session_state.logs.extend(lines)

        st.subheader("⚖ 투표/처형 페이즈")
        alive_names = [p.name for p in game.players if p.alive]
        target = st.selectbox("처형 대상 선택", options=["(선택)"] + alive_names)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("처형 집행", use_container_width=True, type="primary"):
                if target != "(선택)":
                    msg = game.execute(target)
                    st.session_state.logs.append(msg)
                    game.advance_round()
                    st.rerun()
                else:
                    st.warning("대상을 선택하세요.")
        with c2:
            if st.button("처형 건너뛰기", use_container_width=True):
                st.session_state.logs.append(game.skip_execution())
                game.advance_round()
                st.rerun()

    with right:
        st.subheader("🪙 아이템 상점")
        buyer = st.selectbox(
            "구매자",
            options=[p.name for p in game.players if p.alive],
            key="buyer_sel",
        )
        item = st.selectbox(
            "아이템",
            ["진실의 안경", "직업 교체권", "역주입", "꿈 되감기", "익명 투서"],
        )
        item_target = None
        if item in ("진실의 안경", "역주입"):
            item_target = st.selectbox(
                "대상", options=[p.name for p in game.players if p.alive],
                key="item_target_sel",
            )
        if st.button("아이템 사용", use_container_width=True):
            msg = game.use_item(buyer, item, item_target)
            st.session_state.logs.append(msg)
            st.rerun()

    st.divider()

    # ----- 플레이어 정보 -----
    st.subheader("👥 등판 인원")
    cols = st.columns(len(game.players))
    for i, p in enumerate(game.players):
        with cols[i]:
            status = "🟢 생존" if p.alive else "💀 사망"
            st.markdown(
                f"**{p.name}**  \n"
                f"표시 직업: *{p.displayed_role()}*  \n"
                f"코인: {p.coins}  \n"
                f"{status}"
            )

    # ----- 로그 -----
    st.subheader("📜 진행 로그")
    log_box = st.container(height=320)
    with log_box:
        for line in st.session_state.logs[-200:]:
            st.markdown(line)

if __name__ == "__main__":
    main()
