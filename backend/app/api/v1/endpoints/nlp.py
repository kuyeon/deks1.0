"""
자연어 처리 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from loguru import logger
import time

from app.database.database_manager import db_manager

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
        "patterns": ["앞으로", "전진", "가줘", "이동해", "앞으로 가", "앞으로 가줘", "전진해"],
        "description": "로봇을 앞으로 이동시킵니다"
    },
    "turn_left": {
        "patterns": ["왼쪽", "좌회전", "왼쪽으로", "왼쪽으로 돌아", "왼쪽으로 돌아줘"],
        "description": "로봇을 왼쪽으로 회전시킵니다"
    },
    "turn_right": {
        "patterns": ["오른쪽", "우회전", "오른쪽으로", "오른쪽으로 돌아", "오른쪽으로 돌아줘"],
        "description": "로봇을 오른쪽으로 회전시킵니다"
    },
    "stop": {
        "patterns": ["정지", "멈춰", "그만", "정지해", "멈춰줘", "정지해줘"],
        "description": "로봇을 정지시킵니다"
    },
    "spin": {
        "patterns": ["빙글빙글", "돌아", "회전해", "빙글빙글 돌아", "빙글빙글 돌아줘"],
        "description": "로봇을 제자리에서 회전시킵니다"
    }
}


def parse_natural_language_command(message: str) -> dict:
    """
    자연어 명령을 파싱하여 로봇 제어 명령으로 변환합니다.
    
    Args:
        message: 사용자 입력 메시지
        
    Returns:
        파싱된 명령 정보
    """
    message_lower = message.lower().strip()
    
    # 각 명령 패턴과 매칭 확인
    for action, pattern_info in COMMAND_PATTERNS.items():
        for pattern in pattern_info["patterns"]:
            if pattern in message_lower:
                # 기본 매개변수 설정
                parameters = {}
                
                if action == "move_forward":
                    parameters = {"speed": 50, "distance": 100}
                elif action in ["turn_left", "turn_right"]:
                    parameters = {"angle": 90, "speed": 30}
                elif action == "spin":
                    parameters = {"speed": 40}
                
                # 응답 메시지 생성
                response_messages = {
                    "move_forward": "앞으로 이동합니다!",
                    "turn_left": "왼쪽으로 회전합니다!",
                    "turn_right": "오른쪽으로 회전합니다!",
                    "stop": "정지합니다!",
                    "spin": "빙글빙글 돌아갑니다!"
                }
                
                return {
                    "action": action,
                    "confidence": 0.95,
                    "response": response_messages[action],
                    "parameters": parameters
                }
    
    return {
        "action": None,
        "confidence": 0.0,
        "response": None,
        "parameters": None
    }


@router.post("/parse-command", response_model=ParseCommandResponse)
async def parse_command(request: ParseCommandRequest):
    """자연어 명령을 파싱합니다."""
    try:
        logger.info(f"명령 파싱 요청: '{request.message}' (사용자: {request.user_id})")
        
        # 자연어 명령 파싱
        parsed_result = parse_natural_language_command(request.message)
        
        if parsed_result["action"]:
            command_id = f"cmd_{hash(request.message) % 10000}"
            
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
                timestamp="2024-01-01T12:00:00Z"
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
