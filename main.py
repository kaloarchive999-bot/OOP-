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
