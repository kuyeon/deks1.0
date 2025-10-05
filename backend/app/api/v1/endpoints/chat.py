"""
채팅 상호작용 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from loguru import logger
import time
import uuid
from datetime import datetime

from app.database.database_manager import db_manager
from app.services.chat_service import ChatService

router = APIRouter()

# 채팅 서비스 인스턴스
chat_service = ChatService()


# 요청/응답 모델
class ChatMessageRequest(BaseModel):
    """채팅 메시지 요청 모델"""
    message: str
    user_id: str = "default_user"
    session_id: Optional[str] = None


class ChatMessageResponse(BaseModel):
    """채팅 메시지 응답 모델"""
    success: bool
    message_id: str
    response: str
    emotion: str
    conversation_type: str
    timestamp: str
    context: Optional[Dict[str, Any]] = None
    nlp_analysis: Optional[Dict[str, Any]] = None


class ChatHistoryResponse(BaseModel):
    """채팅 기록 응답 모델"""
    success: bool
    conversations: List[Dict[str, Any]]
    total_count: int
    has_more: bool


class ChatContextResponse(BaseModel):
    """채팅 컨텍스트 응답 모델"""
    success: bool
    context: Dict[str, Any]


class EmotionUpdateRequest(BaseModel):
    """감정 상태 업데이트 요청 모델"""
    emotion: str
    user_id: str
    reason: Optional[str] = None


class EmotionUpdateResponse(BaseModel):
    """감정 상태 업데이트 응답 모델"""
    success: bool
    emotion_updated: str
    led_expression: str
    buzzer_sound: str
    timestamp: str


class LearningDataRequest(BaseModel):
    """학습 데이터 요청 모델"""
    user_id: str
    interaction_data: Dict[str, Any]


# API 엔드포인트
@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(request: ChatMessageRequest):
    """
    채팅 메시지를 전송하고 로봇의 응답을 받습니다.
    
    Args:
        request: 채팅 메시지 요청
        
    Returns:
        ChatMessageResponse: 로봇의 응답과 컨텍스트 정보
    """
    try:
        logger.info(f"채팅 메시지 수신: {request.message} (사용자: {request.user_id})")
        
        # 세션 ID 생성 (없는 경우)
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        
        # 채팅 서비스를 통해 응답 생성
        response_data = await chat_service.process_message(
            message=request.message,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        return ChatMessageResponse(
            success=True,
            message_id=response_data["message_id"],
            response=response_data["response"],
            emotion=response_data["emotion"],
            conversation_type=response_data["conversation_type"],
            timestamp=response_data["timestamp"],
            context=response_data.get("context"),
            nlp_analysis=response_data.get("nlp_analysis")
        )
        
    except Exception as e:
        logger.error(f"채팅 메시지 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=f"채팅 메시지 처리 중 오류가 발생했습니다: {str(e)}")


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    user_id: str = Query(..., description="사용자 ID"),
    limit: int = Query(20, description="조회할 대화 수"),
    offset: int = Query(0, description="시작 위치")
):
    """
    사용자의 채팅 기록을 조회합니다.
    
    Args:
        user_id: 사용자 ID
        limit: 조회할 대화 수
        offset: 시작 위치
        
    Returns:
        ChatHistoryResponse: 채팅 기록 목록
    """
    try:
        logger.info(f"채팅 기록 조회: 사용자 {user_id}, limit={limit}, offset={offset}")
        
        # 데이터베이스에서 채팅 기록 조회
        conversations = await chat_service.get_chat_history(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        total_count = await chat_service.get_chat_count(user_id)
        
        return ChatHistoryResponse(
            success=True,
            conversations=conversations,
            total_count=total_count,
            has_more=(offset + limit) < total_count
        )
        
    except Exception as e:
        logger.error(f"채팅 기록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"채팅 기록 조회 중 오류가 발생했습니다: {str(e)}")


@router.get("/context", response_model=ChatContextResponse)
async def get_chat_context(
    user_id: str = Query(..., description="사용자 ID"),
    session_id: Optional[str] = Query(None, description="세션 ID")
):
    """
    사용자의 채팅 컨텍스트를 조회합니다.
    
    Args:
        user_id: 사용자 ID
        session_id: 세션 ID (선택사항)
        
    Returns:
        ChatContextResponse: 채팅 컨텍스트 정보
    """
    try:
        logger.info(f"채팅 컨텍스트 조회: 사용자 {user_id}, 세션 {session_id}")
        
        # 채팅 서비스에서 컨텍스트 조회
        context = await chat_service.get_chat_context(
            user_id=user_id,
            session_id=session_id
        )
        
        return ChatContextResponse(
            success=True,
            context=context
        )
        
    except Exception as e:
        logger.error(f"채팅 컨텍스트 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"채팅 컨텍스트 조회 중 오류가 발생했습니다: {str(e)}")


@router.post("/emotion", response_model=EmotionUpdateResponse)
async def update_emotion(request: EmotionUpdateRequest):
    """
    로봇의 감정 상태를 업데이트합니다.
    
    Args:
        request: 감정 상태 업데이트 요청
        
    Returns:
        EmotionUpdateResponse: 업데이트된 감정 상태 정보
    """
    try:
        logger.info(f"감정 상태 업데이트: {request.emotion} (사용자: {request.user_id})")
        
        # 감정 상태 업데이트
        emotion_data = await chat_service.update_emotion(
            emotion=request.emotion,
            user_id=request.user_id,
            reason=request.reason
        )
        
        return EmotionUpdateResponse(
            success=True,
            emotion_updated=emotion_data["emotion"],
            led_expression=emotion_data["led_expression"],
            buzzer_sound=emotion_data["buzzer_sound"],
            timestamp=emotion_data["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"감정 상태 업데이트 실패: {e}")
        raise HTTPException(status_code=500, detail=f"감정 상태 업데이트 중 오류가 발생했습니다: {str(e)}")


@router.post("/learning")
async def update_learning_data(request: LearningDataRequest):
    """
    사용자 상호작용 데이터를 학습 시스템에 업데이트합니다.
    
    Args:
        request: 학습 데이터 요청
        
    Returns:
        dict: 학습 결과
    """
    try:
        logger.info(f"학습 데이터 업데이트: 사용자 {request.user_id}")
        
        # 학습 데이터 업데이트
        result = await chat_service.update_learning_data(
            user_id=request.user_id,
            interaction_data=request.interaction_data
        )
        
        return {
            "success": True,
            "message": "학습 데이터가 성공적으로 업데이트되었습니다",
            "learning_result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"학습 데이터 업데이트 실패: {e}")
        raise HTTPException(status_code=500, detail=f"학습 데이터 업데이트 중 오류가 발생했습니다: {str(e)}")


@router.get("/patterns")
async def get_conversation_patterns():
    """
    지원하는 대화 패턴을 조회합니다.
    
    Returns:
        dict: 대화 패턴 목록
    """
    try:
        logger.info("대화 패턴 조회")
        
        patterns = await chat_service.get_conversation_patterns()
        
        return {
            "success": True,
            "patterns": patterns,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"대화 패턴 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"대화 패턴 조회 중 오류가 발생했습니다: {str(e)}")


@router.get("/emotions")
async def get_emotion_states():
    """
    지원하는 감정 상태를 조회합니다.
    
    Returns:
        dict: 감정 상태 목록
    """
    try:
        logger.info("감정 상태 조회")
        
        emotions = await chat_service.get_emotion_states()
        
        return {
            "success": True,
            "emotions": emotions,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"감정 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"감정 상태 조회 중 오류가 발생했습니다: {str(e)}")
