"""
채팅 상호작용 서비스
"""

import uuid
import random
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from loguru import logger

from app.database.database_manager import db_manager
from app.services.chat_nlp import ChatNLP, IntentType, EmotionType


class ChatService:
    """채팅 상호작용 서비스 클래스"""
    
    def __init__(self):
        self.conversation_patterns = self._init_conversation_patterns()
        self.emotion_states = self._init_emotion_states()
        try:
            self.nlp = ChatNLP()  # NLP 모듈 초기화
            logger.info("NLP 모듈 초기화 성공")
        except Exception as e:
            logger.error("NLP 모듈 초기화 실패: %s", e)
            self.nlp = None
    
    def _init_conversation_patterns(self) -> Dict[str, Dict[str, Any]]:
        """대화 패턴 초기화"""
        return {
            "greeting": {
                "keywords": ["안녕", "하이", "헬로", "덱스", "hello", "hi"],
                "responses": [
                    "안녕하세요! 저는 덱스에요. 당신은 누구신가요?",
                    "안녕하세요! 만나서 반가워요. 저는 덱스라고 해요.",
                    "안녕하세요! 저는 덱스 로봇이에요. 오늘은 어떤 도움이 필요하신가요?"
                ],
                "emotion": "happy",
                "led_expression": "happy",
                "buzzer_sound": "greeting"
            },
            "introduction": {
                "keywords": ["나는", "내 이름은", "저는", "내가"],
                "responses": [
                    "안녕하세요 {user_name}님! 만나서 반가워요. 저는 덱스라고 해요.",
                    "반가워요 {user_name}님! 저는 덱스라는 로봇이에요.",
                    "안녕하세요 {user_name}님! 저는 덱스예요. 앞으로 잘 부탁드려요!"
                ],
                "emotion": "excited",
                "led_expression": "happy",
                "buzzer_sound": "success"
            },
            "question_about_robot": {
                "keywords": ["넌 뭐야", "너는 누구", "뭐하는", "할 수 있는", "뭐야", "누구야"],
                "responses": [
                    "저는 덱스라는 로봇이에요! 이동하고 센서로 주변을 감지할 수 있어요.",
                    "저는 로봇 덱스예요. 앞으로 가달라고 하시면 이동할 수 있어요.",
                    "저는 덱스 로봇이에요. 움직이고 주변을 탐지하는 것이 제 특기예요."
                ],
                "emotion": "curious",
                "led_expression": "surprised",
                "buzzer_sound": "notification"
            },
            "question_capabilities": {
                "keywords": ["할 수", "능력", "기능", "뭐 해", "어떻게"],
                "responses": [
                    "앞으로 가달라고 하시면 이동할 수 있어요. 한번 해보실래요?",
                    "저는 이동하고 센서로 주변을 감지할 수 있어요. 명령을 내려보세요!",
                    "저는 움직일 수 있고 주변을 탐지할 수 있어요. 무엇을 도와드릴까요?"
                ],
                "emotion": "excited",
                "led_expression": "happy",
                "buzzer_sound": "success"
            },
            "farewell": {
                "keywords": ["안녕히 가", "잘 가", "또 봐", "바이", "bye", "굿바이", "잘 있어", "나중에 봐", "다음에 봐", "또 만나", "작별"],
                "responses": [
                    "안녕히 가세요 {user_name}님! 또 만나요. 좋은 하루 되세요!",
                    "안녕히 가세요! 언제든지 다시 찾아주세요.",
                    "좋은 하루 보내세요! 또 봐요 {user_name}님."
                ],
                "emotion": "bittersweet",
                "led_expression": "sad",
                "buzzer_sound": "farewell"
            },
            "compliment": {
                "keywords": ["좋아", "멋져", "고마워", "감사", "대단", "훌륭", "멋진", "와", "와!"],
                "responses": [
                    "고마워요! 더 열심히 도와드릴게요!",
                    "정말 기뻐요! 언제든지 도와드릴게요.",
                    "감사해요! 저도 정말 좋아요!"
                ],
                "emotion": "happy",
                "led_expression": "happy",
                "buzzer_sound": "success"
            },
            "confused": {
                "keywords": ["모르겠", "이해 안", "뭐라고", "잘 모르", "뭔 소리", "이해 못해", "뭔가", "음", "이해가 안"],
                "responses": [
                    "죄송해요. 다시 말씀해 주실 수 있나요?",
                    "이해하지 못했어요. 다른 방법으로 설명해 주세요.",
                    "무엇을 도와드릴까요? 명확히 말씀해 주세요."
                ],
                "emotion": "confused",
                "led_expression": "neutral",
                "buzzer_sound": "error"
            },
            "request_help": {
                "keywords": ["도와", "도움", "어떻게 해야", "방법", "알려", "가르쳐", "어떻게 해야 해", "움직일", "움직이"],
                "responses": [
                    "무엇을 도와드릴까요? 구체적으로 말씀해 주세요.",
                    "저는 로봇 제어를 도와드릴 수 있어요. 어떤 도움이 필요하신가요?",
                    "앞으로 가달라고 하시면 이동할 수 있어요. 명령을 내려보세요!"
                ],
                "emotion": "helpful",
                "led_expression": "happy",
                "buzzer_sound": "notification"
            },
            "praise": {
                "keywords": ["잘했", "좋았", "멋있", "훌륭", "대단", "최고", "멋진", "와", "와!"],
                "responses": [
                    "고마워요! 정말 기뻐요!",
                    "칭찬해 주셔서 감사해요. 더 열심히 할게요!",
                    "정말 좋아요! 언제든지 도와드릴게요."
                ],
                "emotion": "excited",
                "led_expression": "happy",
                "buzzer_sound": "success"
            }
        }
    
    def _init_emotion_states(self) -> Dict[str, Dict[str, str]]:
        """감정 상태 초기화"""
        return {
            "happy": {
                "led_expression": "happy",
                "buzzer_sound": "success",
                "response_style": "cheerful"
            },
            "excited": {
                "led_expression": "happy",
                "buzzer_sound": "success",
                "response_style": "enthusiastic"
            },
            "curious": {
                "led_expression": "surprised",
                "buzzer_sound": "notification",
                "response_style": "inquisitive"
            },
            "confused": {
                "led_expression": "neutral",
                "buzzer_sound": "error",
                "response_style": "helpful"
            },
            "sad": {
                "led_expression": "sad",
                "buzzer_sound": "error",
                "response_style": "gentle"
            },
            "proud": {
                "led_expression": "happy",
                "buzzer_sound": "success",
                "response_style": "confident"
            },
            "bittersweet": {
                "led_expression": "sad",
                "buzzer_sound": "farewell",
                "response_style": "warm"
            },
            "helpful": {
                "led_expression": "happy",
                "buzzer_sound": "notification",
                "response_style": "supportive"
            }
        }
    
    async def process_message(self, message: str, user_id: str, session_id: str) -> Dict[str, Any]:
        """
        메시지를 처리하고 응답을 생성합니다.
        
        Args:
            message: 사용자 메시지
            user_id: 사용자 ID
            session_id: 세션 ID
            
        Returns:
            Dict: 응답 데이터
        """
        try:
            # 메시지 ID 생성
            message_id = str(uuid.uuid4())
            
            # NLP 분석 수행
            if self.nlp:
                try:
                    nlp_analysis = self.nlp.analyze_text(message)
                    # 기존 패턴 기반 분석과 NLP 분석 결과 결합
                    intent = self._combine_intent_analysis(message, nlp_analysis)
                    emotion = self._combine_emotion_analysis(message, intent, nlp_analysis)
                except Exception as e:
                    logger.error("NLP 분석 실패, 기본 분석 사용: %s", e)
                    intent = self._analyze_intent(message)
                    emotion = self._analyze_emotion(message, intent)
                    nlp_analysis = None
            else:
                # NLP 모듈이 없으면 기존 방식 사용
                intent = self._analyze_intent(message)
                emotion = self._analyze_emotion(message, intent)
                nlp_analysis = None
            
            # 컨텍스트 조회
            context = await self.get_chat_context(user_id, session_id)
            
            # 응답 생성
            response = self._generate_response(message, intent, emotion, context)
            
            # 대화 기록 저장
            await self._save_conversation(
                message_id=message_id,
                user_id=user_id,
                session_id=session_id,
                user_message=message,
                robot_response=response["text"],
                emotion_detected=emotion,
                emotion_responded=response["emotion"],
                conversation_type=intent
            )
            
            # 컨텍스트 업데이트
            await self._update_context(user_id, session_id, intent, response)
            
            result = {
                "message_id": message_id,
                "response": response["text"],
                "emotion": response["emotion"],
                "conversation_type": intent,
                "timestamp": datetime.now().isoformat(),
                "context": {
                    "user_name": context.get("user_name"),
                    "robot_mood": response["emotion"],
                    "follow_up": response.get("follow_up")
                }
            }
            
            # NLP 분석 데이터가 있으면 추가
            if nlp_analysis and self.nlp:
                result["nlp_analysis"] = {
                    "intent_confidence": nlp_analysis.intent.confidence,
                    "emotion_confidence": nlp_analysis.emotion.confidence,
                    "sentiment_score": nlp_analysis.emotion.sentiment_score,
                    "keywords": nlp_analysis.keywords,
                    "entities": nlp_analysis.entities,
                    "is_question": self.nlp.is_question(message),
                    "question_type": self.nlp.extract_question_type(message)
                }
            
            return result
            
        except Exception as e:
            logger.error(f"메시지 처리 실패: {e}")
            raise
    
    def _analyze_intent(self, message: str) -> str:
        """메시지의 의도를 분석합니다."""
        message_lower = message.lower().strip()
        
        # 우선순위 기반 의도 분석 (더 구체적인 패턴을 먼저 확인)
        priority_intents = [
            "farewell",      # 작별 인사 (우선순위 높음)
            "introduction",  # 자기소개
            "request_help",  # 도움 요청 (우선순위 높임)
            "question_about_robot",  # 로봇에 대한 질문
            "question_capabilities", # 능력에 대한 질문
            "praise",        # 칭찬
            "compliment",    # 칭찬 (일반)
            "confused",      # 혼란
            "greeting"       # 인사 (우선순위 낮음)
        ]
        
        # 우선순위 순서대로 의도 확인
        for intent in priority_intents:
            if intent in self.conversation_patterns:
                pattern_data = self.conversation_patterns[intent]
                for keyword in pattern_data["keywords"]:
                    # 정확한 키워드 매칭 (부분 매칭보다 정확한 매칭 우선)
                    if keyword.lower() == message_lower:
                        return intent
                    # 부분 매칭
                    elif keyword.lower() in message_lower:
                        return intent
        
        return "unknown"
    
    def _analyze_emotion(self, message: str, intent: str) -> str:
        """메시지의 감정을 분석합니다."""
        # 의도에 따른 기본 감정
        if intent in self.conversation_patterns:
            return self.conversation_patterns[intent]["emotion"]
        
        # 키워드 기반 감정 분석
        positive_keywords = ["좋아", "멋져", "고마워", "감사", "대단", "훌륭"]
        negative_keywords = ["싫어", "나빠", "화나", "짜증"]
        
        message_lower = message.lower()
        
        for keyword in positive_keywords:
            if keyword in message_lower:
                return "happy"
        
        for keyword in negative_keywords:
            if keyword in message_lower:
                return "sad"
        
        return "neutral"
    
    def _generate_response(self, message: str, intent: str, emotion: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """응답을 생성합니다."""
        user_name = context.get("user_name")
        
        if intent in self.conversation_patterns:
            pattern = self.conversation_patterns[intent]
            responses = pattern["responses"]
            
            # 랜덤 응답 선택
            response_text = random.choice(responses)
            
            # 사용자 이름 치환 (자기소개가 아닌 경우에만)
            if user_name and "{user_name}" in response_text and intent != "introduction":
                response_text = response_text.format(user_name=user_name)
            
            # 이름 추출 및 치환 (자기소개인 경우)
            if intent == "introduction":
                extracted_name = self._extract_name(message)
                if extracted_name:
                    # 기존 사용자 이름이 없거나 추출된 이름이 더 구체적일 때 업데이트
                    if not user_name or len(extracted_name) > 1:
                        user_name = extracted_name
                    # 모든 {user_name} 치환
                    response_text = response_text.replace("{user_name}", extracted_name)
                elif user_name:
                    response_text = response_text.replace("{user_name}", user_name)
                else:
                    # 이름이 없으면 기본값 사용
                    response_text = response_text.replace("{user_name}", "")
            
            # 다른 의도에서도 {user_name} 치환 처리
            if "{user_name}" in response_text:
                if user_name:
                    response_text = response_text.replace("{user_name}", user_name)
                else:
                    response_text = response_text.replace("{user_name}", "")
            
            return {
                "text": response_text,
                "emotion": pattern["emotion"],
                "led_expression": pattern["led_expression"],
                "buzzer_sound": pattern["buzzer_sound"],
                "follow_up": self._generate_follow_up(intent)
            }
        
        # 알 수 없는 의도
        return {
            "text": "죄송해요. 이해하지 못했어요. 다시 말씀해 주실 수 있나요?",
            "emotion": "confused",
            "led_expression": "neutral",
            "buzzer_sound": "error"
        }
    
    def _extract_name(self, message: str) -> Optional[str]:
        """메시지에서 이름을 추출합니다."""
        # 다양한 자기소개 패턴 매칭 (더 정확한 정규표현식)
        patterns = [
            # "나는 김철수야" 형태
            r"나는\s+([가-힣]{2,10})\s*야",
            # "내 이름은 김철수야" 형태  
            r"내\s+이름은\s+([가-힣]{2,10})\s*야",
            # "내 이름은 김철수입니다" 형태 (정확한 매칭)
            r"내\s+이름은\s+([가-힣]{2,10})입니다",
            # "내 이름은 김철수" 형태 (끝에 공백이나 구두점)
            r"내\s+이름은\s+([가-힣]{2,10})(?:\s|$)",
            # "저는 김철수입니다" 형태
            r"저는\s+([가-힣]{2,10})입니다",
            # "저는 김철수야" 형태
            r"저는\s+([가-힣]{2,10})\s*야",
            # "저는 김철수" 형태 (끝에 공백이나 구두점) - 가장 중요!
            r"저는\s+([가-힣]{2,10})(?:\s|$)",
            # "내가 김철수야" 형태
            r"내가\s+([가-힣]{2,10})\s*야",
            # "내가 김철수" 형태
            r"내가\s+([가-힣]{2,10})(?:\s|$)",
            # "김철수야" 형태 (단독)
            r"^([가-힣]{2,10})\s*야$",
            # "김철수입니다" 형태 (단독)
            r"^([가-힣]{2,10})\s*입니다$"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                name = match.group(1)
                # 일반적인 단어가 아닌 실제 이름인지 확인
                common_words = {"덱스", "로봇", "친구", "사람", "이름", "내", "저", "나"}
                if name not in common_words:
                    return name
        
        return None
    
    def _generate_follow_up(self, intent: str) -> Optional[str]:
        """후속 질문을 생성합니다."""
        follow_ups = {
            "greeting": "오늘은 어떤 도움이 필요하신가요?",
            "introduction": "저는 로봇이에요. 이동하고 센서로 주변을 감지할 수 있어요.",
            "question_about_robot": "앞으로 가달라고 하시면 이동할 수 있어요. 한번 해보실래요?",
            "question_capabilities": "무엇을 도와드릴까요?",
            "request_help": "구체적으로 어떤 도움이 필요하신가요?",
            "praise": "언제든지 도와드릴게요!",
            "compliment": "언제든지 도와드릴게요!",
            "farewell": None,  # 작별 인사에는 후속 질문 없음
            "confused": "다시 한번 말씀해 주실 수 있나요?"
        }
        
        return follow_ups.get(intent)
    
    def _combine_intent_analysis(self, message: str, nlp_analysis) -> str:
        """기존 패턴 기반 분석과 NLP 분석 결과를 결합합니다."""
        # NLP 분석 결과를 우선으로 하되, 신뢰도가 낮으면 기존 패턴 사용
        if nlp_analysis.intent.confidence > 0.7:
            # NLP 결과를 문자열로 변환
            intent_mapping = {
                IntentType.GREETING: "greeting",
                IntentType.INTRODUCTION: "introduction", 
                IntentType.QUESTION_ABOUT_ROBOT: "question_about_robot",
                IntentType.QUESTION_CAPABILITIES: "question_capabilities",
                IntentType.REQUEST_HELP: "request_help",
                IntentType.PRAISE: "praise",
                IntentType.COMPLIMENT: "compliment",
                IntentType.FAREWELL: "farewell",
                IntentType.CONFUSED: "confused",
                IntentType.UNKNOWN: "unknown"
            }
            return intent_mapping.get(nlp_analysis.intent.intent, "unknown")
        else:
            # 기존 패턴 기반 분석 사용
            return self._analyze_intent(message)
    
    def _combine_emotion_analysis(self, message: str, intent: str, nlp_analysis) -> str:
        """기존 패턴 기반 분석과 NLP 분석 결과를 결합합니다."""
        # NLP 분석 결과를 우선으로 하되, 신뢰도가 낮으면 기존 패턴 사용
        if nlp_analysis.emotion.confidence > 0.6:
            # NLP 결과를 문자열로 변환
            emotion_mapping = {
                EmotionType.HAPPY: "happy",
                EmotionType.EXCITED: "excited",
                EmotionType.CURIOUS: "curious", 
                EmotionType.PROUD: "proud",
                EmotionType.HELPFUL: "helpful",
                EmotionType.CONFUSED: "confused",
                EmotionType.SAD: "sad",
                EmotionType.NEUTRAL: "neutral",
                EmotionType.BITTERSWEET: "bittersweet"
            }
            return emotion_mapping.get(nlp_analysis.emotion.emotion, "neutral")
        else:
            # 기존 패턴 기반 분석 사용
            return self._analyze_emotion(message, intent)
    
    async def get_chat_history(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """채팅 기록을 조회합니다."""
        try:
            # 데이터베이스에서 채팅 기록 조회
            query = """
            SELECT message_id, user_message, robot_response, emotion_detected, 
                   emotion_responded, conversation_type, timestamp
            FROM chat_messages 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
            """
            
            results = db_manager.execute_query(query, (user_id, limit, offset))
            
            conversations = []
            for row in results:
                conversations.append({
                    "message_id": row[0],
                    "user_message": row[1],
                    "robot_response": row[2],
                    "emotion_detected": row[3],
                    "emotion_responded": row[4],
                    "conversation_type": row[5],
                    "timestamp": row[6]
                })
            
            return conversations
            
        except Exception as e:
            logger.error(f"채팅 기록 조회 실패: {e}")
            raise
    
    async def get_chat_count(self, user_id: str) -> int:
        """사용자의 채팅 기록 수를 조회합니다."""
        try:
            query = "SELECT COUNT(*) FROM chat_messages WHERE user_id = ?"
            result = db_manager.execute_query(query, (user_id,))
            return result[0][0] if result else 0
        except Exception as e:
            logger.error(f"채팅 기록 수 조회 실패: {e}")
            return 0
    
    async def get_chat_context(self, user_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """채팅 컨텍스트를 조회합니다."""
        try:
            # 기본 컨텍스트
            context = {
                "user_id": user_id,
                "session_id": session_id,
                "user_name": None,
                "conversation_count": 0,
                "last_interaction": None,
                "robot_mood": "friendly",
                "current_topic": "greeting",
                "remembered_info": {
                    "user_preferences": [],
                    "recent_commands": []
                }
            }
            
            # 데이터베이스에서 컨텍스트 조회
            if session_id:
                query = "SELECT * FROM chat_contexts WHERE user_id = ? AND session_id = ?"
                result = db_manager.execute_query(query, (user_id, session_id))
            else:
                query = "SELECT * FROM chat_contexts WHERE user_id = ? ORDER BY last_update DESC LIMIT 1"
                result = db_manager.execute_query(query, (user_id,))
            
            if result:
                row = result[0]
                context.update({
                    "user_name": row[3],  # user_name 컬럼
                    "conversation_count": row[4],  # conversation_count 컬럼
                    "last_interaction": row[5],  # last_interaction 컬럼
                    "robot_mood": row[6],  # robot_mood 컬럼
                    "current_topic": row[7],  # current_topic 컬럼
                    "remembered_info": eval(row[8]) if row[8] else {}  # remembered_info 컬럼
                })
            
            return context
            
        except Exception as e:
            logger.error(f"채팅 컨텍스트 조회 실패: {e}")
            return {
                "user_id": user_id,
                "session_id": session_id,
                "user_name": None,
                "conversation_count": 0,
                "last_interaction": None,
                "robot_mood": "friendly",
                "current_topic": "greeting",
                "remembered_info": {}
            }
    
    async def update_emotion(self, emotion: str, user_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """감정 상태를 업데이트합니다."""
        try:
            if emotion not in self.emotion_states:
                raise ValueError(f"지원하지 않는 감정 상태: {emotion}")
            
            emotion_config = self.emotion_states[emotion]
            
            # 감정 상태 저장
            await self._save_emotion_update(user_id, emotion, reason)
            
            return {
                "emotion": emotion,
                "led_expression": emotion_config["led_expression"],
                "buzzer_sound": emotion_config["buzzer_sound"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"감정 상태 업데이트 실패: {e}")
            raise
    
    async def update_learning_data(self, user_id: str, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """학습 데이터를 업데이트합니다."""
        try:
            # 학습 데이터 저장
            learning_result = await self._save_learning_data(user_id, interaction_data)
            
            return learning_result
            
        except Exception as e:
            logger.error(f"학습 데이터 업데이트 실패: {e}")
            raise
    
    async def get_conversation_patterns(self) -> Dict[str, Any]:
        """대화 패턴을 반환합니다."""
        return self.conversation_patterns
    
    async def get_emotion_states(self) -> Dict[str, Any]:
        """감정 상태를 반환합니다."""
        return self.emotion_states
    
    async def _save_conversation(self, message_id: str, user_id: str, session_id: str,
                                user_message: str, robot_response: str, emotion_detected: str,
                                emotion_responded: str, conversation_type: str):
        """대화를 데이터베이스에 저장합니다."""
        try:
            query = """
            INSERT INTO chat_messages 
            (message_id, user_id, session_id, user_message, robot_response, 
             emotion_detected, emotion_responded, conversation_type, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            db_manager.execute_query(query, (
                message_id, user_id, session_id, user_message, robot_response,
                emotion_detected, emotion_responded, conversation_type, datetime.now().isoformat()
            ))
            
            logger.info(f"대화 저장 완료: {message_id}")
            
        except Exception as e:
            logger.error(f"대화 저장 실패: {e}")
            raise
    
    async def _update_context(self, user_id: str, session_id: str, intent: str, response: Dict[str, Any]):
        """컨텍스트를 업데이트합니다."""
        try:
            # 이름 추출 (자기소개인 경우)
            user_name = None
            if intent == "introduction":
                user_name = self._extract_name(response["text"])
            
            # 컨텍스트 업데이트 또는 생성
            query = """
            INSERT OR REPLACE INTO chat_contexts 
            (user_id, session_id, user_name, conversation_count, last_interaction, 
             robot_mood, current_topic, remembered_info, last_update)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # 기존 대화 수 조회
            count_query = "SELECT COUNT(*) FROM chat_messages WHERE user_id = ? AND session_id = ?"
            count_result = db_manager.execute_query(count_query, (user_id, session_id))
            conversation_count = count_result[0][0] if count_result else 0
            
            db_manager.execute_query(query, (
                user_id, session_id, user_name, conversation_count + 1,
                datetime.now().isoformat(), response["emotion"], intent,
                str({"user_preferences": [], "recent_commands": []}),
                datetime.now().isoformat()
            ))
            
            logger.info(f"컨텍스트 업데이트 완료: {user_id}")
            
        except Exception as e:
            logger.error(f"컨텍스트 업데이트 실패: {e}")
            raise
    
    async def _save_emotion_update(self, user_id: str, emotion: str, reason: Optional[str]):
        """감정 업데이트를 저장합니다."""
        try:
            query = """
            INSERT INTO emotion_updates (user_id, emotion, reason, timestamp)
            VALUES (?, ?, ?, ?)
            """
            
            db_manager.execute_query(query, (user_id, emotion, reason, datetime.now().isoformat()))
            
        except Exception as e:
            logger.error(f"감정 업데이트 저장 실패: {e}")
            raise
    
    async def _save_learning_data(self, user_id: str, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """학습 데이터를 저장합니다."""
        try:
            query = """
            INSERT INTO learning_data (user_id, interaction_data, timestamp)
            VALUES (?, ?, ?)
            """
            
            db_manager.execute_query(query, (user_id, str(interaction_data), datetime.now().isoformat()))
            
            return {
                "learning_type": "interaction_pattern",
                "data_points": 1,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"학습 데이터 저장 실패: {e}")
            raise
