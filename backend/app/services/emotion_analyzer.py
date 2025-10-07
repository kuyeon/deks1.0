"""
강화된 감정 분석 및 반응 시스템
더 세밀하고 다양한 감정 표현
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from loguru import logger
import re


class EmotionCategory(Enum):
    """감정 카테고리"""
    POSITIVE = "positive"  # 긍정적
    NEGATIVE = "negative"  # 부정적
    NEUTRAL = "neutral"    # 중립적
    MIXED = "mixed"        # 복합적


class EmotionIntensity(Enum):
    """감정 강도"""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5


@dataclass
class EmotionState:
    """감정 상태"""
    primary_emotion: str
    secondary_emotion: Optional[str] = None
    category: EmotionCategory = EmotionCategory.NEUTRAL
    intensity: EmotionIntensity = EmotionIntensity.MEDIUM
    sentiment_score: float = 0.0  # -1.0 ~ 1.0
    confidence: float = 0.5
    triggers: List[str] = None  # 감정을 유발한 키워드
    
    def __post_init__(self):
        if self.triggers is None:
            self.triggers = []


@dataclass
class EmotionResponse:
    """감정 기반 응답"""
    emotion_state: EmotionState
    led_expression: str
    buzzer_sound: str
    response_modifier: str  # 응답 스타일 수정자
    animation: Optional[str] = None


class EmotionAnalyzer:
    """강화된 감정 분석기"""
    
    def __init__(self):
        """감정 분석기 초기화"""
        self.emotion_patterns = self._init_emotion_patterns()
        self.emotion_lexicon = self._init_emotion_lexicon()
        self.expression_mapping = self._init_expression_mapping()
        
        logger.info("강화된 감정 분석기 초기화 완료")
    
    def _init_emotion_patterns(self) -> Dict[str, Dict[str, Any]]:
        """감정 패턴 초기화"""
        return {
            # 긍정적 감정
            "joyful": {
                "keywords": ["기쁘", "좋아", "행복", "즐거", "신나", "완전", "최고", "짱"],
                "category": EmotionCategory.POSITIVE,
                "intensity": EmotionIntensity.VERY_HIGH,
                "sentiment_range": (0.7, 1.0)
            },
            "excited": {
                "keywords": ["와", "우와", "대박", "진짜", "멋져", "신기", "놀라"],
                "category": EmotionCategory.POSITIVE,
                "intensity": EmotionIntensity.HIGH,
                "sentiment_range": (0.5, 0.9)
            },
            "happy": {
                "keywords": ["좋아", "괜찮", "감사", "고마워", "만족"],
                "category": EmotionCategory.POSITIVE,
                "intensity": EmotionIntensity.MEDIUM,
                "sentiment_range": (0.3, 0.7)
            },
            "pleased": {
                "keywords": ["그래", "네", "응", "좋아요", "알겠어"],
                "category": EmotionCategory.POSITIVE,
                "intensity": EmotionIntensity.LOW,
                "sentiment_range": (0.1, 0.5)
            },
            
            # 호기심/관심
            "curious": {
                "keywords": ["뭐", "왜", "어떻게", "무슨", "어디", "누구", "언제", "?"],
                "category": EmotionCategory.NEUTRAL,
                "intensity": EmotionIntensity.MEDIUM,
                "sentiment_range": (-0.1, 0.3)
            },
            "interested": {
                "keywords": ["재밌", "흥미", "알고 싶", "궁금", "보고 싶"],
                "category": EmotionCategory.POSITIVE,
                "intensity": EmotionIntensity.MEDIUM,
                "sentiment_range": (0.2, 0.6)
            },
            
            # 부정적 감정
            "sad": {
                "keywords": ["슬프", "우울", "아쉬", "안타", "속상"],
                "category": EmotionCategory.NEGATIVE,
                "intensity": EmotionIntensity.MEDIUM,
                "sentiment_range": (-0.7, -0.3)
            },
            "frustrated": {
                "keywords": ["짜증", "화나", "답답", "귀찮", "싫", "미워"],
                "category": EmotionCategory.NEGATIVE,
                "intensity": EmotionIntensity.HIGH,
                "sentiment_range": (-0.9, -0.5)
            },
            "worried": {
                "keywords": ["걱정", "불안", "무서", "두려", "조심"],
                "category": EmotionCategory.NEGATIVE,
                "intensity": EmotionIntensity.MEDIUM,
                "sentiment_range": (-0.6, -0.2)
            },
            
            # 도움주는 감정
            "helpful": {
                "keywords": ["도와", "도움", "알려줘", "가르쳐", "설명"],
                "category": EmotionCategory.POSITIVE,
                "intensity": EmotionIntensity.MEDIUM,
                "sentiment_range": (0.2, 0.5)
            },
            "supportive": {
                "keywords": ["힘내", "괜찮", "잘할", "응원", "파이팅"],
                "category": EmotionCategory.POSITIVE,
                "intensity": EmotionIntensity.MEDIUM,
                "sentiment_range": (0.3, 0.6)
            },
            
            # 중립/혼란
            "confused": {
                "keywords": ["모르겠", "이해 안", "뭐라고", "헷갈", "애매"],
                "category": EmotionCategory.NEUTRAL,
                "intensity": EmotionIntensity.MEDIUM,
                "sentiment_range": (-0.2, 0.2)
            },
            "neutral": {
                "keywords": ["그냥", "보통", "평범", "그저 그래"],
                "category": EmotionCategory.NEUTRAL,
                "intensity": EmotionIntensity.LOW,
                "sentiment_range": (-0.1, 0.1)
            },
            
            # 자랑스러운
            "proud": {
                "keywords": ["자랑", "뿌듯", "훌륭", "멋진", "대단"],
                "category": EmotionCategory.POSITIVE,
                "intensity": EmotionIntensity.HIGH,
                "sentiment_range": (0.6, 0.9)
            },
            
            # 복합 감정
            "bittersweet": {
                "keywords": ["안녕히", "잘 가", "작별", "헤어", "떠나"],
                "category": EmotionCategory.MIXED,
                "intensity": EmotionIntensity.MEDIUM,
                "sentiment_range": (-0.3, 0.3)
            }
        }
    
    def _init_emotion_lexicon(self) -> Dict[str, float]:
        """감정 어휘 사전 (단어 -> 감정 점수)"""
        return {
            # 매우 긍정적 (+0.8 ~ +1.0)
            "최고": 1.0, "완벽": 1.0, "환상": 0.9, "대박": 0.9,
            "멋져": 0.8, "훌륭": 0.8, "짱": 0.9,
            
            # 긍정적 (+0.4 ~ +0.7)
            "좋아": 0.7, "괜찮": 0.6, "만족": 0.7, "기쁘": 0.7,
            "행복": 0.8, "감사": 0.6, "고마워": 0.6,
            
            # 약간 긍정적 (+0.1 ~ +0.3)
            "그래": 0.2, "네": 0.2, "응": 0.2, "알겠어": 0.2,
            
            # 중립 (-0.1 ~ +0.1)
            "보통": 0.0, "그냥": 0.0, "평범": 0.0,
            
            # 약간 부정적 (-0.3 ~ -0.1)
            "아쉬": -0.2, "별로": -0.2, "글쎄": -0.1,
            
            # 부정적 (-0.7 ~ -0.4)
            "싫어": -0.7, "안 좋": -0.6, "미워": -0.7,
            "슬프": -0.6, "우울": -0.7,
            
            # 매우 부정적 (-1.0 ~ -0.8)
            "최악": -1.0, "끔찍": -0.9, "화나": -0.8,
            "짜증": -0.8, "답답": -0.7
        }
    
    def _init_expression_mapping(self) -> Dict[str, Dict[str, str]]:
        """감정별 표현 매핑"""
        return {
            "joyful": {
                "led": "happy_animated",
                "buzzer": "success_melody",
                "animation": "rainbow"
            },
            "excited": {
                "led": "happy_blink",
                "buzzer": "success",
                "animation": "blink_fast"
            },
            "happy": {
                "led": "happy",
                "buzzer": "success",
                "animation": None
            },
            "pleased": {
                "led": "smile",
                "buzzer": "notification",
                "animation": None
            },
            "curious": {
                "led": "surprised",
                "buzzer": "notification",
                "animation": "question_mark"
            },
            "interested": {
                "led": "focused",
                "buzzer": "info",
                "animation": None
            },
            "sad": {
                "led": "sad",
                "buzzer": "error",
                "animation": "fade"
            },
            "frustrated": {
                "led": "angry",
                "buzzer": "warning",
                "animation": "shake"
            },
            "worried": {
                "led": "concerned",
                "buzzer": "warning",
                "animation": "fade"
            },
            "helpful": {
                "led": "happy",
                "buzzer": "notification",
                "animation": None
            },
            "supportive": {
                "led": "warm",
                "buzzer": "success",
                "animation": "pulse"
            },
            "confused": {
                "led": "neutral",
                "buzzer": "error",
                "animation": "question_mark"
            },
            "neutral": {
                "led": "neutral",
                "buzzer": None,
                "animation": None
            },
            "proud": {
                "led": "proud",
                "buzzer": "success_melody",
                "animation": "sparkle"
            },
            "bittersweet": {
                "led": "sad",
                "buzzer": "farewell",
                "animation": "wave"
            }
        }
    
    def analyze_emotion(
        self,
        text: str,
        intent: Optional[str] = None,
        context_emotions: Optional[List[str]] = None
    ) -> EmotionState:
        """
        감정 분석 (강화된 버전)
        
        Args:
            text: 분석할 텍스트
            intent: 의도 (선택)
            context_emotions: 이전 대화의 감정들 (선택)
        
        Returns:
            EmotionState: 감정 상태
        """
        text_lower = text.lower().strip()
        
        # 1. 패턴 기반 감정 분석
        pattern_emotions = self._analyze_by_patterns(text_lower)
        
        # 2. 어휘 사전 기반 감정 점수 계산
        sentiment_score = self._calculate_sentiment_score(text_lower)
        
        # 3. 의도 기반 감정 보정
        if intent:
            pattern_emotions = self._adjust_emotion_by_intent(pattern_emotions, intent)
        
        # 4. 컨텍스트 기반 감정 보정
        if context_emotions:
            pattern_emotions = self._adjust_emotion_by_context(
                pattern_emotions, context_emotions
            )
        
        # 5. 최종 감정 결정
        if pattern_emotions:
            primary = pattern_emotions[0]
            secondary = pattern_emotions[1] if len(pattern_emotions) > 1 else None
            
            emotion_config = self.emotion_patterns[primary]
            
            return EmotionState(
                primary_emotion=primary,
                secondary_emotion=secondary,
                category=emotion_config["category"],
                intensity=emotion_config["intensity"],
                sentiment_score=sentiment_score,
                confidence=0.8 if len(pattern_emotions) > 0 else 0.5,
                triggers=self._find_emotion_triggers(text_lower, primary)
            )
        else:
            # 기본 감정 (중립)
            return EmotionState(
                primary_emotion="neutral",
                category=EmotionCategory.NEUTRAL,
                intensity=EmotionIntensity.LOW,
                sentiment_score=sentiment_score,
                confidence=0.3
            )
    
    def get_emotion_response(self, emotion_state: EmotionState) -> EmotionResponse:
        """
        감정 상태에 맞는 응답 생성
        
        Args:
            emotion_state: 감정 상태
        
        Returns:
            EmotionResponse: 감정 기반 응답
        """
        emotion = emotion_state.primary_emotion
        
        if emotion in self.expression_mapping:
            mapping = self.expression_mapping[emotion]
            
            # 강도에 따라 애니메이션 조정
            animation = mapping.get("animation")
            if emotion_state.intensity == EmotionIntensity.VERY_HIGH:
                if animation:
                    animation = f"{animation}_intense"
            
            return EmotionResponse(
                emotion_state=emotion_state,
                led_expression=mapping["led"],
                buzzer_sound=mapping["buzzer"] or "none",
                response_modifier=self._get_response_modifier(emotion_state),
                animation=animation
            )
        else:
            # 기본 응답
            return EmotionResponse(
                emotion_state=emotion_state,
                led_expression="neutral",
                buzzer_sound="none",
                response_modifier="neutral"
            )
    
    def _analyze_by_patterns(self, text: str) -> List[str]:
        """패턴 기반 감정 분석"""
        detected_emotions = []
        
        for emotion, config in self.emotion_patterns.items():
            for keyword in config["keywords"]:
                if keyword in text:
                    detected_emotions.append((emotion, config["intensity"].value))
                    break
        
        # 강도 순으로 정렬
        detected_emotions.sort(key=lambda x: x[1], reverse=True)
        
        return [emotion for emotion, _ in detected_emotions]
    
    def _calculate_sentiment_score(self, text: str) -> float:
        """감정 점수 계산 (-1.0 ~ 1.0)"""
        words = re.findall(r'[가-힣]+', text)
        
        if not words:
            return 0.0
        
        total_score = 0.0
        matched_count = 0
        
        for word in words:
            # 부분 매칭으로 어휘 사전 검색
            for lexicon_word, score in self.emotion_lexicon.items():
                if lexicon_word in word:
                    total_score += score
                    matched_count += 1
                    break
        
        if matched_count == 0:
            return 0.0
        
        # 평균 점수 계산 및 정규화
        avg_score = total_score / matched_count
        return max(-1.0, min(1.0, avg_score))
    
    def _adjust_emotion_by_intent(
        self,
        emotions: List[str],
        intent: str
    ) -> List[str]:
        """의도에 따른 감정 보정"""
        intent_emotion_map = {
            "greeting": ["happy", "excited"],
            "introduction": ["excited", "happy"],
            "question_about_robot": ["curious", "helpful"],
            "question_capabilities": ["proud", "excited"],
            "request_help": ["helpful", "supportive"],
            "praise": ["happy", "proud"],
            "compliment": ["joyful", "excited"],
            "farewell": ["bittersweet", "sad"],
            "confused": ["confused", "worried"],
            "robot_move_forward": ["helpful", "excited"],
            "robot_turn": ["helpful", "happy"],
            "robot_stop": ["helpful", "neutral"],
            "robot_spin": ["excited", "joyful"]
        }
        
        # 의도에 맞는 감정이 없으면 추가
        if intent in intent_emotion_map:
            suggested_emotions = intent_emotion_map[intent]
            if not any(e in emotions for e in suggested_emotions):
                emotions = suggested_emotions + emotions
        
        return emotions
    
    def _adjust_emotion_by_context(
        self,
        emotions: List[str],
        context_emotions: List[str]
    ) -> List[str]:
        """이전 대화의 감정을 고려한 보정"""
        # 이전 감정이 부정적이었다면, 긍정적 응답으로 분위기 전환
        negative_emotions = ["sad", "frustrated", "worried"]
        if any(e in context_emotions[-3:] for e in negative_emotions):
            # 긍정적 감정 추가
            if not any(e in emotions for e in ["happy", "supportive", "helpful"]):
                emotions.insert(0, "supportive")
        
        return emotions
    
    def _find_emotion_triggers(self, text: str, emotion: str) -> List[str]:
        """감정을 유발한 키워드 찾기"""
        if emotion not in self.emotion_patterns:
            return []
        
        triggers = []
        keywords = self.emotion_patterns[emotion]["keywords"]
        
        for keyword in keywords:
            if keyword in text:
                triggers.append(keyword)
        
        return triggers
    
    def _get_response_modifier(self, emotion_state: EmotionState) -> str:
        """응답 스타일 수정자"""
        modifiers = {
            "joyful": "cheerful",        # 명랑하게
            "excited": "enthusiastic",   # 열정적으로
            "happy": "friendly",         # 친근하게
            "pleased": "polite",         # 공손하게
            "curious": "inquisitive",    # 호기심 있게
            "interested": "engaged",     # 관심 있게
            "sad": "gentle",             # 부드럽게
            "frustrated": "apologetic",  # 사과하듯
            "worried": "reassuring",     # 안심시키며
            "helpful": "supportive",     # 지원하듯
            "supportive": "encouraging", # 격려하며
            "confused": "understanding", # 이해하며
            "neutral": "calm",           # 침착하게
            "proud": "confident",        # 자신감 있게
            "bittersweet": "warm"        # 따뜻하게
        }
        
        return modifiers.get(emotion_state.primary_emotion, "neutral")
    
    def blend_emotions(
        self,
        user_emotion: EmotionState,
        _robot_current_mood: str
    ) -> EmotionState:
        """
        사용자 감정과 로봇 현재 분위기를 혼합
        
        Args:
            user_emotion: 사용자 감정
            robot_current_mood: 로봇 현재 분위기
        
        Returns:
            혼합된 감정 상태
        """
        # 사용자가 부정적이면 로봇은 긍정적/지지적으로 반응
        if user_emotion.category == EmotionCategory.NEGATIVE:
            return EmotionState(
                primary_emotion="supportive",
                secondary_emotion=user_emotion.primary_emotion,
                category=EmotionCategory.POSITIVE,
                intensity=EmotionIntensity.MEDIUM,
                sentiment_score=0.5,
                confidence=0.8
            )
        
        # 사용자가 매우 긍정적이면 로봇도 같이 기뻐함
        if user_emotion.intensity == EmotionIntensity.VERY_HIGH:
            return EmotionState(
                primary_emotion="excited",
                category=EmotionCategory.POSITIVE,
                intensity=EmotionIntensity.HIGH,
                sentiment_score=0.8,
                confidence=0.9
            )
        
        # 기본적으로 사용자 감정에 맞춤
        return user_emotion


# 전역 감정 분석기 인스턴스
_emotion_analyzer: Optional[EmotionAnalyzer] = None


def get_emotion_analyzer() -> EmotionAnalyzer:
    """감정 분석기 싱글톤 인스턴스"""
    global _emotion_analyzer
    if _emotion_analyzer is None:
        _emotion_analyzer = EmotionAnalyzer()
    return _emotion_analyzer

