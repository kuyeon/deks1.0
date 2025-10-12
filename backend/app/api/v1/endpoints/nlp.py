"""
자연어 처리 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from loguru import logger
import time

from app.database.database_manager import db_manager
from app.services.socket_bridge import get_socket_bridge
from datetime import datetime

router = APIRouter()


# 요청/응답 모델
class ParseCommandRequest(BaseModel):
    """명령 파싱 요청 모델"""
    message: str
    user_id: str = "default_user"
    session_id: Optional[str] = None


class CommandPattern(BaseModel):
    """명령 패턴 모델"""
    action: str
    patterns: List[str]
    description: str


class ParseCommandResponse(BaseModel):
    """명령 파싱 응답 모델"""
    success: bool
    command_id: Optional[str] = None
    action: Optional[str] = None
    confidence: Optional[float] = None
    response: Optional[str] = None
    parameters: Optional[dict] = None
    timestamp: str
    error: Optional[str] = None
    suggestions: Optional[List[str]] = None


class SupportedCommandsResponse(BaseModel):
    """지원 명령어 목록 응답 모델"""
    success: bool
    supported_commands: List[CommandPattern]
    timestamp: str


# 명령어 패턴 정의
COMMAND_PATTERNS = {
    "move_forward": {
        "patterns": ["앞으로", "전진", "가줘", "이동해", "앞으로 가", "앞으로 가줘", "전진해", "가자", "직진"],
        "description": "로봇을 앞으로 이동시킵니다"
    },
    "move_backward": {
        "patterns": ["뒤로", "후진", "뒤로 가", "뒤로 가줘", "후진해"],
        "description": "로봇을 뒤로 이동시킵니다"
    },
    "turn_left": {
        "patterns": ["왼쪽", "좌회전", "왼쪽으로", "왼쪽으로 돌아", "왼쪽으로 돌아줘", "좌회전해"],
        "description": "로봇을 왼쪽으로 회전시킵니다"
    },
    "turn_right": {
        "patterns": ["오른쪽", "우회전", "오른쪽으로", "오른쪽으로 돌아", "오른쪽으로 돌아줘", "우회전해"],
        "description": "로봇을 오른쪽으로 회전시킵니다"
    },
    "stop": {
        "patterns": ["정지", "멈춰", "그만", "정지해", "멈춰줘", "정지해줘", "스톱"],
        "description": "로봇을 정지시킵니다"
    },
    "spin": {
        "patterns": ["빙글빙글", "돌아", "회전해", "빙글빙글 돌아", "빙글빙글 돌아줘", "제자리 회전"],
        "description": "로봇을 제자리에서 회전시킵니다"
    }
}

# 속도 수식어 패턴 정의
SPEED_MODIFIERS = {
    "very_fast": {
        "patterns": ["아주 빨리", "매우 빨리", "엄청 빨리", "굉장히 빨리", "최대한 빨리"],
        "speed": 100,
        "description": "매우 빠른 속도"
    },
    "fast": {
        "patterns": ["빨리", "빠르게", "빠른", "급하게", "서둘러"],
        "speed": 90,
        "description": "빠른 속도"
    },
    "normal": {
        "patterns": ["보통", "적당히", "일반", "평범하게"],
        "speed": 50,
        "description": "보통 속도"
    },
    "slow": {
        "patterns": ["천천히", "느리게", "느린", "조심스럽게", "살살"],
        "speed": 25,
        "description": "느린 속도"
    },
    "very_slow": {
        "patterns": ["아주 천천히", "매우 천천히", "엄청 천천히", "굉장히 천천히"],
        "speed": 12,
        "description": "매우 느린 속도"
    }
}

# 거리 수식어 패턴 정의
DISTANCE_MODIFIERS = {
    "very_long": {
        "patterns": ["아주 멀리", "매우 멀리", "엄청 멀리", "오래"],
        "distance": 200,
        "description": "매우 긴 거리"
    },
    "long": {
        "patterns": ["멀리", "길게"],
        "distance": 150,
        "description": "긴 거리"
    },
    "normal": {
        "patterns": ["조금", "적당히", "보통"],
        "distance": 100,
        "description": "보통 거리"
    },
    "short": {
        "patterns": ["짧게", "살짝", "약간"],
        "distance": 50,
        "description": "짧은 거리"
    },
    "very_short": {
        "patterns": ["아주 짧게", "매우 짧게"],
        "distance": 30,
        "description": "매우 짧은 거리"
    }
}


def parse_natural_language_command(message: str) -> dict:
    """
    자연어 명령을 파싱하여 로봇 제어 명령으로 변환합니다.
    속도와 거리 수식어를 인식합니다.
    
    Args:
        message: 사용자 입력 메시지
        
    Returns:
        파싱된 명령 정보
    """
    message_lower = message.lower().strip()
    
    # 속도 수식어 감지
    detected_speed = 50  # 기본 속도
    speed_modifier_name = "normal"
    for modifier_name, modifier_info in SPEED_MODIFIERS.items():
        for pattern in modifier_info["patterns"]:
            if pattern in message_lower:
                detected_speed = modifier_info["speed"]
                speed_modifier_name = modifier_name
                break
        if speed_modifier_name != "normal" and detected_speed != 50:
            break
    
    # 거리 수식어 감지
    detected_distance = 100  # 기본 거리
    distance_modifier_name = "normal"
    for modifier_name, modifier_info in DISTANCE_MODIFIERS.items():
        for pattern in modifier_info["patterns"]:
            if pattern in message_lower:
                detected_distance = modifier_info["distance"]
                distance_modifier_name = modifier_name
                break
        if distance_modifier_name != "normal" and detected_distance != 100:
            break
    
    # 각 명령 패턴과 매칭 확인
    for action, pattern_info in COMMAND_PATTERNS.items():
        for pattern in pattern_info["patterns"]:
            if pattern in message_lower:
                # 기본 매개변수 설정 (속도 및 거리 수식어 적용)
                parameters = {}
                
                if action == "move_forward":
                    parameters = {
                        "speed": detected_speed,
                        "distance": detected_distance
                    }
                elif action == "move_backward":
                    parameters = {
                        "speed": detected_speed,
                        "distance": detected_distance
                    }
                elif action in ["turn_left", "turn_right"]:
                    parameters = {
                        "angle": 90,
                        "speed": detected_speed
                    }
                elif action == "spin":
                    parameters = {
                        "speed": detected_speed,
                        "rotations": 1
                    }
                
                # 응답 메시지 생성 (속도 수식어 반영)
                speed_description = ""
                if speed_modifier_name == "very_fast":
                    speed_description = "아주 빠르게 "
                elif speed_modifier_name == "fast":
                    speed_description = "빠르게 "
                elif speed_modifier_name == "slow":
                    speed_description = "천천히 "
                elif speed_modifier_name == "very_slow":
                    speed_description = "아주 천천히 "
                
                response_messages = {
                    "move_forward": f"{speed_description}앞으로 이동합니다!",
                    "move_backward": f"{speed_description}뒤로 이동합니다!",
                    "turn_left": f"{speed_description}왼쪽으로 회전합니다!",
                    "turn_right": f"{speed_description}오른쪽으로 회전합니다!",
                    "stop": "정지합니다!",
                    "spin": f"{speed_description}빙글빙글 돌아갑니다!"
                }
                
                return {
                    "action": action,
                    "confidence": 0.95,
                    "response": response_messages[action],
                    "parameters": parameters,
                    "modifiers": {
                        "speed": speed_modifier_name,
                        "distance": distance_modifier_name,
                        "speed_value": detected_speed,
                        "distance_value": detected_distance
                    }
                }
    
    return {
        "action": None,
        "confidence": 0.0,
        "response": None,
        "parameters": None,
        "modifiers": None
    }


@router.post("/parse-command", response_model=ParseCommandResponse)
async def parse_command(request: ParseCommandRequest):
    """자연어 명령을 파싱합니다."""
    try:
        logger.info(f"명령 파싱 요청: '{request.message}' (사용자: {request.user_id})")
        
        # 자연어 명령 파싱
        parsed_result = parse_natural_language_command(request.message)
        
        if parsed_result["action"]:
            command_id = f"cmd_{int(datetime.now().timestamp())}"
            
            # Socket Bridge를 통해 실제 로봇 명령 실행
            try:
                socket_bridge = await get_socket_bridge()
                robot_controller = socket_bridge.robot_controller
                
                # 파싱된 명령을 로봇 제어기로 전달
                action = parsed_result["action"]
                parameters = parsed_result["parameters"] or {}
                
                command_success = False
                
                if action == "move_forward":
                    command_success = await robot_controller.move_forward(
                        parameters.get("speed", 50),
                        parameters.get("distance", 100)
                    )
                elif action == "move_backward":
                    command_success = await robot_controller.move_backward(
                        parameters.get("speed", 50),
                        parameters.get("distance", 100)
                    )
                elif action == "turn_left":
                    command_success = await robot_controller.turn_left(
                        parameters.get("angle", 90),
                        parameters.get("speed", 50)
                    )
                elif action == "turn_right":
                    command_success = await robot_controller.turn_right(
                        parameters.get("angle", 90),
                        parameters.get("speed", 50)
                    )
                elif action == "stop":
                    command_success = await robot_controller.stop()
                elif action == "spin":
                    command_success = await robot_controller.spin(
                        parameters.get("rotations", 1),
                        parameters.get("speed", 50)
                    )
                
                if not command_success:
                    logger.warning(f"로봇 명령 실행 실패: {action}")
                
            except Exception as e:
                logger.error(f"Socket Bridge 명령 실행 중 오류: {e}")
            
            # 데이터베이스에 상호작용 기록 저장
            interaction_data = {
                'command': request.message,
                'response': parsed_result["response"],
                'success': True,
                'user_id': request.user_id,
                'session_id': request.session_id,
                'command_id': command_id,
                'confidence': parsed_result["confidence"],
                'execution_time': 0.0  # NLP 처리 시간은 즉시이므로 0
            }
            
            db_manager.save_user_interaction(interaction_data)
            db_manager.update_command_frequency(request.message, success=True)
            
            return ParseCommandResponse(
                success=True,
                command_id=command_id,
                action=parsed_result["action"],
                confidence=parsed_result["confidence"],
                response=parsed_result["response"],
                parameters=parsed_result["parameters"],
                timestamp=datetime.now().isoformat()
            )
        else:
            # 인식되지 않은 명령에 대한 제안 생성
            suggestions = []
            for action, pattern_info in COMMAND_PATTERNS.items():
                suggestions.extend(pattern_info["patterns"][:2])  # 각 액션당 2개씩 제안
            
            # 실패한 명령을 에러 패턴으로 저장
            error_data = {
                'failed_command': request.message,
                'error_type': 'unknown_command',
                'user_id': request.user_id,
                'error_message': '명령을 이해할 수 없습니다',
                'context': {'session_id': request.session_id}
            }
            db_manager.save_error_pattern(error_data)
            db_manager.update_command_frequency(request.message, success=False)
            
            return ParseCommandResponse(
                success=False,
                error="NLP_PARSE_ERROR",
                suggestions=suggestions[:3],  # 최대 3개 제안
                timestamp="2024-01-01T12:00:00Z"
            )
            
    except Exception as e:
        logger.error(f"명령 파싱 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"명령 파싱 실패: {str(e)}")


@router.get("/commands", response_model=SupportedCommandsResponse)
async def get_supported_commands():
    """지원하는 명령어 목록을 조회합니다."""
    try:
        logger.info("지원 명령어 목록 조회 요청")
        
        supported_commands = []
        for action, pattern_info in COMMAND_PATTERNS.items():
            supported_commands.append(CommandPattern(
                action=action,
                patterns=pattern_info["patterns"],
                description=pattern_info["description"]
            ))
        
        return SupportedCommandsResponse(
            success=True,
            supported_commands=supported_commands,
            timestamp="2024-01-01T12:00:00Z"
        )
        
    except Exception as e:
        logger.error(f"지원 명령어 목록 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"명령어 목록 조회 실패: {str(e)}")


@router.get("/health")
async def nlp_health_check():
    """NLP 모듈 헬스 체크"""
    return {
        "status": "healthy",
        "module": "nlp",
        "supported_actions": list(COMMAND_PATTERNS.keys()),
        "total_patterns": sum(len(info["patterns"]) for info in COMMAND_PATTERNS.values())
    }
