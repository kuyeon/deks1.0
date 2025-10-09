"""
사용자 분석 및 패턴 학습 API 엔드포인트
4순위 작업: Analytics API 구현
"""

from fastapi import APIRouter, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from loguru import logger

from app.database.database_manager import db_manager
from app.services.analytics_service import get_analytics_service

router = APIRouter()


# 응답 모델
class FrequentCommand(BaseModel):
    """자주 사용하는 명령 모델"""
    command: str
    frequency: int
    success_rate: float


class ErrorPattern(BaseModel):
    """에러 패턴 모델"""
    error_type: str
    frequency: int
    suggestions: List[str]


class UserPatternAnalysis(BaseModel):
    """사용자 패턴 분석 모델"""
    user_id: str
    analysis_period: str
    frequent_commands: List[FrequentCommand]
    preferred_time_slots: List[str]
    common_error_patterns: List[ErrorPattern]
    timestamp: str


class Suggestion(BaseModel):
    """스마트 제안 모델"""
    command: str
    confidence: float
    reason: str


class SmartSuggestionsResponse(BaseModel):
    """스마트 제안 응답 모델"""
    user_id: str
    context: str
    suggestions: List[Suggestion]
    timestamp: str


class FeedbackRequest(BaseModel):
    """피드백 요청 모델"""
    user_id: str
    command_id: str
    satisfaction: int  # 1-5
    feedback: Optional[str] = None
    timestamp: Optional[str] = None


@router.get("/user-patterns")
async def get_user_patterns(
    user_id: str = Query(..., description="사용자 ID"),
    days: int = Query(default=7, ge=1, le=365, description="분석 기간 (일)")
):
    """사용자 패턴을 분석합니다."""
    logger.info(f"사용자 패턴 분석 요청: {user_id} ({days}일)")
    
    analytics_service = await get_analytics_service()
    
    # 사용자 행동 분석
    behavior_profile = await analytics_service.analyze_user_behavior(user_id, days)
    
    # 명령 빈도 분석
    command_frequencies = await analytics_service.get_command_frequency_analysis(user_id, limit=10)
    
    # 시간대별 패턴 분석
    time_patterns = await analytics_service.analyze_time_slot_patterns(user_id, days)
    
    # 에러 패턴 분석
    error_patterns = await analytics_service.analyze_error_patterns(user_id, days)
    
    return {
        "success": True,
        "user_id": user_id,
        "analysis_period": f"{days}_days",
        "behavior_profile": {
            "total_interactions": behavior_profile.total_interactions,
            "total_commands": behavior_profile.total_commands,
            "success_rate": behavior_profile.command_success_rate,
            "learning_level": behavior_profile.learning_level,
            "most_active_time": behavior_profile.most_active_time_slot,
            "avg_session_duration": behavior_profile.avg_session_duration
        },
        "frequent_commands": [
            {
                "command": freq.command,
                "frequency": freq.count,
                "success_rate": freq.success_rate
            }
            for freq in command_frequencies
        ],
        "time_slot_patterns": [
            {
                "time_slot": pattern.time_slot,
                "command_count": pattern.command_count,
                "most_common_command": pattern.most_common_command
            }
            for pattern in time_patterns
        ],
        "error_patterns": error_patterns,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/suggestions", response_model=SmartSuggestionsResponse)
async def get_smart_suggestions(
    user_id: str = Query(..., description="사용자 ID"),
    context: str = Query(default="idle", description="상황 컨텍스트"),
    limit: int = Query(default=5, ge=1, le=10, description="제안 개수")
):
    """스마트 제안을 제공합니다."""
    logger.info(f"스마트 제안 요청: {user_id} (컨텍스트: {context})")
    
    analytics_service = await get_analytics_service()
    
    # 스마트 제안 생성 (빈도, 시간대, 에러 방지, 시퀀스 기반)
    suggestions = await analytics_service.generate_smart_suggestions(
        user_id=user_id,
        context=context,
        limit=limit
    )
    
    return SmartSuggestionsResponse(
        user_id=user_id,
        context=context,
        suggestions=[
            Suggestion(
                command=sug.command,
                confidence=sug.confidence,
                reason=sug.reason
            )
            for sug in suggestions
        ],
        timestamp=datetime.now().isoformat()
    )


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """사용자 피드백을 제출합니다."""
    logger.info(f"피드백 제출: {request.user_id} - 만족도: {request.satisfaction}")
    
    # 피드백 데이터베이스에 저장
    feedback_id = f"fb_{datetime.now().timestamp():.0f}"
    
    query = """
    INSERT INTO user_feedback 
    (feedback_id, user_id, command_id, satisfaction, feedback, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    
    db_manager.execute_query(query, (
        feedback_id,
        request.user_id,
        request.command_id,
        request.satisfaction,
        request.feedback,
        request.timestamp or datetime.now().isoformat()
    ))
    
    logger.info(f"피드백 저장 완료: {feedback_id}")
    
    return {
        "success": True,
        "message": "피드백이 성공적으로 제출되었습니다",
        "feedback_id": feedback_id,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/statistics")
async def get_analytics_statistics():
    """전체 분석 통계를 조회합니다."""
    logger.info("분석 통계 조회 요청")
    
    analytics_service = await get_analytics_service()
    
    # 전체 시스템 통계 조회
    global_stats = await analytics_service.get_global_statistics()
    
    return {
        "success": True,
        "statistics": global_stats,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/user-stats/{user_id}")
async def get_user_statistics(
    user_id: str,
    include_details: bool = Query(default=False, description="상세 정보 포함 여부")
):
    """특정 사용자의 상세 통계를 조회합니다."""
    logger.info(f"사용자 통계 조회: {user_id}")
    
    analytics_service = await get_analytics_service()
    
    # 사용자 통계
    user_stats = await analytics_service.get_user_statistics(user_id)
    
    result = {
        "success": True,
        "user_stats": user_stats,
        "timestamp": datetime.now().isoformat()
    }
    
    # 상세 정보 포함
    if include_details:
        command_frequencies = await analytics_service.get_command_frequency_analysis(
            user_id, limit=5
        )
        
        result["command_frequencies"] = [
            {
                "command": freq.command,
                "count": freq.count,
                "success_rate": freq.success_rate
            }
            for freq in command_frequencies
        ]
    
    return result


@router.get("/command-frequency")
async def get_command_frequency(
    user_id: str = Query(..., description="사용자 ID"),
    limit: int = Query(default=10, ge=1, le=50, description="결과 개수")
):
    """명령 빈도를 조회합니다."""
    logger.info(f"명령 빈도 조회: {user_id}")
    
    analytics_service = await get_analytics_service()
    
    frequencies = await analytics_service.get_command_frequency_analysis(
        user_id, limit
    )
    
    return {
        "success": True,
        "user_id": user_id,
        "command_frequencies": [
            {
                "command": freq.command,
                "count": freq.count,
                "success_count": freq.success_count,
                "failure_count": freq.failure_count,
                "success_rate": freq.success_rate,
                "last_used": freq.last_used.isoformat(),
                "avg_execution_time": freq.avg_execution_time
            }
            for freq in frequencies
        ],
        "timestamp": datetime.now().isoformat()
    }


@router.get("/error-patterns")
async def get_error_patterns(
    user_id: Optional[str] = Query(None, description="사용자 ID (선택)"),
    days: int = Query(default=7, ge=1, le=90, description="분석 기간")
):
    """에러 패턴을 분석합니다."""
    logger.info(f"에러 패턴 분석: user_id={user_id}, days={days}")
    
    analytics_service = await get_analytics_service()
    
    error_patterns = await analytics_service.analyze_error_patterns(user_id, days)
    
    return {
        "success": True,
        "user_id": user_id or "all",
        "analysis_period": f"{days}_days",
        "error_patterns": error_patterns,
        "total_errors": sum(p['frequency'] for p in error_patterns),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/health")
async def analytics_health_check():
    """분석 모듈 헬스 체크"""
    return {
        "status": "healthy",
        "module": "analytics",
        "features": ["user_patterns", "smart_suggestions", "feedback_analysis"]
    }
