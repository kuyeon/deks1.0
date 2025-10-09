"""
강화된 대화 컨텍스트 관리 시스템
장기 기억, 맥락 유지, 대화 흐름 관리
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from loguru import logger
import json

from app.database.database_manager import db_manager
from app.core.exceptions import ChatContextException


@dataclass
class ConversationTopic:
    """대화 주제"""
    topic: str
    started_at: datetime
    last_mentioned: datetime
    mention_count: int = 1
    related_keywords: List[str] = field(default_factory=list)


@dataclass
class UserMemory:
    """사용자 장기 기억"""
    user_id: str
    user_name: Optional[str] = None
    preferred_name: Optional[str] = None  # 호칭 선호도
    personality_traits: Dict[str, float] = field(default_factory=dict)  # 성격 특성
    interests: List[str] = field(default_factory=list)  # 관심사
    preferences: Dict[str, Any] = field(default_factory=dict)  # 선호도
    learned_patterns: Dict[str, int] = field(default_factory=dict)  # 학습된 패턴
    total_interactions: int = 0
    first_met: Optional[datetime] = None
    last_met: Optional[datetime] = None


@dataclass
class ConversationContext:
    """대화 컨텍스트 (세션 기반)"""
    user_id: str
    session_id: str
    user_memory: UserMemory
    current_topics: List[ConversationTopic] = field(default_factory=list)
    recent_messages: List[Dict[str, Any]] = field(default_factory=list)  # 최근 10개
    robot_mood: str = "friendly"
    conversation_phase: str = "greeting"  # greeting, introduction, conversation, command, farewell
    last_intent: Optional[str] = None
    last_emotion: Optional[str] = None
    unresolved_questions: List[str] = field(default_factory=list)
    pending_actions: List[str] = field(default_factory=list)


class ConversationContextManager:
    """대화 컨텍스트 관리자"""
    
    def __init__(self):
        """컨텍스트 관리자 초기화"""
        self.active_contexts: Dict[str, ConversationContext] = {}  # session_id -> context
        self.user_memories: Dict[str, UserMemory] = {}  # user_id -> memory
        self.max_recent_messages = 10
        self.context_timeout = timedelta(hours=1)  # 1시간 후 컨텍스트 만료
        
        logger.info("대화 컨텍스트 관리자 초기화 완료")
    
    async def get_or_create_context(
        self,
        user_id: str,
        session_id: str
    ) -> ConversationContext:
        """
        컨텍스트 조회 또는 생성
        
        Args:
            user_id: 사용자 ID
            session_id: 세션 ID
        
        Returns:
            대화 컨텍스트
        """
        try:
            # 활성 컨텍스트 확인
            if session_id in self.active_contexts:
                context = self.active_contexts[session_id]
                # 타임아웃 체크
                if self._is_context_expired(context):
                    logger.info(f"컨텍스트 타임아웃, 새로 생성: {session_id}")
                    del self.active_contexts[session_id]
                else:
                    return context
            
            # 사용자 장기 기억 로드
            user_memory = await self._load_or_create_user_memory(user_id)
            
            # 새 컨텍스트 생성
            context = ConversationContext(
                user_id=user_id,
                session_id=session_id,
                user_memory=user_memory
            )
            
            # DB에서 이전 대화 히스토리 로드
            await self._load_recent_history(context)
            
            # 활성 컨텍스트에 추가
            self.active_contexts[session_id] = context
            
            logger.info(f"새 컨텍스트 생성: {session_id} (사용자: {user_id})")
            return context
            
        except Exception as e:
            logger.error(f"컨텍스트 조회/생성 실패: {e}")
            raise ChatContextException(
                message=f"컨텍스트 조회/생성 실패: {str(e)}",
                original_exception=e
            )
    
    async def update_context(
        self,
        session_id: str,
        message: str,
        intent: str,
        emotion: str,
        response: str,
        extracted_info: Optional[Dict[str, Any]] = None
    ):
        """
        대화 컨텍스트 업데이트
        
        Args:
            session_id: 세션 ID
            message: 사용자 메시지
            intent: 의도
            emotion: 감정
            response: 로봇 응답
            extracted_info: 추출된 정보 (이름, 선호도 등)
        """
        try:
            if session_id not in self.active_contexts:
                logger.warning(f"활성 컨텍스트가 없음: {session_id}")
                return
            
            context = self.active_contexts[session_id]
            
            # 최근 메시지 추가
            message_record = {
                "timestamp": datetime.now(),
                "user_message": message,
                "robot_response": response,
                "intent": intent,
                "emotion": emotion
            }
            context.recent_messages.append(message_record)
            
            # 최대 개수 유지
            if len(context.recent_messages) > self.max_recent_messages:
                context.recent_messages.pop(0)
            
            # 주제 추적
            await self._update_topics(context, message, intent)
            
            # 대화 단계 업데이트
            context.conversation_phase = self._determine_conversation_phase(
                context, intent
            )
            
            # 마지막 의도/감정 업데이트
            context.last_intent = intent
            context.last_emotion = emotion
            
            # 로봇 분위기 업데이트
            context.robot_mood = emotion
            
            # 추출된 정보 처리
            if extracted_info:
                await self._process_extracted_info(context, extracted_info)
            
            # 사용자 장기 기억 업데이트
            await self._update_user_memory(context)
            
            logger.debug(f"컨텍스트 업데이트 완료: {session_id}")
            
        except Exception as e:
            logger.error(f"컨텍스트 업데이트 실패: {e}")
            raise ChatContextException(
                message=f"컨텍스트 업데이트 실패: {str(e)}",
                original_exception=e
            )
    
    async def get_contextual_info(
        self,
        session_id: str,
        info_type: str
    ) -> Optional[Any]:
        """
        컨텍스트 기반 정보 조회
        
        Args:
            session_id: 세션 ID
            info_type: 정보 유형 (user_name, topics, mood 등)
        
        Returns:
            요청된 정보
        """
        if session_id not in self.active_contexts:
            return None
        
        context = self.active_contexts[session_id]
        
        if info_type == "user_name":
            return context.user_memory.user_name or context.user_memory.preferred_name
        elif info_type == "topics":
            return [topic.topic for topic in context.current_topics]
        elif info_type == "mood":
            return context.robot_mood
        elif info_type == "conversation_phase":
            return context.conversation_phase
        elif info_type == "last_intent":
            return context.last_intent
        elif info_type == "recent_messages":
            return context.recent_messages[-3:]  # 최근 3개
        elif info_type == "interests":
            return context.user_memory.interests
        else:
            return None
    
    async def add_user_interest(self, session_id: str, interest: str):
        """사용자 관심사 추가"""
        if session_id in self.active_contexts:
            context = self.active_contexts[session_id]
            if interest not in context.user_memory.interests:
                context.user_memory.interests.append(interest)
                logger.info(f"사용자 관심사 추가: {interest}")
    
    async def add_user_preference(
        self,
        session_id: str,
        key: str,
        value: Any
    ):
        """사용자 선호도 추가"""
        if session_id in self.active_contexts:
            context = self.active_contexts[session_id]
            context.user_memory.preferences[key] = value
            logger.info(f"사용자 선호도 추가: {key}={value}")
    
    async def remember_info(
        self,
        session_id: str,
        info_key: str,
        info_value: Any
    ):
        """특정 정보 기억하기"""
        if session_id in self.active_contexts:
            context = self.active_contexts[session_id]
            # remembered_info는 user_memory의 preferences에 저장
            context.user_memory.preferences[f"remembered_{info_key}"] = info_value
            logger.info(f"정보 기억: {info_key}={info_value}")
    
    async def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """대화 요약 정보 조회"""
        if session_id not in self.active_contexts:
            return {}
        
        context = self.active_contexts[session_id]
        
        return {
            "user_id": context.user_id,
            "session_id": context.session_id,
            "user_name": context.user_memory.user_name,
            "conversation_phase": context.conversation_phase,
            "robot_mood": context.robot_mood,
            "current_topics": [topic.topic for topic in context.current_topics],
            "message_count": len(context.recent_messages),
            "total_interactions": context.user_memory.total_interactions,
            "interests": context.user_memory.interests,
            "last_intent": context.last_intent,
            "last_emotion": context.last_emotion
        }
    
    def _is_context_expired(self, context: ConversationContext) -> bool:
        """컨텍스트 만료 여부 확인"""
        if not context.recent_messages:
            return False
        
        last_message_time = context.recent_messages[-1]["timestamp"]
        return datetime.now() - last_message_time > self.context_timeout
    
    async def _load_or_create_user_memory(self, user_id: str) -> UserMemory:
        """사용자 장기 기억 로드 또는 생성"""
        try:
            # 캐시 확인
            if user_id in self.user_memories:
                return self.user_memories[user_id]
            
            # DB에서 로드
            query = """
            SELECT user_name, preferred_name, personality_traits, interests, 
                   preferences, learned_patterns, total_interactions, 
                   first_met, last_met
            FROM user_long_term_memory 
            WHERE user_id = ?
            """
            
            result = db_manager.execute_query(query, (user_id,))
            
            if result and result[0]:
                row = result[0]
                memory = UserMemory(
                    user_id=user_id,
                    user_name=row[0],
                    preferred_name=row[1],
                    personality_traits=json.loads(row[2]) if row[2] else {},
                    interests=json.loads(row[3]) if row[3] else [],
                    preferences=json.loads(row[4]) if row[4] else {},
                    learned_patterns=json.loads(row[5]) if row[5] else {},
                    total_interactions=row[6] or 0,
                    first_met=datetime.fromisoformat(row[7]) if row[7] else None,
                    last_met=datetime.fromisoformat(row[8]) if row[8] else None
                )
            else:
                # 새 사용자 기억 생성
                memory = UserMemory(
                    user_id=user_id,
                    first_met=datetime.now(),
                    last_met=datetime.now()
                )
            
            # 캐시에 저장
            self.user_memories[user_id] = memory
            
            return memory
            
        except Exception as e:
            logger.error(f"사용자 기억 로드 실패: {e}")
            # 기본 메모리 반환
            return UserMemory(user_id=user_id)
    
    async def _load_recent_history(self, context: ConversationContext):
        """최근 대화 히스토리 로드"""
        try:
            query = """
            SELECT user_message, robot_response, emotion_detected, 
                   emotion_responded, conversation_type, timestamp
            FROM chat_messages 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
            """
            
            results = db_manager.execute_query(
                query,
                (context.user_id, self.max_recent_messages)
            )
            
            if results:
                for row in reversed(results):  # 오래된 것부터
                    context.recent_messages.append({
                        "timestamp": datetime.fromisoformat(row[5]),
                        "user_message": row[0],
                        "robot_response": row[1],
                        "intent": row[4],
                        "emotion": row[3]
                    })
            
        except Exception as e:
            logger.error(f"히스토리 로드 실패: {e}")
    
    async def _update_topics(
        self,
        context: ConversationContext,
        message: str,
        intent: str
    ):
        """대화 주제 추적 및 업데이트"""
        # 주제 매핑
        topic_mapping = {
            "greeting": "인사",
            "introduction": "자기소개",
            "question_about_robot": "로봇 정보",
            "question_capabilities": "로봇 능력",
            "request_help": "도움 요청",
            "robot_move_forward": "로봇 이동",
            "robot_turn": "로봇 회전",
            "robot_stop": "로봇 정지",
            "robot_spin": "로봇 회전",
            "praise": "칭찬",
            "compliment": "칭찬",
            "farewell": "작별"
        }
        
        topic_name = topic_mapping.get(intent, "일반 대화")
        
        # 기존 주제 업데이트 또는 새 주제 추가
        topic_found = False
        for topic in context.current_topics:
            if topic.topic == topic_name:
                topic.last_mentioned = datetime.now()
                topic.mention_count += 1
                topic_found = True
                break
        
        if not topic_found:
            new_topic = ConversationTopic(
                topic=topic_name,
                started_at=datetime.now(),
                last_mentioned=datetime.now(),
                mention_count=1
            )
            context.current_topics.append(new_topic)
        
        # 오래된 주제 제거 (5분 이상 언급되지 않음)
        context.current_topics = [
            topic for topic in context.current_topics
            if datetime.now() - topic.last_mentioned < timedelta(minutes=5)
        ]
    
    def _determine_conversation_phase(
        self,
        context: ConversationContext,
        intent: str
    ) -> str:
        """대화 단계 결정"""
        # 작별 인사
        if intent == "farewell":
            return "farewell"
        
        # 명령 단계
        if intent.startswith("robot_"):
            return "command"
        
        # 자기소개 단계
        if intent == "introduction":
            return "introduction"
        
        # 인사 단계
        if intent == "greeting" and context.user_memory.total_interactions == 0:
            return "greeting"
        
        # 일반 대화 단계
        return "conversation"
    
    async def _process_extracted_info(
        self,
        context: ConversationContext,
        extracted_info: Dict[str, Any]
    ):
        """추출된 정보 처리 (이름, 선호도 등)"""
        # 사용자 이름 업데이트
        if "user_name" in extracted_info and extracted_info["user_name"]:
            context.user_memory.user_name = extracted_info["user_name"]
            logger.info(f"사용자 이름 업데이트: {extracted_info['user_name']}")
        
        # 선호도 업데이트
        if "preferences" in extracted_info:
            for key, value in extracted_info["preferences"].items():
                context.user_memory.preferences[key] = value
        
        # 관심사 추가
        if "interests" in extracted_info:
            for interest in extracted_info["interests"]:
                if interest not in context.user_memory.interests:
                    context.user_memory.interests.append(interest)
    
    async def _update_user_memory(self, context: ConversationContext):
        """사용자 장기 기억 업데이트 (DB 저장)"""
        try:
            memory = context.user_memory
            memory.total_interactions += 1
            memory.last_met = datetime.now()
            
            # DB에 저장
            query = """
            INSERT OR REPLACE INTO user_long_term_memory 
            (user_id, user_name, preferred_name, personality_traits, interests,
             preferences, learned_patterns, total_interactions, first_met, last_met)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            db_manager.execute_query(query, (
                memory.user_id,
                memory.user_name,
                memory.preferred_name,
                json.dumps(memory.personality_traits, ensure_ascii=False),
                json.dumps(memory.interests, ensure_ascii=False),
                json.dumps(memory.preferences, ensure_ascii=False),
                json.dumps(memory.learned_patterns, ensure_ascii=False),
                memory.total_interactions,
                memory.first_met.isoformat() if memory.first_met else None,
                memory.last_met.isoformat() if memory.last_met else None
            ))
            
            # 캐시 업데이트
            self.user_memories[memory.user_id] = memory
            
        except Exception as e:
            logger.error(f"사용자 기억 저장 실패: {e}")
    
    async def cleanup_expired_contexts(self):
        """만료된 컨텍스트 정리"""
        expired_sessions = []
        
        for session_id, context in self.active_contexts.items():
            if self._is_context_expired(context):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_contexts[session_id]
            logger.info(f"만료된 컨텍스트 제거: {session_id}")
        
        if expired_sessions:
            logger.info(f"총 {len(expired_sessions)}개 컨텍스트 정리됨")
    
    async def get_active_context_count(self) -> int:
        """활성 컨텍스트 수 조회"""
        return len(self.active_contexts)
    
    async def get_total_user_count(self) -> int:
        """총 사용자 수 조회"""
        try:
            query = "SELECT COUNT(DISTINCT user_id) FROM user_long_term_memory"
            result = db_manager.execute_query(query)
            return result[0][0] if result else 0
        except Exception as e:
            logger.error(f"사용자 수 조회 실패: {e}")
            return 0


# 전역 컨텍스트 관리자 인스턴스
_context_manager: Optional[ConversationContextManager] = None


async def get_context_manager() -> ConversationContextManager:
    """컨텍스트 관리자 싱글톤 인스턴스 조회"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ConversationContextManager()
    return _context_manager

