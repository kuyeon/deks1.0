"""
표현 제어 API 엔드포인트 (LED, 버저)
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from loguru import logger

router = APIRouter()


# 요청 모델
class LEDExpressionRequest(BaseModel):
    """LED 표정 설정 요청 모델"""
    expression: str
    duration: int = 3000  # 밀리초
    user_id: str = "default_user"


class BuzzerRequest(BaseModel):
    """버저 소리 제어 요청 모델"""
    sound: str
    frequency: int = 1000
    duration: int = 500
    user_id: str = "default_user"


# 지원하는 표현과 소리
SUPPORTED_EXPRESSIONS = ["happy", "sad", "surprised", "neutral", "heart"]
SUPPORTED_SOUNDS = ["beep", "melody", "alarm", "success", "error"]


@router.post("/led")
async def set_led_expression(request: LEDExpressionRequest):
    """LED 표정을 설정합니다."""
    try:
        if request.expression not in SUPPORTED_EXPRESSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"지원하지 않는 표정입니다. 지원 표정: {SUPPORTED_EXPRESSIONS}"
            )
        
        logger.info(f"LED 표정 설정: {request.expression} ({request.duration}ms)")
        
        # TODO: Socket Bridge를 통해 ESP32에 LED 명령 전송
        
        return {
            "success": True,
            "message": f"LED 표정을 '{request.expression}'으로 설정했습니다",
            "expression": request.expression,
            "duration": request.duration,
            "command_id": f"led_{hash(str(request)) % 10000}",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LED 표정 설정 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"LED 표정 설정 실패: {str(e)}")


@router.post("/buzzer")
async def set_buzzer_sound(request: BuzzerRequest):
    """버저 소리를 설정합니다."""
    try:
        if request.sound not in SUPPORTED_SOUNDS:
            raise HTTPException(
                status_code=400,
                detail=f"지원하지 않는 소리입니다. 지원 소리: {SUPPORTED_SOUNDS}"
            )
        
        logger.info(f"버저 소리 설정: {request.sound} ({request.frequency}Hz, {request.duration}ms)")
        
        # TODO: Socket Bridge를 통해 ESP32에 버저 명령 전송
        
        return {
            "success": True,
            "message": f"버저 소리를 '{request.sound}'으로 설정했습니다",
            "sound": request.sound,
            "frequency": request.frequency,
            "duration": request.duration,
            "command_id": f"buzzer_{hash(str(request)) % 10000}",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"버저 소리 설정 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"버저 소리 설정 실패: {str(e)}")


@router.get("/expressions")
async def get_supported_expressions():
    """지원하는 LED 표정 목록을 조회합니다."""
    try:
        logger.info("지원 LED 표정 목록 조회 요청")
        
        return {
            "success": True,
            "supported_expressions": SUPPORTED_EXPRESSIONS,
            "descriptions": {
                "happy": "행복한 표정",
                "sad": "슬픈 표정", 
                "surprised": "놀란 표정",
                "neutral": "평범한 표정",
                "heart": "하트 표정"
            },
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"지원 표정 목록 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"표정 목록 조회 실패: {str(e)}")


@router.get("/sounds")
async def get_supported_sounds():
    """지원하는 버저 소리 목록을 조회합니다."""
    try:
        logger.info("지원 버저 소리 목록 조회 요청")
        
        return {
            "success": True,
            "supported_sounds": SUPPORTED_SOUNDS,
            "descriptions": {
                "beep": "기본 비프음",
                "melody": "멜로디",
                "alarm": "경보음",
                "success": "성공음",
                "error": "에러음"
            },
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"지원 소리 목록 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"소리 목록 조회 실패: {str(e)}")


@router.get("/health")
async def expression_health_check():
    """표현 제어 모듈 헬스 체크"""
    return {
        "status": "healthy",
        "module": "expression",
        "supported_expressions": len(SUPPORTED_EXPRESSIONS),
        "supported_sounds": len(SUPPORTED_SOUNDS)
    }
