"""
채팅용 자연어 처리 모듈

이 모듈은 채팅 상호작용을 위한 고급 NLP 기능을 제공합니다:
- 의도 분류 (Intent Classification)
- 개체명 인식 (Named Entity Recognition)
- 감정 분석 (Sentiment Analysis)
- 키워드 추출 (Keyword Extraction)
- 문장 유사도 계산 (Sentence Similarity)
"""

import re
import logging
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from collections import Counter

logger = logging.getLogger(__name__)

class IntentType(Enum):
    """의도 타입 열거형"""
    GREETING = "greeting"
    INTRODUCTION = "introduction"
    QUESTION_ABOUT_ROBOT = "question_about_robot"
    QUESTION_CAPABILITIES = "question_capabilities"
    REQUEST_HELP = "request_help"
    PRAISE = "praise"
    COMPLIMENT = "compliment"
    FAREWELL = "farewell"
    CONFUSED = "confused"
    UNKNOWN = "unknown"

class EmotionType(Enum):
    """감정 타입 열거형"""
    HAPPY = "happy"
    EXCITED = "excited"
    CURIOUS = "curious"
    PROUD = "proud"
    HELPFUL = "helpful"
    CONFUSED = "confused"
    SAD = "sad"
    NEUTRAL = "neutral"
    BITTERSWEET = "bittersweet"

@dataclass
class IntentResult:
    """의도 분석 결과"""
    intent: IntentType
    confidence: float
    keywords: List[str]
    entities: Dict[str, Any]

@dataclass
class EmotionResult:
    """감정 분석 결과"""
    emotion: EmotionType
    confidence: float
    sentiment_score: float  # -1.0 (부정) ~ 1.0 (긍정)
    keywords: List[str]

@dataclass
class NLPAnalysis:
    """NLP 분석 결과"""
    intent: IntentResult
    emotion: EmotionResult
    keywords: List[str]
    entities: Dict[str, Any]
    similarity_scores: Dict[str, float]

class ChatNLP:
    """채팅용 자연어 처리 클래스"""
    
    def __init__(self):
        """NLP 모듈 초기화"""
        self.intent_patterns = self._init_intent_patterns()
        self.emotion_patterns = self._init_emotion_patterns()
        self.entity_patterns = self._init_entity_patterns()
        self.similarity_cache = {}
        
        logger.info("채팅 NLP 모듈 초기화 완료")
    
    def _init_intent_patterns(self) -> Dict[IntentType, Dict[str, Any]]:
        """의도 패턴 초기화"""
        return {
            IntentType.GREETING: {
                "keywords": ["안녕", "하이", "헬로", "좋은 아침", "좋은 저녁", "인사"],
                "patterns": [
                    r"안녕.*",
                    r"하이.*",
                    r"헬로.*",
                    r"좋은\s+(아침|저녁).*"
                ],
                "weight": 1.0
            },
            IntentType.INTRODUCTION: {
                "keywords": ["나는", "내 이름은", "저는", "내가"],
                "patterns": [
                    r"나는\s+([가-힣]+).*",
                    r"내\s+이름은\s+([가-힣]+).*",
                    r"저는\s+([가-힣]+).*",
                    r"내가\s+([가-힣]+).*"
                ],
                "weight": 1.0
            },
            IntentType.QUESTION_ABOUT_ROBOT: {
                "keywords": ["넌 뭐야", "너는 누구", "뭐하는", "할 수 있는", "뭐야", "누구야"],
                "patterns": [
                    r".*넌\s+뭐야.*",
                    r".*너는\s+누구.*",
                    r".*뭐하는.*",
                    r".*할\s+수\s+있는.*"
                ],
                "weight": 1.0
            },
            IntentType.QUESTION_CAPABILITIES: {
                "keywords": ["할 수", "능력", "기능", "뭐 해", "어떻게"],
                "patterns": [
                    r".*할\s+수.*",
                    r".*능력.*",
                    r".*기능.*",
                    r".*어떻게.*"
                ],
                "weight": 1.0
            },
            IntentType.REQUEST_HELP: {
                "keywords": ["도와", "도움", "어떻게 해야", "방법", "알려", "가르쳐"],
                "patterns": [
                    r".*도와.*",
                    r".*도움.*",
                    r".*어떻게\s+해야.*",
                    r".*방법.*"
                ],
                "weight": 1.0
            },
            IntentType.PRAISE: {
                "keywords": ["잘했", "좋았", "멋있", "훌륭", "대단", "최고"],
                "patterns": [
                    r".*잘했.*",
                    r".*좋았.*",
                    r".*멋있.*",
                    r".*훌륭.*"
                ],
                "weight": 1.0
            },
            IntentType.COMPLIMENT: {
                "keywords": ["좋아", "멋져", "고마워", "감사", "대단", "훌륭"],
                "patterns": [
                    r".*좋아.*",
                    r".*멋져.*",
                    r".*고마워.*",
                    r".*감사.*"
                ],
                "weight": 1.0
            },
            IntentType.FAREWELL: {
                "keywords": ["안녕히 가", "잘 가", "또 봐", "바이", "bye", "굿바이"],
                "patterns": [
                    r".*안녕히\s+가.*",
                    r".*잘\s+가.*",
                    r".*또\s+봐.*",
                    r".*바이.*"
                ],
                "weight": 1.0
            },
            IntentType.CONFUSED: {
                "keywords": ["모르겠", "이해 안", "뭐라고", "잘 모르", "뭔 소리", "이해 못해"],
                "patterns": [
                    r".*모르겠.*",
                    r".*이해\s+안.*",
                    r".*뭐라고.*",
                    r".*잘\s+모르.*"
                ],
                "weight": 1.0
            }
        }
    
    def _init_emotion_patterns(self) -> Dict[EmotionType, Dict[str, Any]]:
        """감정 패턴 초기화"""
        return {
            EmotionType.HAPPY: {
                "keywords": ["좋아", "기뻐", "행복", "즐거", "웃음", "ㅋㅋ", "ㅎㅎ"],
                "weight": 1.0,
                "sentiment": 0.8
            },
            EmotionType.EXCITED: {
                "keywords": ["신나", "기대", "설레", "와", "대박", "멋져"],
                "weight": 1.0,
                "sentiment": 0.9
            },
            EmotionType.CURIOUS: {
                "keywords": ["궁금", "어떻게", "뭐야", "왜", "언제", "어디"],
                "weight": 1.0,
                "sentiment": 0.2
            },
            EmotionType.PROUD: {
                "keywords": ["자랑", "대단", "훌륭", "잘했", "최고", "멋있"],
                "weight": 1.0,
                "sentiment": 0.9
            },
            EmotionType.HELPFUL: {
                "keywords": ["도와", "도움", "알려", "가르쳐", "설명"],
                "weight": 1.0,
                "sentiment": 0.6
            },
            EmotionType.CONFUSED: {
                "keywords": ["모르겠", "이해 안", "혼란", "어려워", "복잡"],
                "weight": 1.0,
                "sentiment": -0.3
            },
            EmotionType.SAD: {
                "keywords": ["슬퍼", "우울", "힘들", "아쉬워", "속상"],
                "weight": 1.0,
                "sentiment": -0.8
            },
            EmotionType.BITTERSWEET: {
                "keywords": ["안녕히", "작별", "이별", "아쉬워", "그리워"],
                "weight": 1.0,
                "sentiment": -0.2
            }
        }
    
    def _init_entity_patterns(self) -> Dict[str, List[str]]:
        """개체명 패턴 초기화"""
        return {
            "PERSON": [
                r"([가-힣]{2,10})\s*님",
                r"([가-힣]{2,10})\s*씨",
                r"나는\s+([가-힣]{2,10})",
                r"내\s+이름은\s+([가-힣]{2,10})",
                r"저는\s+([가-힣]{2,10})"
            ],
            "ROBOT": [
                r"로봇",
                r"덱스",
                r"기계",
                r"AI"
            ],
            "ACTION": [
                r"이동",
                r"움직",
                r"가다",
                r"오다",
                r"돌다",
                r"멈추"
            ],
            "OBJECT": [
                r"센서",
                r"카메라",
                r"바퀴",
                r"모터",
                r"LED"
            ]
        }
    
    def analyze_text(self, text: str) -> NLPAnalysis:
        """텍스트에 대한 종합적인 NLP 분석 수행"""
        try:
            # 의도 분석
            intent_result = self._analyze_intent(text)
            
            # 감정 분석
            emotion_result = self._analyze_emotion(text)
            
            # 키워드 추출
            keywords = self._extract_keywords(text)
            
            # 개체명 인식
            entities = self._extract_entities(text)
            
            # 유사도 계산
            similarity_scores = self._calculate_similarity(text)
            
            return NLPAnalysis(
                intent=intent_result,
                emotion=emotion_result,
                keywords=keywords,
                entities=entities,
                similarity_scores=similarity_scores
            )
            
        except Exception as e:
            logger.error("NLP 분석 실패: %s", e)
            # 기본값 반환
            return NLPAnalysis(
                intent=IntentResult(IntentType.UNKNOWN, 0.0, [], {}),
                emotion=EmotionResult(EmotionType.NEUTRAL, 0.0, 0.0, []),
                keywords=[],
                entities={},
                similarity_scores={}
            )
    
    def _analyze_intent(self, text: str) -> IntentResult:
        """의도 분석"""
        text_lower = text.lower().strip()
        best_intent = IntentType.UNKNOWN
        best_confidence = 0.0
        matched_keywords = []
        entities = {}
        
        for intent_type, pattern_data in self.intent_patterns.items():
            confidence = 0.0
            intent_keywords = []
            
            # 키워드 매칭
            for keyword in pattern_data["keywords"]:
                if keyword.lower() in text_lower:
                    confidence += 0.3
                    intent_keywords.append(keyword)
            
            # 패턴 매칭
            for pattern in pattern_data["patterns"]:
                match = re.search(pattern, text_lower)
                if match:
                    confidence += 0.5
                    # 개체명 추출
                    if match.groups():
                        entities[intent_type.value] = match.groups()
            
            # 가중치 적용
            confidence *= pattern_data["weight"]
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_intent = intent_type
                matched_keywords = intent_keywords
        
        # 신뢰도 정규화 (0.0 ~ 1.0)
        best_confidence = min(best_confidence, 1.0)
        
        return IntentResult(
            intent=best_intent,
            confidence=best_confidence,
            keywords=matched_keywords,
            entities=entities
        )
    
    def _analyze_emotion(self, text: str) -> EmotionResult:
        """감정 분석"""
        text_lower = text.lower().strip()
        best_emotion = EmotionType.NEUTRAL
        best_confidence = 0.0
        sentiment_score = 0.0
        matched_keywords = []
        
        for emotion_type, pattern_data in self.emotion_patterns.items():
            confidence = 0.0
            emotion_keywords = []
            
            # 키워드 매칭
            for keyword in pattern_data["keywords"]:
                if keyword.lower() in text_lower:
                    confidence += 0.4
                    emotion_keywords.append(keyword)
                    sentiment_score += pattern_data["sentiment"]
            
            # 가중치 적용
            confidence *= pattern_data["weight"]
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_emotion = emotion_type
                matched_keywords = emotion_keywords
        
        # 신뢰도 정규화
        best_confidence = min(best_confidence, 1.0)
        
        # 감정 점수 정규화 (-1.0 ~ 1.0)
        sentiment_score = max(-1.0, min(1.0, sentiment_score / max(len(matched_keywords), 1)))
        
        return EmotionResult(
            emotion=best_emotion,
            confidence=best_confidence,
            sentiment_score=sentiment_score,
            keywords=matched_keywords
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        # 간단한 키워드 추출 (실제로는 더 정교한 방법 사용 가능)
        words = re.findall(r'[가-힣a-zA-Z]+', text.lower())
        
        # 불용어 제거
        stopwords = {"은", "는", "이", "가", "을", "를", "에", "의", "로", "으로", "와", "과", "도", "만", "부터", "까지"}
        keywords = [word for word in words if word not in stopwords and len(word) > 1]
        
        # 빈도 기반 키워드 선택
        word_freq = Counter(keywords)
        return [word for word, freq in word_freq.most_common(5)]
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """개체명 인식"""
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            entity_values = []
            for pattern in patterns:
                matches = re.findall(pattern, text)
                entity_values.extend(matches)
            
            if entity_values:
                entities[entity_type] = list(set(entity_values))  # 중복 제거
        
        return entities
    
    def _calculate_similarity(self, text: str) -> Dict[str, float]:
        """문장 유사도 계산 (간단한 버전)"""
        # 실제로는 더 정교한 유사도 계산 방법 사용 가능
        # 여기서는 키워드 기반 유사도 계산
        text_keywords = set(self._extract_keywords(text))
        similarity_scores = {}
        
        # 각 의도와의 유사도 계산
        for intent_type, pattern_data in self.intent_patterns.items():
            intent_keywords = set(pattern_data["keywords"])
            if text_keywords and intent_keywords:
                intersection = text_keywords.intersection(intent_keywords)
                union = text_keywords.union(intent_keywords)
                similarity = len(intersection) / len(union) if union else 0.0
                similarity_scores[intent_type.value] = similarity
        
        return similarity_scores
    
    def get_intent_suggestions(self, text: str, top_k: int = 3) -> List[Tuple[IntentType, float]]:
        """의도 제안 (상위 K개)"""
        analysis = self.analyze_text(text)
        suggestions = []
        
        # 모든 의도에 대한 유사도 계산
        for intent_type in IntentType:
            if intent_type != IntentType.UNKNOWN:
                similarity = analysis.similarity_scores.get(intent_type.value, 0.0)
                suggestions.append((intent_type, similarity))
        
        # 유사도 순으로 정렬하여 상위 K개 반환
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:top_k]
    
    def get_emotion_trend(self, texts: List[str]) -> Dict[str, float]:
        """감정 트렌드 분석"""
        emotions = []
        sentiments = []
        
        for text in texts:
            analysis = self.analyze_text(text)
            emotions.append(analysis.emotion.emotion.value)
            sentiments.append(analysis.emotion.sentiment_score)
        
        # 감정 분포 계산
        emotion_counts = Counter(emotions)
        total = len(emotions)
        emotion_distribution = {emotion: count/total for emotion, count in emotion_counts.items()}
        
        # 평균 감정 점수
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
        
        return {
            "emotion_distribution": emotion_distribution,
            "average_sentiment": avg_sentiment,
            "total_messages": total
        }
    
    def is_question(self, text: str) -> bool:
        """질문인지 판단"""
        question_patterns = [
            r".*\?$",
            r".*뭐야.*",
            r".*뭐.*",
            r".*어떻게.*",
            r".*왜.*",
            r".*언제.*",
            r".*어디.*",
            r".*누구.*"
        ]
        
        text_lower = text.lower().strip()
        for pattern in question_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def extract_question_type(self, text: str) -> str:
        """질문 유형 추출"""
        if not self.is_question(text):
            return "not_question"
        
        text_lower = text.lower().strip()
        
        if re.search(r".*뭐야.*|.*뭐.*", text_lower):
            return "what"
        elif re.search(r".*어떻게.*", text_lower):
            return "how"
        elif re.search(r".*왜.*", text_lower):
            return "why"
        elif re.search(r".*언제.*", text_lower):
            return "when"
        elif re.search(r".*어디.*", text_lower):
            return "where"
        elif re.search(r".*누구.*", text_lower):
            return "who"
        else:
            return "general"
