"""
Deks 1.0 강화된 Chat Interaction API 테스트
3순위 작업: 대화 시스템 고도화
"""

import pytest
from app.services.conversation_context_manager import (
    ConversationContextManager,
    UserMemory,
    ConversationContext,
    ConversationTopic
)
from app.services.emotion_analyzer import (
    EmotionAnalyzer,
    EmotionState,
    EmotionCategory,
    EmotionIntensity
)
from app.services.chat_service import ChatService
from datetime import datetime, timedelta


class TestConversationContextManager:
    """대화 컨텍스트 관리자 테스트"""
    
    @pytest.mark.asyncio
    async def test_create_new_context(self):
        """새 컨텍스트 생성 테스트"""
        manager = ConversationContextManager()
        
        context = await manager.get_or_create_context(
            user_id="test_user_001",
            session_id="session_001"
        )
        
        assert context is not None
        assert context.user_id == "test_user_001"
        assert context.session_id == "session_001"
        assert isinstance(context.user_memory, UserMemory)
    
    @pytest.mark.asyncio
    async def test_context_caching(self):
        """컨텍스트 캐싱 테스트"""
        manager = ConversationContextManager()
        
        context1 = await manager.get_or_create_context("user1", "session1")
        context2 = await manager.get_or_create_context("user1", "session1")
        
        # 같은 객체여야 함
        assert context1 is context2
    
    @pytest.mark.asyncio
    async def test_update_context_with_message(self):
        """메시지로 컨텍스트 업데이트 테스트"""
        manager = ConversationContextManager()
        context = await manager.get_or_create_context("user1", "session1")
        
        await manager.update_context(
            session_id="session1",
            message="안녕 덱스!",
            intent="greeting",
            emotion="happy",
            response="안녕하세요!",
            extracted_info={}
        )
        
        assert len(context.recent_messages) == 1
        assert context.last_intent == "greeting"
        assert context.last_emotion == "happy"
    
    @pytest.mark.asyncio
    async def test_user_name_extraction(self):
        """사용자 이름 추출 및 저장 테스트"""
        manager = ConversationContextManager()
        context = await manager.get_or_create_context("user1", "session1")
        
        await manager.update_context(
            session_id="session1",
            message="저는 김철수예요",
            intent="introduction",
            emotion="happy",
            response="안녕하세요 김철수님!",
            extracted_info={"user_name": "김철수"}
        )
        
        assert context.user_memory.user_name == "김철수"
    
    @pytest.mark.asyncio
    async def test_conversation_topics_tracking(self):
        """대화 주제 추적 테스트"""
        manager = ConversationContextManager()
        context = await manager.get_or_create_context("user1", "session1")
        
        # 첫 주제
        await manager.update_context(
            session_id="session1",
            message="안녕",
            intent="greeting",
            emotion="happy",
            response="안녕하세요!"
        )
        
        assert len(context.current_topics) >= 1
        assert any(topic.topic == "인사" for topic in context.current_topics)
    
    @pytest.mark.asyncio
    async def test_conversation_phase_detection(self):
        """대화 단계 감지 테스트"""
        manager = ConversationContextManager()
        context = await manager.get_or_create_context("user1", "session1")
        
        # 인사 단계
        await manager.update_context(
            session_id="session1",
            message="안녕",
            intent="greeting",
            emotion="happy",
            response="안녕하세요!"
        )
        
        # 단계가 설정되어야 함
        assert context.conversation_phase in ["greeting", "conversation"]
    
    @pytest.mark.asyncio
    async def test_contextual_info_retrieval(self):
        """컨텍스트 정보 조회 테스트"""
        manager = ConversationContextManager()
        context = await manager.get_or_create_context("user1", "session1")
        
        await manager.update_context(
            session_id="session1",
            message="저는 김철수예요",
            intent="introduction",
            emotion="happy",
            response="반가워요!",
            extracted_info={"user_name": "김철수"}
        )
        
        user_name = await manager.get_contextual_info("session1", "user_name")
        assert user_name == "김철수"
        
        mood = await manager.get_contextual_info("session1", "mood")
        assert mood is not None


class TestEmotionAnalyzer:
    """강화된 감정 분석기 테스트"""
    
    def test_emotion_analyzer_initialization(self):
        """감정 분석기 초기화 테스트"""
        analyzer = EmotionAnalyzer()
        
        assert analyzer is not None
        assert len(analyzer.emotion_patterns) > 0
        assert len(analyzer.emotion_lexicon) > 0
        assert len(analyzer.expression_mapping) > 0
    
    def test_positive_emotion_detection(self):
        """긍정 감정 감지 테스트"""
        analyzer = EmotionAnalyzer()
        
        emotion_state = analyzer.analyze_emotion("정말 최고예요! 너무 좋아요!")
        
        assert emotion_state.category == EmotionCategory.POSITIVE
        assert emotion_state.sentiment_score > 0.5
        assert emotion_state.primary_emotion in ["joyful", "happy", "excited"]
    
    def test_negative_emotion_detection(self):
        """부정 감정 감지 테스트"""
        analyzer = EmotionAnalyzer()
        
        emotion_state = analyzer.analyze_emotion("정말 짜증나요. 화가 나요.")
        
        assert emotion_state.category == EmotionCategory.NEGATIVE
        assert emotion_state.sentiment_score < -0.3
    
    def test_neutral_emotion_detection(self):
        """중립 감정 감지 테스트"""
        analyzer = EmotionAnalyzer()
        
        emotion_state = analyzer.analyze_emotion("그냥 보통이에요.")
        
        assert emotion_state.category == EmotionCategory.NEUTRAL
        assert -0.2 < emotion_state.sentiment_score < 0.2
    
    def test_emotion_with_intent(self):
        """의도와 함께 감정 분석 테스트"""
        analyzer = EmotionAnalyzer()
        
        emotion_state = analyzer.analyze_emotion(
            text="도움이 필요해요",
            intent="request_help"
        )
        
        # 의도에 맞게 감정이 보정되었는지 확인
        assert emotion_state.primary_emotion in ["helpful", "supportive", "curious", "excited"]
    
    def test_sentiment_score_calculation(self):
        """감정 점수 계산 테스트"""
        analyzer = EmotionAnalyzer()
        
        # 매우 긍정적
        state1 = analyzer.analyze_emotion("최고! 완벽해요! 멋져요!")
        assert state1.sentiment_score > 0.7
        
        # 매우 부정적
        state2 = analyzer.analyze_emotion("최악이에요. 끔찍해요.")
        assert state2.sentiment_score < -0.7
    
    def test_emotion_intensity(self):
        """감정 강도 테스트"""
        analyzer = EmotionAnalyzer()
        
        # 강한 긍정
        state = analyzer.analyze_emotion("완전 대박! 최고!")
        assert state.intensity in [EmotionIntensity.HIGH, EmotionIntensity.VERY_HIGH]
    
    def test_emotion_triggers(self):
        """감정 유발 키워드 찾기 테스트"""
        analyzer = EmotionAnalyzer()
        
        emotion_state = analyzer.analyze_emotion("정말 좋아요! 감사해요!")
        
        assert len(emotion_state.triggers) > 0
    
    def test_get_emotion_response(self):
        """감정 응답 생성 테스트"""
        analyzer = EmotionAnalyzer()
        
        emotion_state = EmotionState(
            primary_emotion="happy",
            category=EmotionCategory.POSITIVE,
            intensity=EmotionIntensity.MEDIUM,
            sentiment_score=0.7
        )
        
        response = analyzer.get_emotion_response(emotion_state)
        
        assert response.led_expression is not None
        assert response.buzzer_sound is not None
        assert response.response_modifier is not None
    
    def test_blend_emotions(self):
        """감정 혼합 테스트"""
        analyzer = EmotionAnalyzer()
        
        # 사용자가 부정적이면 로봇은 지지적으로
        user_emotion = EmotionState(
            primary_emotion="sad",
            category=EmotionCategory.NEGATIVE,
            intensity=EmotionIntensity.MEDIUM,
            sentiment_score=-0.5
        )
        
        blended = analyzer.blend_emotions(user_emotion, "neutral")
        
        assert blended.primary_emotion == "supportive"
        assert blended.category == EmotionCategory.POSITIVE


class TestEnhancedChatScenarios:
    """강화된 채팅 시나리오 테스트"""
    
    def test_new_scenarios_exist(self):
        """새 시나리오 존재 확인"""
        service = ChatService()
        
        new_scenarios = [
            "question_about_feelings",
            "question_about_name",
            "casual_chat",
            "encouragement",
            "apology",
            "love_expression",
            "joke_request",
            "weather_question",
            "time_question"
        ]
        
        for scenario in new_scenarios:
            assert scenario in service.conversation_patterns
    
    @pytest.mark.asyncio
    async def test_feelings_question_response(self):
        """기분 질문 응답 테스트"""
        service = ChatService()
        
        response = await service.process_message(
            message="기분 어때?",
            user_id="test_user",
            session_id="test_session"
        )
        
        assert response is not None
        assert "기분" in response["response"] or "좋" in response["response"]
        assert response["conversation_type"] == "question_about_feelings"
    
    @pytest.mark.asyncio
    async def test_name_question_response(self):
        """이름 질문 응답 테스트"""
        service = ChatService()
        
        response = await service.process_message(
            message="너 이름이 뭐야?",
            user_id="test_user",
            session_id="test_session"
        )
        
        assert response is not None
        assert "덱스" in response["response"]
        assert response["conversation_type"] == "question_about_name"
    
    @pytest.mark.asyncio
    async def test_love_expression_response(self):
        """사랑 표현 응답 테스트"""
        service = ChatService()
        
        response = await service.process_message(
            message="정말 귀여워!",
            user_id="test_user",
            session_id="test_session"
        )
        
        assert response is not None
        assert response["emotion"] in ["joyful", "happy", "excited"]
    
    @pytest.mark.asyncio
    async def test_apology_response(self):
        """사과 응답 테스트"""
        service = ChatService()
        
        response = await service.process_message(
            message="미안해",
            user_id="test_user",
            session_id="test_session"
        )
        
        assert response is not None
        assert "괜찮" in response["response"]
        assert response["emotion"] == "supportive"
    
    @pytest.mark.asyncio
    async def test_encouragement_response(self):
        """응원 응답 테스트"""
        service = ChatService()
        
        response = await service.process_message(
            message="파이팅!",
            user_id="test_user",
            session_id="test_session"
        )
        
        assert response is not None
        assert response["emotion"] == "supportive"


class TestContextualResponseGeneration:
    """컨텍스트 기반 응답 생성 테스트"""
    
    @pytest.mark.asyncio
    async def test_first_time_greeting(self):
        """첫 만남 인사 테스트"""
        service = ChatService()
        
        response = await service.process_message(
            message="안녕",
            user_id="new_user_001",
            session_id="new_session_001"
        )
        
        assert response is not None
        # 첫 만남 시 더 친근한 응답
        assert "덱스" in response["response"] or "처음" in response["response"] or "누구" in response["response"]
    
    @pytest.mark.asyncio
    async def test_returning_user_greeting(self):
        """재방문 사용자 인사 테스트"""
        manager = ConversationContextManager()
        context = await manager.get_or_create_context("returning_user", "session2")
        
        # 사용자 기억 업데이트 (이전 방문 시뮬레이션)
        context.user_memory.user_name = "김철수"
        context.user_memory.total_interactions = 15
        
        service = ChatService()
        response = await service.process_message(
            message="안녕",
            user_id="returning_user",
            session_id="session2"
        )
        
        assert response is not None
    
    @pytest.mark.asyncio
    async def test_context_includes_topics(self):
        """응답에 주제 정보 포함 테스트"""
        service = ChatService()
        
        response = await service.process_message(
            message="앞으로 가줘",
            user_id="test_user",
            session_id="test_session"
        )
        
        assert response is not None
        assert "context" in response
        assert "current_topics" in response["context"]
    
    @pytest.mark.asyncio
    async def test_conversation_phase_tracking(self):
        """대화 단계 추적 테스트"""
        service = ChatService()
        
        # 첫 인사
        response1 = await service.process_message(
            message="안녕",
            user_id="phase_test_user",
            session_id="phase_session"
        )
        
        assert "conversation_phase" in response1["context"]
        
        # 자기소개
        response2 = await service.process_message(
            message="저는 김철수예요",
            user_id="phase_test_user",
            session_id="phase_session"
        )
        
        assert response2["context"]["conversation_phase"] in ["introduction", "conversation"]


class TestUserMemorySystem:
    """사용자 기억 시스템 테스트"""
    
    @pytest.mark.asyncio
    async def test_user_memory_creation(self):
        """사용자 기억 생성 테스트"""
        memory = UserMemory(user_id="test_user")
        
        assert memory.user_id == "test_user"
        assert memory.total_interactions == 0
        assert isinstance(memory.interests, list)
        assert isinstance(memory.preferences, dict)
    
    @pytest.mark.asyncio
    async def test_add_user_interest(self):
        """사용자 관심사 추가 테스트"""
        manager = ConversationContextManager()
        context = await manager.get_or_create_context("user1", "session1")
        
        await manager.add_user_interest("session1", "로봇")
        await manager.add_user_interest("session1", "AI")
        
        assert "로봇" in context.user_memory.interests
        assert "AI" in context.user_memory.interests
    
    @pytest.mark.asyncio
    async def test_add_user_preference(self):
        """사용자 선호도 추가 테스트"""
        manager = ConversationContextManager()
        context = await manager.get_or_create_context("user1", "session1")
        
        await manager.add_user_preference("session1", "response_style", "casual")
        
        assert context.user_memory.preferences["response_style"] == "casual"
    
    @pytest.mark.asyncio
    async def test_remember_specific_info(self):
        """특정 정보 기억 테스트"""
        manager = ConversationContextManager()
        context = await manager.get_or_create_context("user1", "session1")
        
        await manager.remember_info("session1", "favorite_color", "파란색")
        
        assert "remembered_favorite_color" in context.user_memory.preferences
        assert context.user_memory.preferences["remembered_favorite_color"] == "파란색"


class TestEmotionResponseSystem:
    """감정 응답 시스템 테스트"""
    
    def test_emotion_state_creation(self):
        """감정 상태 생성 테스트"""
        state = EmotionState(
            primary_emotion="happy",
            category=EmotionCategory.POSITIVE,
            intensity=EmotionIntensity.MEDIUM,
            sentiment_score=0.7,
            confidence=0.8,
            triggers=["좋아", "감사"]
        )
        
        assert state.primary_emotion == "happy"
        assert state.category == EmotionCategory.POSITIVE
        assert len(state.triggers) == 2
    
    def test_complex_emotion_detection(self):
        """복합 감정 감지 테스트"""
        analyzer = EmotionAnalyzer()
        
        # 혼합된 감정 ("안녕히"는 작별이라 bittersweet)
        state = analyzer.analyze_emotion("안녕히 가세요. 감사했어요.")
        
        assert state.category in [EmotionCategory.MIXED, EmotionCategory.POSITIVE]
    
    def test_emotion_intensity_levels(self):
        """감정 강도 레벨 테스트"""
        # 강도 레벨이 정의되어 있는지 확인
        assert EmotionIntensity.VERY_LOW.value == 1
        assert EmotionIntensity.LOW.value == 2
        assert EmotionIntensity.MEDIUM.value == 3
        assert EmotionIntensity.HIGH.value == 4
        assert EmotionIntensity.VERY_HIGH.value == 5


class TestEnhancedChatService:
    """강화된 채팅 서비스 테스트"""
    
    @pytest.mark.asyncio
    async def test_emotion_analyzer_integration(self):
        """감정 분석기 통합 테스트"""
        service = ChatService()
        
        assert service.emotion_analyzer is not None
    
    @pytest.mark.asyncio
    async def test_enhanced_emotion_states(self):
        """확장된 감정 상태 테스트"""
        service = ChatService()
        
        # 새로 추가된 감정들이 있는지 확인
        new_emotions = ["joyful", "supportive", "friendly", "pleased", 
                       "interested", "frustrated", "worried", "neutral"]
        
        for emotion in new_emotions:
            assert emotion in service.emotion_states
    
    @pytest.mark.asyncio
    async def test_contextual_response_generation(self):
        """컨텍스트 기반 응답 생성 테스트"""
        service = ChatService()
        
        # 첫 메시지
        response1 = await service.process_message(
            message="안녕 덱스",
            user_id="context_test_user",
            session_id="context_session"
        )
        
        assert response1 is not None
        assert "context" in response1
        
        # 두 번째 메시지 (컨텍스트 활용)
        response2 = await service.process_message(
            message="저는 김철수예요",
            user_id="context_test_user",
            session_id="context_session"
        )
        
        assert response2 is not None
        assert response2["context"]["total_interactions"] >= 1


@pytest.mark.asyncio
class TestConversationFlow:
    """대화 흐름 테스트"""
    
    async def test_complete_conversation_flow(self):
        """완전한 대화 흐름 테스트"""
        service = ChatService()
        user_id = "flow_test_user"
        session_id = "flow_session"
        
        # 1. 인사
        response1 = await service.process_message("안녕", user_id, session_id)
        assert response1["conversation_type"] == "greeting"
        
        # 2. 자기소개
        response2 = await service.process_message("저는 김철수예요", user_id, session_id)
        assert response2["conversation_type"] == "introduction"
        
        # 3. 질문
        response3 = await service.process_message("넌 뭐 할 수 있어?", user_id, session_id)
        assert response3["conversation_type"] in ["question_about_robot", "question_capabilities"]
        
        # 4. 명령
        response4 = await service.process_message("앞으로 가줘", user_id, session_id)
        assert response4["conversation_type"] == "robot_move_forward"
        
        # 5. 칭찬
        response5 = await service.process_message("잘했어!", user_id, session_id)
        assert response5["conversation_type"] in ["praise", "compliment"]
        
        # 모든 응답이 컨텍스트를 포함해야 함
        for response in [response1, response2, response3, response4, response5]:
            assert "context" in response
            assert "current_topics" in response["context"]
    
    async def test_topic_transition(self):
        """주제 전환 테스트"""
        service = ChatService()
        user_id = "topic_user"
        session_id = "topic_session"
        
        # 로봇 능력 질문
        await service.process_message("뭐 할 수 있어?", user_id, session_id)
        
        # 날씨로 주제 전환
        response = await service.process_message("오늘 날씨 어때?", user_id, session_id)
        
        assert response is not None
        # 주제가 전환되었는지 확인
        assert len(response["context"]["current_topics"]) >= 1

