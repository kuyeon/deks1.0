"""
표현 제어 API 엔드포인트 (LED, 버저) - 고도화 버전
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from loguru import logger
from datetime import datetime

router = APIRouter()


# 요청 모델
class LEDExpressionRequest(BaseModel):
    """LED 표정 설정 요청 모델"""
    expression: str = Field(..., description="표정 타입")
    duration: int = Field(3000, ge=100, le=30000, description="지속시간 (밀리초)")
    brightness: int = Field(100, ge=0, le=100, description="밝기 (0-100%)")
    animation: Optional[str] = Field(None, description="애니메이션 효과")
    user_id: str = Field("default_user", description="사용자 ID")


class BuzzerRequest(BaseModel):
    """버저 소리 제어 요청 모델"""
    sound: str = Field(..., description="소리 타입")
    frequency: int = Field(1000, ge=200, le=5000, description="주파수 (Hz)")
    duration: int = Field(500, ge=50, le=5000, description="지속시간 (밀리초)")
    volume: int = Field(80, ge=0, le=100, description="볼륨 (0-100%)")
    melody: Optional[List[int]] = Field(None, description="커스텀 멜로디 (주파수 리스트)")
    user_id: str = Field("default_user", description="사용자 ID")


class EmotionExpressionRequest(BaseModel):
    """감정 기반 표현 요청 모델"""
    emotion: str = Field(..., description="감정 상태")
    intensity: float = Field(1.0, ge=0.0, le=1.0, description="감정 강도")
    user_id: str = Field("default_user", description="사용자 ID")


class PatternRequest(BaseModel):
    """패턴 생성/수정 요청 모델"""
    pattern_name: str = Field(..., description="패턴 이름")
    pattern_type: str = Field(..., description="패턴 타입 (led/buzzer)")
    pattern_data: Dict[str, Any] = Field(..., description="패턴 데이터")
    user_id: str = Field("default_user", description="사용자 ID")


# 지원하는 표현과 소리 (확장)
SUPPORTED_EXPRESSIONS = {
    "basic": ["happy", "sad", "angry", "surprised", "neutral", "heart", "wink", "sleepy"],
    "status": ["waiting", "working", "error", "success", "thinking", "listening"],
    "animation": ["blink", "fade", "rainbow", "wave", "pulse", "sparkle"]
}

SUPPORTED_SOUNDS = {
    "notification": ["beep", "success", "error", "warning", "info"],
    "melody": ["melody", "startup", "shutdown", "waiting", "thinking", "celebration"],
    "alarm": ["alert", "emergency", "low_battery", "connection_lost"]
}

# 감정별 표현 매핑
EMOTION_EXPRESSIONS = {
    "happy": {"expression": "happy", "animation": "sparkle", "sound": "success"},
    "sad": {"expression": "sad", "animation": "fade", "sound": "error"},
    "angry": {"expression": "angry", "animation": "pulse", "sound": "warning"},
    "surprised": {"expression": "surprised", "animation": "blink", "sound": "beep"},
    "neutral": {"expression": "neutral", "animation": None, "sound": None},
    "excited": {"expression": "happy", "animation": "rainbow", "sound": "celebration"},
    "confused": {"expression": "thinking", "animation": "wave", "sound": "thinking"},
    "sleepy": {"expression": "sleepy", "animation": "fade", "sound": None}
}


@router.post("/led")
async def set_led_expression(request: LEDExpressionRequest):
    """LED 표정을 설정합니다."""
    try:
        # 지원하는 표정인지 확인
        all_expressions = []
        for category in SUPPORTED_EXPRESSIONS.values():
            all_expressions.extend(category)
        
        if request.expression not in all_expressions:
            raise HTTPException(
                status_code=400, 
                detail=f"지원하지 않는 표정입니다. 지원 표정: {all_expressions}"
            )
        
        # 애니메이션 검증
        if request.animation and request.animation not in SUPPORTED_EXPRESSIONS["animation"]:
            raise HTTPException(
                status_code=400, 
                detail=f"지원하지 않는 애니메이션입니다. 지원 애니메이션: {SUPPORTED_EXPRESSIONS['animation']}"
            )
        
        logger.info(f"LED 표정 설정: {request.expression} (밝기: {request.brightness}%, 지속: {request.duration}ms, 애니메이션: {request.animation})")
        
        # TODO: Socket Bridge를 통해 ESP32에 LED 명령 전송
        # led_command = {
        #     "type": "led_expression",
        #     "expression": request.expression,
        #     "brightness": request.brightness,
        #     "duration": request.duration,
        #     "animation": request.animation,
        #     "timestamp": datetime.now().isoformat()
        # }
        # await send_to_esp32(led_command)
        
        return {
            "success": True,
            "message": f"LED 표정을 '{request.expression}'으로 설정했습니다",
            "expression": request.expression,
            "brightness": request.brightness,
            "duration": request.duration,
            "animation": request.animation,
            "command_id": f"led_{hash(str(request)) % 10000}",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LED 표정 설정 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"LED 표정 설정 실패: {str(e)}") from e


@router.post("/buzzer")
async def set_buzzer_sound(request: BuzzerRequest):
    """버저 소리를 설정합니다."""
    try:
        # 지원하는 소리인지 확인
        all_sounds = []
        for category in SUPPORTED_SOUNDS.values():
            all_sounds.extend(category)
        
        if request.sound not in all_sounds:
            raise HTTPException(
                status_code=400,
                detail=f"지원하지 않는 소리입니다. 지원 소리: {all_sounds}"
            )
        
        # 커스텀 멜로디 검증
        if request.melody:
            if len(request.melody) > 20:  # 최대 20개 음표
                raise HTTPException(
                    status_code=400,
                    detail="멜로디는 최대 20개 음표까지 지원합니다"
                )
            for freq in request.melody:
                if not (200 <= freq <= 5000):
                    raise HTTPException(
                        status_code=400,
                        detail="멜로디 주파수는 200-5000Hz 범위여야 합니다"
                    )
        
        logger.info(f"버저 소리 설정: {request.sound} (주파수: {request.frequency}Hz, 볼륨: {request.volume}%, 지속: {request.duration}ms)")
        
        # TODO: Socket Bridge를 통해 ESP32에 버저 명령 전송
        # buzzer_command = {
        #     "type": "buzzer_sound",
        #     "sound": request.sound,
        #     "frequency": request.frequency,
        #     "volume": request.volume,
        #     "duration": request.duration,
        #     "melody": request.melody,
        #     "timestamp": datetime.now().isoformat()
        # }
        # await send_to_esp32(buzzer_command)
        
        return {
            "success": True,
            "message": f"버저 소리를 '{request.sound}'으로 설정했습니다",
            "sound": request.sound,
            "frequency": request.frequency,
            "volume": request.volume,
            "duration": request.duration,
            "melody": request.melody,
            "command_id": f"buzzer_{hash(str(request)) % 10000}",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"버저 소리 설정 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"버저 소리 설정 실패: {str(e)}") from e


@router.post("/emotion")
async def express_emotion(request: EmotionExpressionRequest):
    """감정에 따른 자동 표현을 설정합니다."""
    try:
        if request.emotion not in EMOTION_EXPRESSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"지원하지 않는 감정입니다. 지원 감정: {list(EMOTION_EXPRESSIONS.keys())}"
            )
        
        emotion_config = EMOTION_EXPRESSIONS[request.emotion]
        
        # 감정 강도에 따른 조정
        # duration = int(3000 * request.intensity)  # 강도에 비례한 지속시간
        # brightness = int(100 * request.intensity)  # 강도에 비례한 밝기
        
        logger.info(f"감정 표현: {request.emotion} (강도: {request.intensity})")
        
        # LED 표현
        if emotion_config["expression"]:
            # led_command = {
            #     "type": "led_expression",
            #     "expression": emotion_config["expression"],
            #     "brightness": brightness,
            #     "duration": duration,
            #     "animation": emotion_config["animation"],
            #     "timestamp": datetime.now().isoformat()
            # }
            # await send_to_esp32(led_command)
            pass
        
        # 버저 소리
        if emotion_config["sound"]:
            # buzzer_command = {
            #     "type": "buzzer_sound",
            #     "sound": emotion_config["sound"],
            #     "frequency": 1000,
            #     "volume": int(80 * request.intensity),
            #     "duration": int(500 * request.intensity),
            #     "timestamp": datetime.now().isoformat()
            # }
            # await send_to_esp32(buzzer_command)
            pass
        
        return {
            "success": True,
            "message": f"감정 '{request.emotion}'을 표현했습니다",
            "emotion": request.emotion,
            "intensity": request.intensity,
            "expression": emotion_config["expression"],
            "animation": emotion_config["animation"],
            "sound": emotion_config["sound"],
            "command_id": f"emotion_{hash(str(request)) % 10000}",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"감정 표현 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"감정 표현 실패: {str(e)}") from e


@router.post("/pattern")
async def create_pattern(request: PatternRequest):
    """사용자 정의 패턴을 생성합니다."""
    try:
        if request.pattern_type not in ["led", "buzzer"]:
            raise HTTPException(
                status_code=400,
                detail="패턴 타입은 'led' 또는 'buzzer'여야 합니다"
            )
        
        # 패턴 데이터 검증
        if request.pattern_type == "led":
            required_fields = ["expression", "duration"]
            if not all(field in request.pattern_data for field in required_fields):
                raise HTTPException(
                    status_code=400,
                    detail=f"LED 패턴에는 {required_fields} 필드가 필요합니다"
                )
        elif request.pattern_type == "buzzer":
            required_fields = ["sound", "frequency", "duration"]
            if not all(field in request.pattern_data for field in required_fields):
                raise HTTPException(
                    status_code=400,
                    detail=f"버저 패턴에는 {required_fields} 필드가 필요합니다"
                )
        
        logger.info(f"사용자 패턴 생성: {request.pattern_name} ({request.pattern_type})")
        
        # TODO: 패턴을 데이터베이스에 저장
        # await save_user_pattern(request.pattern_name, request.pattern_type, request.pattern_data, request.user_id)
        
        return {
            "success": True,
            "message": f"패턴 '{request.pattern_name}'을 생성했습니다",
            "pattern_name": request.pattern_name,
            "pattern_type": request.pattern_type,
            "pattern_data": request.pattern_data,
            "command_id": f"pattern_{hash(str(request)) % 10000}",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"패턴 생성 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"패턴 생성 실패: {str(e)}") from e


@router.get("/expressions")
async def get_supported_expressions():
    """지원하는 LED 표정 목록을 조회합니다."""
    try:
        logger.info("지원 LED 표정 목록 조회 요청")
        
        descriptions = {
            "happy": "행복한 표정", "sad": "슬픈 표정", "angry": "화난 표정",
            "surprised": "놀란 표정", "neutral": "평범한 표정", "heart": "하트 표정",
            "wink": "윙크 표정", "sleepy": "졸린 표정", "waiting": "대기 상태",
            "working": "작업 중", "error": "에러 상태", "success": "성공 상태",
            "thinking": "생각 중", "listening": "듣는 중"
        }
        
        return {
            "success": True,
            "supported_expressions": SUPPORTED_EXPRESSIONS,
            "descriptions": descriptions,
            "total_count": sum(len(category) for category in SUPPORTED_EXPRESSIONS.values()),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"지원 표정 목록 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"표정 목록 조회 실패: {str(e)}") from e


@router.get("/sounds")
async def get_supported_sounds():
    """지원하는 버저 소리 목록을 조회합니다."""
    try:
        logger.info("지원 버저 소리 목록 조회 요청")
        
        descriptions = {
            "beep": "기본 비프음", "success": "성공음", "error": "에러음",
            "warning": "경고음", "info": "정보음", "startup": "시작 멜로디",
            "shutdown": "종료 멜로디", "waiting": "대기 멜로디", "thinking": "생각 멜로디",
            "celebration": "축하 멜로디", "alert": "알림음", "emergency": "비상음",
            "low_battery": "배터리 부족", "connection_lost": "연결 끊김"
        }
        
        return {
            "success": True,
            "supported_sounds": SUPPORTED_SOUNDS,
            "descriptions": descriptions,
            "total_count": sum(len(category) for category in SUPPORTED_SOUNDS.values()),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"지원 소리 목록 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"소리 목록 조회 실패: {str(e)}") from e


@router.get("/emotions")
async def get_supported_emotions():
    """지원하는 감정 목록을 조회합니다."""
    try:
        logger.info("지원 감정 목록 조회 요청")
        
        return {
            "success": True,
            "supported_emotions": list(EMOTION_EXPRESSIONS.keys()),
            "emotion_mappings": EMOTION_EXPRESSIONS,
            "total_count": len(EMOTION_EXPRESSIONS),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"지원 감정 목록 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"감정 목록 조회 실패: {str(e)}") from e


@router.post("/auto-express")
async def auto_express_situation(situation: str, user_id: str = "default_user"):  # noqa: ARG001
    """상황별 자동 표현을 실행합니다."""
    try:
        situation_mappings = {
            "command_received": {"expression": "listening", "sound": "beep", "animation": "blink"},
            "command_completed": {"expression": "success", "sound": "success", "animation": "sparkle"},
            "command_error": {"expression": "error", "sound": "error", "animation": "pulse"},
            "user_greeting": {"expression": "happy", "sound": "success", "animation": "wave"},
            "user_farewell": {"expression": "neutral", "sound": "beep", "animation": "fade"},
            "system_startup": {"expression": "happy", "sound": "startup", "animation": "rainbow"},
            "system_shutdown": {"expression": "sleepy", "sound": "shutdown", "animation": "fade"},
            "low_battery": {"expression": "sad", "sound": "low_battery", "animation": "pulse"},
            "connection_lost": {"expression": "error", "sound": "connection_lost", "animation": "pulse"}
        }
        
        if situation not in situation_mappings:
            raise HTTPException(
                status_code=400,
                detail=f"지원하지 않는 상황입니다. 지원 상황: {list(situation_mappings.keys())}"
            )
        
        config = situation_mappings[situation]
        
        logger.info(f"상황별 자동 표현: {situation}")
        
        # LED 표현
        if config["expression"]:
            # TODO: Socket Bridge를 통해 ESP32에 LED 명령 전송
            # led_command = {
            #     "type": "led_expression",
            #     "expression": config["expression"],
            #     "brightness": 100,
            #     "duration": 2000,
            #     "animation": config["animation"],
            #     "timestamp": datetime.now().isoformat()
            # }
            # await send_to_esp32(led_command)
            pass
        
        # 버저 소리
        if config["sound"]:
            # TODO: Socket Bridge를 통해 ESP32에 버저 명령 전송
            # buzzer_command = {
            #     "type": "buzzer_sound",
            #     "sound": config["sound"],
            #     "frequency": 1000,
            #     "volume": 80,
            #     "duration": 500,
            #     "timestamp": datetime.now().isoformat()
            # }
            # await send_to_esp32(buzzer_command)
            pass
        
        return {
            "success": True,
            "message": f"상황 '{situation}'에 대한 자동 표현을 실행했습니다",
            "situation": situation,
            "expression": config["expression"],
            "sound": config["sound"],
            "animation": config["animation"],
            "command_id": f"auto_{hash(situation) % 10000}",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"자동 표현 실행 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"자동 표현 실행 실패: {str(e)}") from e


@router.get("/health")
async def expression_health_check():
    """표현 제어 모듈 헬스 체크"""
    try:
        total_expressions = sum(len(category) for category in SUPPORTED_EXPRESSIONS.values())
        total_sounds = sum(len(category) for category in SUPPORTED_SOUNDS.values())
        
        return {
        "status": "healthy",
        "module": "expression",
            "supported_expressions": total_expressions,
            "supported_sounds": total_sounds,
            "supported_emotions": len(EMOTION_EXPRESSIONS),
            "features": [
                "led_expressions", "buzzer_sounds", "emotion_mapping",
                "custom_patterns", "auto_situations", "animations"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:  # noqa: BLE001
        logger.error(f"헬스 체크 중 오류: {e}")
        return {
            "status": "unhealthy",
            "module": "expression",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
    }
