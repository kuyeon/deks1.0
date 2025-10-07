"""
Deks 1.0 Analytics API 테스트
4순위 작업: 사용자 분석 및 패턴 학습
"""

import pytest
from datetime import datetime, timedelta
from app.services.analytics_service import (
    AnalyticsService,
    CommandFrequency,
    TimeSlotPattern,
    UserBehaviorProfile,
    SmartSuggestion
)
from app.database.database_manager import db_manager


class TestAnalyticsService:
    """Analytics 서비스 테스트"""
    
    @pytest.mark.asyncio
    async def test_analytics_service_initialization(self):
        """Analytics 서비스 초기화 테스트"""
        service = AnalyticsService()
        
        assert service is not None
        assert len(service.time_slots) == 4
        assert len(service.learning_levels) == 3
    
    @pytest.mark.asyncio
    async def test_time_slot_detection(self):
        """시간대 감지 테스트"""
        service = AnalyticsService()
        
        assert service._get_time_slot(8) == "morning"    # 08:00
        assert service._get_time_slot(14) == "afternoon" # 14:00
        assert service._get_time_slot(20) == "evening"   # 20:00
        assert service._get_time_slot(1) == "night"      # 01:00
    
    @pytest.mark.asyncio
    async def test_learning_level_determination(self):
        """학습 레벨 결정 테스트"""
        service = AnalyticsService()
        
        assert service._determine_learning_level(5) == "beginner"
        assert service._determine_learning_level(50) == "intermediate"
        assert service._determine_learning_level(150) == "advanced"
    
    @pytest.mark.asyncio
    async def test_command_frequency_dataclass(self):
        """CommandFrequency 데이터클래스 테스트"""
        freq = CommandFrequency(
            command="move_forward",
            count=10,
            success_count=9,
            failure_count=1,
            success_rate=90.0,
            last_used=datetime.now(),
            avg_execution_time=0.5
        )
        
        assert freq.command == "move_forward"
        assert freq.success_rate == 90.0
        assert freq.count == 10
    
    @pytest.mark.asyncio
    async def test_time_slot_pattern_dataclass(self):
        """TimeSlotPattern 데이터클래스 테스트"""
        pattern = TimeSlotPattern(
            time_slot="morning",
            command_count=15,
            most_common_command="move_forward",
            avg_satisfaction=4.2
        )
        
        assert pattern.time_slot == "morning"
        assert pattern.command_count == 15
        assert pattern.avg_satisfaction == 4.2
    
    @pytest.mark.asyncio
    async def test_user_behavior_profile_dataclass(self):
        """UserBehaviorProfile 데이터클래스 테스트"""
        profile = UserBehaviorProfile(
            user_id="test_user",
            total_interactions=50,
            total_commands=30,
            favorite_commands=["move_forward", "turn_right"],
            command_success_rate=95.0,
            avg_session_duration=300.0,
            most_active_time_slot="evening",
            learning_level="intermediate",
            preferences={"style": "casual"}
        )
        
        assert profile.user_id == "test_user"
        assert profile.learning_level == "intermediate"
        assert len(profile.favorite_commands) == 2
    
    @pytest.mark.asyncio
    async def test_smart_suggestion_dataclass(self):
        """SmartSuggestion 데이터클래스 테스트"""
        suggestion = SmartSuggestion(
            command="move_forward",
            confidence=0.85,
            reason="자주 사용하는 명령입니다",
            category="frequency_based"
        )
        
        assert suggestion.command == "move_forward"
        assert suggestion.confidence == 0.85
        assert suggestion.category == "frequency_based"


class TestErrorFixSuggestions:
    """에러 수정 제안 테스트"""
    
    @pytest.mark.asyncio
    async def test_connection_error_suggestions(self):
        """연결 에러 제안 테스트"""
        service = AnalyticsService()
        
        suggestions = service._generate_error_fix_suggestions(
            "move_forward",
            "로봇 연결이 끊어졌습니다"
        )
        
        assert len(suggestions) > 0
        assert any("연결" in s for s in suggestions)
    
    @pytest.mark.asyncio
    async def test_timeout_error_suggestions(self):
        """타임아웃 에러 제안 테스트"""
        service = AnalyticsService()
        
        suggestions = service._generate_error_fix_suggestions(
            "turn_left",
            "명령 타임아웃 발생"
        )
        
        assert len(suggestions) > 0
        assert any("다시 시도" in s or "기다려" in s for s in suggestions)
    
    @pytest.mark.asyncio
    async def test_parameter_error_suggestions(self):
        """파라미터 에러 제안 테스트"""
        service = AnalyticsService()
        
        suggestions = service._generate_error_fix_suggestions(
            "move_forward",
            "유효하지 않은 파라미터"
        )
        
        assert len(suggestions) > 0
        assert any("형식" in s or "값" in s for s in suggestions)


class TestGlobalStatistics:
    """전체 통계 테스트"""
    
    @pytest.mark.asyncio
    async def test_get_global_statistics(self):
        """전체 통계 조회 테스트"""
        service = AnalyticsService()
        
        stats = await service.get_global_statistics()
        
        assert "total_users" in stats
        assert "total_commands" in stats
        assert "success_rate" in stats
        assert "most_popular_command" in stats
        assert "error_rate" in stats
        assert "timestamp" in stats
    
    @pytest.mark.asyncio
    async def test_statistics_data_types(self):
        """통계 데이터 타입 테스트"""
        service = AnalyticsService()
        
        stats = await service.get_global_statistics()
        
        assert isinstance(stats["total_users"], int)
        assert isinstance(stats["total_commands"], int)
        assert isinstance(stats["success_rate"], (int, float))
        assert isinstance(stats["error_rate"], (int, float))


class TestUserStatistics:
    """사용자 통계 테스트"""
    
    @pytest.mark.asyncio
    async def test_get_user_statistics(self):
        """사용자 통계 조회 테스트"""
        service = AnalyticsService()
        
        stats = await service.get_user_statistics("test_user")
        
        assert "user_id" in stats
        assert "total_interactions" in stats
        assert "total_commands" in stats
        assert "success_rate" in stats
        assert "learning_level" in stats
        assert stats["user_id"] == "test_user"
    
    @pytest.mark.asyncio
    async def test_learning_level_in_stats(self):
        """통계에 학습 레벨 포함 테스트"""
        service = AnalyticsService()
        
        stats = await service.get_user_statistics("test_user")
        
        assert stats["learning_level"] in ["beginner", "intermediate", "advanced"]


@pytest.mark.asyncio
class TestSmartSuggestions:
    """스마트 제안 테스트"""
    
    async def test_generate_smart_suggestions(self):
        """스마트 제안 생성 테스트"""
        service = AnalyticsService()
        
        suggestions = await service.generate_smart_suggestions(
            user_id="test_user",
            context="idle",
            limit=5
        )
        
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 5
    
    async def test_suggestion_structure(self):
        """제안 구조 테스트"""
        service = AnalyticsService()
        
        suggestions = await service.generate_smart_suggestions(
            user_id="test_user",
            limit=3
        )
        
        if suggestions:
            sug = suggestions[0]
            assert isinstance(sug, SmartSuggestion)
            assert hasattr(sug, 'command')
            assert hasattr(sug, 'confidence')
            assert hasattr(sug, 'reason')
            assert hasattr(sug, 'category')
    
    async def test_suggestion_confidence_range(self):
        """제안 신뢰도 범위 테스트"""
        service = AnalyticsService()
        
        suggestions = await service.generate_smart_suggestions(
            user_id="test_user",
            limit=5
        )
        
        for sug in suggestions:
            assert 0.0 <= sug.confidence <= 1.0


class TestParameterValidation:
    """파라미터 검증 테스트"""
    
    @pytest.mark.asyncio
    async def test_invalid_days_parameter(self):
        """유효하지 않은 days 파라미터 테스트"""
        service = AnalyticsService()
        
        with pytest.raises(Exception):  # InvalidParameterException
            await service.analyze_user_behavior("test_user", days=0)
    
    @pytest.mark.asyncio
    async def test_negative_days_parameter(self):
        """음수 days 파라미터 테스트"""
        service = AnalyticsService()
        
        with pytest.raises(Exception):
            await service.analyze_user_behavior("test_user", days=-5)


class TestAnalyticsIntegration:
    """Analytics API 통합 테스트"""
    
    def test_analytics_router_exists(self):
        """Analytics 라우터 존재 확인"""
        from app.api.v1.endpoints import analytics
        
        assert analytics.router is not None
    
    def test_all_endpoints_defined(self):
        """모든 엔드포인트 정의 확인"""
        from app.api.v1.endpoints import analytics
        
        routes = [route.path for route in analytics.router.routes]
        
        expected_routes = [
            "/user-patterns",
            "/suggestions",
            "/feedback",
            "/statistics",
            "/user-stats/{user_id}",
            "/command-frequency",
            "/error-patterns",
            "/health"
        ]
        
        for expected in expected_routes:
            assert any(expected in route for route in routes), f"Missing route: {expected}"

