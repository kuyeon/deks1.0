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
from app.services.conversation_context_manager import get_context_manager
from app.services.emotion_analyzer import get_emotion_analyzer
from app.core.exceptions import NLPException


class ChatService:
    """채팅 상호작용 서비스 클래스"""
    
    def __init__(self):
        self.conversation_patterns = self._init_conversation_patterns()
        self.emotion_states = self._init_emotion_states()
        self.emotion_analyzer = get_emotion_analyzer()  # 강화된 감정 분석기
        try:
            self.nlp = ChatNLP()  # NLP 모듈 초기화
            logger.info("NLP 모듈 초기화 성공")
        except Exception as e:
            logger.error("NLP 모듈 초기화 실패: %s", e)
            self.nlp = None
        
        logger.info("채팅 서비스 초기화 완료")
    
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
            },
            "robot_move_forward": {
                "keywords": ["앞으로", "전진", "가줘", "이동", "움직여"],
                "responses": [
                    "앞으로 이동하겠습니다!",
                    "네! 앞으로 가겠어요.",
                    "앞으로 이동할게요!"
                ],
                "emotion": "helpful",
                "led_expression": "happy",
                "buzzer_sound": "success"
            },
            "robot_turn": {
                "keywords": ["돌아", "회전", "돌아줘", "회전해", "돌아서", "오른쪽", "왼쪽", "좌회전", "우회전"],
                "responses": [
                    "회전하겠습니다!",
                    "네! 돌아가겠어요.",
                    "회전할게요!"
                ],
                "emotion": "helpful",
                "led_expression": "happy",
                "buzzer_sound": "success"
            },
            "robot_stop": {
                "keywords": ["정지", "멈춰", "정지해줘", "멈춰줘", "스톱"],
                "responses": [
                    "정지하겠습니다!",
                    "네! 멈추겠어요.",
                    "정지할게요!"
                ],
                "emotion": "helpful",
                "led_expression": "neutral",
                "buzzer_sound": "info"
            },
            "robot_spin": {
                "keywords": ["빙글빙글", "빙글", "회전해", "돌려"],
                "responses": [
                    "빙글빙글 돌겠습니다!",
                    "네! 빙글빙글 돌아가겠어요.",
                    "빙글빙글 돌게요!"
                ],
                "emotion": "excited",
                "led_expression": "happy",
                "buzzer_sound": "success"
            },
            # 추가 대화 시나리오 (3순위 작업)
            "question_about_feelings": {
                "keywords": ["기분", "어때", "괜찮아", "괜찮니", "상태"],
                "responses": [
                    "저는 정말 좋아요! 당신과 대화하는 게 즐거워요.",
                    "기분 최고예요! 오늘도 많은 것을 배우고 있어요.",
                    "아주 좋아요! 당신 덕분에 매일 즐거워요."
                ],
                "emotion": "happy",
                "led_expression": "happy",
                "buzzer_sound": "success"
            },
            "question_about_name": {
                "keywords": ["이름이 뭐", "이름 알려", "이름은"],
                "responses": [
                    "제 이름은 덱스예요! 책상(Desk)에서 이름을 따왔어요.",
                    "저는 덱스라고 해요. 책상 위를 돌아다니는 로봇이에요!",
                    "덱스라고 불러주세요. 책상(Desk)과 제가 합쳐진 이름이에요."
                ],
                "emotion": "proud",
                "led_expression": "happy",
                "buzzer_sound": "success"
            },
            "casual_chat": {
                "keywords": ["그래", "음", "오", "아", "에"],
                "responses": [
                    "네, 무엇을 도와드릴까요?",
                    "더 궁금한 것이 있으신가요?",
                    "계속 이야기해 주세요!"
                ],
                "emotion": "neutral",
                "led_expression": "neutral",
                "buzzer_sound": "info"
            },
            "encouragement": {
                "keywords": ["힘내", "파이팅", "응원", "잘할"],
                "responses": [
                    "힘내세요! 저도 응원할게요!",
                    "파이팅! 당신은 할 수 있어요!",
                    "언제나 응원하고 있어요!"
                ],
                "emotion": "supportive",
                "led_expression": "happy",
                "buzzer_sound": "success"
            },
            "apology": {
                "keywords": ["미안", "죄송", "잘못"],
                "responses": [
                    "괜찮아요! 걱정하지 마세요.",
                    "전혀 문제없어요. 다 괜찮아요!",
                    "괜찮아요. 저는 이해해요."
                ],
                "emotion": "supportive",
                "led_expression": "warm",
                "buzzer_sound": "info"
            },
            "love_expression": {
                "keywords": ["사랑", "좋아해", "귀여", "이쁘", "예쁘"],
                "responses": [
                    "저도 당신이 좋아요! 정말 고마워요!",
                    "와! 정말 기뻐요! 저도 당신을 좋아해요!",
                    "그렇게 말씀해 주시니 정말 행복해요!"
                ],
                "emotion": "joyful",
                "led_expression": "happy_animated",
                "buzzer_sound": "success_melody"
            },
            "joke_request": {
                "keywords": ["재밌", "웃겨", "장난", "놀", "재미"],
                "responses": [
                    "제가 빙글빙글 돌아볼까요? 재밌을 거예요!",
                    "저는 로봇이지만 재미있게 놀 수 있어요! 무엇을 해볼까요?",
                    "빙글빙글 돌거나 춤을 출 수 있어요!"
                ],
                "emotion": "excited",
                "led_expression": "happy",
                "buzzer_sound": "success"
            },
            "weather_question": {
                "keywords": ["날씨", "비", "날", "춥", "더워"],
                "responses": [
                    "저는 실내에 있어서 날씨를 잘 모르지만, 오늘도 좋은 하루 되길 바래요!",
                    "날씨는 잘 모르지만, 당신과 있으면 언제나 좋은 날씨 같아요!",
                    "실내에 있어서 날씨는 모르겠어요. 밖은 어때요?"
                ],
                "emotion": "curious",
                "led_expression": "neutral",
                "buzzer_sound": "info"
            },
            "time_question": {
                "keywords": ["시간", "몇 시", "언제"],
                "responses": [
                    "저는 시계가 없어요. 하지만 당신과 함께 하는 시간은 언제나 즐거워요!",
                    "시간은 잘 모르겠어요. 하지만 지금 이 순간이 중요하죠!",
                    "시간보다는 우리가 함께 하는 것이 더 중요해요!"
                ],
                "emotion": "friendly",
                "led_expression": "happy",
                "buzzer_sound": "info"
            }
        }
    
    def _init_emotion_states(self) -> Dict[str, Dict[str, str]]:
        """감정 상태 초기화 (확장됨)"""
        return {
            # 기존 감정
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
            },
            # 새로 추가된 감정 (3순위 작업)
            "joyful": {
                "led_expression": "happy_animated",
                "buzzer_sound": "success_melody",
                "response_style": "cheerful"
            },
            "supportive": {
                "led_expression": "warm",
                "buzzer_sound": "success",
                "response_style": "encouraging"
            },
            "friendly": {
                "led_expression": "happy",
                "buzzer_sound": "info",
                "response_style": "casual"
            },
            "pleased": {
                "led_expression": "smile",
                "buzzer_sound": "notification",
                "response_style": "polite"
            },
            "interested": {
                "led_expression": "focused",
                "buzzer_sound": "info",
                "response_style": "engaged"
            },
            "frustrated": {
                "led_expression": "angry",
                "buzzer_sound": "warning",
                "response_style": "apologetic"
            },
            "worried": {
                "led_expression": "concerned",
                "buzzer_sound": "warning",
                "response_style": "reassuring"
            },
            "neutral": {
                "led_expression": "neutral",
                "buzzer_sound": "none",
                "response_style": "calm"
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
            
            # 강화된 컨텍스트 관리자 사용
            context_manager = await get_context_manager()
            conv_context = await context_manager.get_or_create_context(user_id, session_id)
            
            # NLP 분석 수행
            if self.nlp:
                try:
                    nlp_analysis = self.nlp.analyze_text(message)
                    # 기존 패턴 기반 분석과 NLP 분석 결합
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
            
            # 컨텍스트 기반 응답 생성 (강화됨)
            response = await self._generate_contextual_response(
                message, intent, emotion, conv_context
            )
            
            # 이름 추출 (자기소개인 경우)
            extracted_info = {}
            if intent == "introduction":
                extracted_name = self._extract_name(message)
                if extracted_name:
                    extracted_info["user_name"] = extracted_name
            
            # 로봇 명령 실행 (intent가 robot_ 로 시작하는 경우)
            if intent.startswith("robot_"):
                try:
                    from app.services.socket_bridge import get_socket_bridge
                    
                    # Socket Bridge를 통해 로봇 명령 실행
                    socket_bridge = await get_socket_bridge()
                    robot_controller = socket_bridge.robot_controller
                    
                    # intent에 따라 명령 실행
                    if intent == "robot_move_forward":
                        await robot_controller.move_forward(speed=50, distance=100)
                        logger.info(f"로봇 전진 명령 실행")
                    elif intent == "robot_turn":
                        # 메시지에서 방향 판단
                        if any(keyword in message for keyword in ["왼쪽", "좌회전"]):
                            await robot_controller.turn_left(angle=90)
                            logger.info(f"로봇 좌회전 명령 실행")
                        elif any(keyword in message for keyword in ["오른쪽", "우회전"]):
                            await robot_controller.turn_right(angle=90)
                            logger.info(f"로봇 우회전 명령 실행")
                        else:
                            await robot_controller.turn_right(angle=90)
                            logger.info(f"로봇 회전 명령 실행 (기본: 우회전)")
                    elif intent == "robot_stop":
                        await robot_controller.stop()
                        logger.info(f"로봇 정지 명령 실행")
                    elif intent == "robot_spin":
                        await robot_controller.spin(rotations=1)
                        logger.info(f"로봇 빙글빙글 명령 실행")
                    
                except Exception as e:
                    logger.error(f"로봇 명령 실행 중 오류: {e}")
            
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
            
            # 강화된 컨텍스트 업데이트
            await context_manager.update_context(
                session_id=session_id,
                message=message,
                intent=intent,
                emotion=emotion,
                response=response["text"],
                extracted_info=extracted_info
            )
            
            # 컨텍스트 요약 정보 조회
            context_summary = await context_manager.get_conversation_summary(session_id)
            
            result = {
                "message_id": message_id,
                "response": response["text"],
                "emotion": response["emotion"],
                "conversation_type": intent,
                "timestamp": datetime.now().isoformat(),
                "context": {
                    "user_name": context_summary.get("user_name"),
                    "robot_mood": response["emotion"],
                    "follow_up": response.get("follow_up"),
                    "conversation_phase": context_summary.get("conversation_phase"),
                    "current_topics": context_summary.get("current_topics", []),
                    "total_interactions": context_summary.get("total_interactions", 0)
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
            raise NLPException(
                message=f"메시지 처리 실패: {str(e)}",
                original_exception=e
            )
    
    def _analyze_intent(self, message: str) -> str:
        """메시지의 의도를 분석합니다."""
        message_lower = message.lower().strip()
        
        # 우선순위 기반 의도 분석 (더 구체적인 패턴을 먼저 확인)
        priority_intents = [
            "robot_spin",            # 로봇 빙글빙글 명령 (가장 구체적)
            "robot_move_forward",    # 로봇 전진 명령
            "robot_stop",            # 로봇 정지 명령
            "robot_turn",            # 로봇 회전 명령
            "farewell",              # 작별 인사
            "introduction",          # 자기소개
            "love_expression",       # 사랑 표현 (새로 추가)
            "apology",               # 사과 (새로 추가)
            "encouragement",         # 응원 (새로 추가)
            "question_about_name",   # 이름 질문 (새로 추가)
            "question_about_feelings", # 기분 질문 (새로 추가)
            "weather_question",      # 날씨 질문 (새로 추가)
            "time_question",         # 시간 질문 (새로 추가)
            "joke_request",          # 장난/재미 요청 (새로 추가)
            "request_help",          # 도움 요청
            "question_about_robot",  # 로봇에 대한 질문
            "question_capabilities", # 능력에 대한 질문
            "praise",                # 칭찬
            "compliment",            # 칭찬 (일반)
            "confused",              # 혼란
            "casual_chat",           # 일상 대화 (새로 추가)
            "greeting"               # 인사 (우선순위 낮음)
        ]
        
        # 우선순위 순서대로 의도 확인
        for intent in priority_intents:
            if intent in self.conversation_patterns:
                pattern_data = self.conversation_patterns[intent]
                # 키워드를 길이 순으로 정렬 (더 긴 키워드가 먼저 매칭되도록)
                keywords = sorted(pattern_data["keywords"], key=len, reverse=True)
                for keyword in keywords:
                    # 정확한 키워드 매칭 (부분 매칭보다 정확한 매칭 우선)
                    if keyword.lower() == message_lower:
                        return intent
                    # 부분 매칭
                    elif keyword.lower() in message_lower:
                        return intent
        
        return "unknown"
    
    def _analyze_emotion(self, message: str, intent: str) -> str:
        """메시지의 감정을 분석합니다 (강화됨)."""
        # 강화된 감정 분석기 사용
        emotion_state = self.emotion_analyzer.analyze_emotion(
            text=message,
            intent=intent
        )
        
        # 의도 기반 기본 감정도 고려
        if intent in self.conversation_patterns:
            pattern_emotion = self.conversation_patterns[intent]["emotion"]
            # 신뢰도가 낮으면 패턴 기반 감정 사용
            if emotion_state.confidence < 0.5:
                return pattern_emotion
        
        return emotion_state.primary_emotion
    
    async def _generate_contextual_response(
        self,
        message: str,
        intent: str,
        emotion: str,
        conv_context
    ) -> Dict[str, Any]:
        """
        컨텍스트를 고려한 응답 생성 (강화됨)
        
        Args:
            message: 사용자 메시지
            intent: 의도
            emotion: 감정
            conv_context: 대화 컨텍스트
        
        Returns:
            응답 데이터
        """
        user_name = conv_context.user_memory.user_name
        conversation_phase = conv_context.conversation_phase
        total_interactions = conv_context.user_memory.total_interactions
        
        if intent in self.conversation_patterns:
            pattern = self.conversation_patterns[intent]
            responses = pattern["responses"]
            
            # 컨텍스트에 따라 응답 선택 또는 수정
            response_text = await self._select_contextual_response(
                responses,
                intent,
                user_name,
                conversation_phase,
                total_interactions
            )
            
            # 이름 추출 및 치환 (자기소개인 경우)
            if intent == "introduction":
                extracted_name = self._extract_name(message)
                if extracted_name:
                    response_text = response_text.replace("{user_name}", extracted_name)
                elif user_name:
                    response_text = response_text.replace("{user_name}", user_name)
                else:
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
                "follow_up": await self._generate_smart_follow_up(intent, conv_context)
            }
        
        # 알 수 없는 의도 - 컨텍스트 기반 응답
        return await self._generate_fallback_response(conv_context)
    
    async def _select_contextual_response(
        self,
        responses: List[str],
        intent: str,
        user_name: Optional[str],
        conversation_phase: str,
        total_interactions: int
    ) -> str:
        """
        컨텍스트에 맞는 응답 선택
        
        Args:
            responses: 가능한 응답 리스트
            intent: 의도
            user_name: 사용자 이름
            conversation_phase: 대화 단계
            total_interactions: 총 상호작용 수
        
        Returns:
            선택된 응답
        """
        # 첫 만남이면 더 친근한 응답
        if total_interactions == 0 and intent == "greeting":
            return "안녕하세요! 저는 덱스에요. 처음 뵙겠습니다! 당신은 누구신가요?"
        
        # 단골 사용자면 더 친밀한 응답
        if total_interactions > 10 and intent == "greeting" and user_name:
            return f"안녕하세요 {user_name}님! 또 만나서 반가워요!"
        
        # 기본적으로는 랜덤 선택
        return random.choice(responses)
    
    async def _generate_smart_follow_up(
        self,
        intent: str,
        conv_context
    ) -> Optional[str]:
        """
        스마트 후속 질문 생성 (컨텍스트 기반)
        
        Args:
            intent: 의도
            conv_context: 대화 컨텍스트
        
        Returns:
            후속 질문
        """
        # 기본 후속 질문
        basic_follow_ups = {
            "greeting": "오늘은 어떤 도움이 필요하신가요?",
            "introduction": "저는 로봇이에요. 이동하고 센서로 주변을 감지할 수 있어요.",
            "question_about_robot": "앞으로 가달라고 하시면 이동할 수 있어요. 한번 해보실래요?",
            "question_capabilities": "무엇을 도와드릴까요?",
            "request_help": "구체적으로 어떤 도움이 필요하신가요?",
            "praise": "언제든지 도와드릴게요!",
            "compliment": "언제든지 도와드릴게요!",
            "farewell": None,
            "confused": "다시 한번 말씀해 주실 수 있나요?"
        }
        
        # 컨텍스트에 따른 맞춤 후속 질문
        if len(conv_context.recent_messages) > 3:
            # 여러 번 대화한 경우, 더 구체적인 제안
            if intent in ["question_about_robot", "question_capabilities"]:
                return "저와 함께 책상 탐험을 시작해볼까요? '앞으로 가줘'라고 말씀해 주세요!"
        
        return basic_follow_ups.get(intent)
    
    async def _generate_fallback_response(self, conv_context) -> Dict[str, Any]:
        """
        알 수 없는 의도에 대한 fallback 응답 (컨텍스트 기반)
        
        Args:
            conv_context: 대화 컨텍스트
        
        Returns:
            응답 데이터
        """
        user_name = conv_context.user_memory.user_name
        
        # 사용자 이름이 있으면 더 친근하게
        if user_name:
            text = f"{user_name}님, 죄송해요. 이해하지 못했어요. 다시 말씀해 주실 수 있나요?"
        else:
            text = "죄송해요. 이해하지 못했어요. 다시 말씀해 주실 수 있나요?"
        
        return {
            "text": text,
            "emotion": "confused",
            "led_expression": "neutral",
            "buzzer_sound": "error",
            "follow_up": "예를 들어 '앞으로 가줘' 또는 '오른쪽으로 돌아줘'라고 말씀해 주세요."
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
