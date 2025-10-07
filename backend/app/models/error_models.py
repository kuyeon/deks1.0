"""
Deks 1.0 에러 응답 모델
표준화된 에러 응답 형식을 정의
"""

from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ErrorDetail(BaseModel):
    """에러 상세 정보"""
    field: Optional[str] = Field(None, description="에러가 발생한 필드명")
    message: str = Field(..., description="에러 메시지")
    code: Optional[str] = Field(None, description="필드별 에러 코드")


class ErrorResponse(BaseModel):
    """표준 에러 응답 모델"""
    success: bool = Field(False, description="요청 성공 여부 (항상 false)")
    error_code: int = Field(..., description="Deks 에러 코드")
    error_name: str = Field(..., description="에러 코드 이름")
    message: str = Field(..., description="사용자 친화적 에러 메시지")
    details: Dict[str, Any] = Field(default_factory=dict, description="추가 에러 세부 정보")
    timestamp: str = Field(..., description="에러 발생 시각 (ISO 8601)")
    path: Optional[str] = Field(None, description="에러가 발생한 API 경로")
    request_id: Optional[str] = Field(None, description="요청 추적 ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": 6002,
                "error_name": "ROBOT_COMMAND_FAILED",
                "message": "로봇 명령 실행에 실패했습니다: move_forward",
                "details": {
                    "command": "move_forward",
                    "reason": "로봇이 응답하지 않습니다"
                },
                "timestamp": "2024-01-01T12:00:00.000Z",
                "path": "/api/v1/robot/move/forward",
                "request_id": "req_abc123"
            }
        }


class ValidationErrorResponse(BaseModel):
    """검증 에러 응답 모델 (Pydantic 검증 실패 시)"""
    success: bool = Field(False, description="요청 성공 여부 (항상 false)")
    error_code: int = Field(2001, description="검증 에러 코드")
    error_name: str = Field("VALIDATION_ERROR", description="에러 코드 이름")
    message: str = Field("입력값 검증에 실패했습니다", description="에러 메시지")
    errors: List[ErrorDetail] = Field(..., description="필드별 검증 에러 목록")
    timestamp: str = Field(..., description="에러 발생 시각")
    path: Optional[str] = Field(None, description="API 경로")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": 2001,
                "error_name": "VALIDATION_ERROR",
                "message": "입력값 검증에 실패했습니다",
                "errors": [
                    {
                        "field": "speed",
                        "message": "속도는 0에서 100 사이여야 합니다",
                        "code": "value_error.number.not_gt"
                    },
                    {
                        "field": "distance",
                        "message": "필수 필드입니다",
                        "code": "value_error.missing"
                    }
                ],
                "timestamp": "2024-01-01T12:00:00.000Z",
                "path": "/api/v1/robot/move/forward"
            }
        }


class ErrorStatistics(BaseModel):
    """에러 통계 모델 (모니터링용)"""
    total_errors: int = Field(..., description="총 에러 수")
    errors_by_code: Dict[str, int] = Field(..., description="에러 코드별 발생 횟수")
    errors_by_endpoint: Dict[str, int] = Field(..., description="엔드포인트별 에러 횟수")
    last_error_time: Optional[str] = Field(None, description="마지막 에러 발생 시각")
    error_rate: float = Field(..., description="에러 발생률 (%)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_errors": 42,
                "errors_by_code": {
                    "ROBOT_COMMAND_FAILED": 15,
                    "VALIDATION_ERROR": 12,
                    "SOCKET_DISCONNECTED": 8,
                    "SENSOR_READ_ERROR": 7
                },
                "errors_by_endpoint": {
                    "/api/v1/robot/move/forward": 15,
                    "/api/v1/sensors/latest": 7,
                    "/api/v1/chat/message": 12
                },
                "last_error_time": "2024-01-01T12:00:00.000Z",
                "error_rate": 2.1
            }
        }


class HealthCheckError(BaseModel):
    """헬스 체크 에러 정보"""
    component: str = Field(..., description="컴포넌트 이름")
    status: str = Field(..., description="상태 (healthy, degraded, unhealthy)")
    message: Optional[str] = Field(None, description="상태 메시지")
    last_check: str = Field(..., description="마지막 체크 시각")
    error_count: int = Field(0, description="최근 에러 횟수")


class SystemHealthResponse(BaseModel):
    """시스템 헬스 체크 응답"""
    status: str = Field(..., description="전체 시스템 상태")
    timestamp: str = Field(..., description="체크 시각")
    components: List[HealthCheckError] = Field(..., description="컴포넌트별 상태")
    uptime: float = Field(..., description="가동 시간 (초)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00.000Z",
                "components": [
                    {
                        "component": "database",
                        "status": "healthy",
                        "message": "연결 정상",
                        "last_check": "2024-01-01T12:00:00.000Z",
                        "error_count": 0
                    },
                    {
                        "component": "socket_bridge",
                        "status": "degraded",
                        "message": "일부 연결 불안정",
                        "last_check": "2024-01-01T12:00:00.000Z",
                        "error_count": 3
                    },
                    {
                        "component": "robot_controller",
                        "status": "healthy",
                        "message": "정상 작동",
                        "last_check": "2024-01-01T12:00:00.000Z",
                        "error_count": 0
                    }
                ],
                "uptime": 3600.5
            }
        }


def create_error_response(
    error_code: int,
    error_name: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    path: Optional[str] = None,
    request_id: Optional[str] = None
) -> ErrorResponse:
    """
    에러 응답 생성 헬퍼 함수
    
    Args:
        error_code: 에러 코드
        error_name: 에러 이름
        message: 에러 메시지
        details: 추가 세부 정보
        path: API 경로
        request_id: 요청 ID
    
    Returns:
        표준화된 에러 응답
    """
    return ErrorResponse(
        success=False,
        error_code=error_code,
        error_name=error_name,
        message=message,
        details=details or {},
        timestamp=datetime.now().isoformat(),
        path=path,
        request_id=request_id
    )


def create_validation_error_response(
    errors: List[Dict[str, Any]],
    path: Optional[str] = None
) -> ValidationErrorResponse:
    """
    검증 에러 응답 생성 헬퍼 함수
    
    Args:
        errors: 검증 에러 리스트 (Pydantic 형식)
        path: API 경로
    
    Returns:
        검증 에러 응답
    """
    error_details = []
    for error in errors:
        field = ".".join(str(loc) for loc in error.get("loc", []))
        error_details.append(
            ErrorDetail(
                field=field,
                message=error.get("msg", "알 수 없는 에러"),
                code=error.get("type", "unknown")
            )
        )
    
    return ValidationErrorResponse(
        success=False,
        error_code=2001,
        error_name="VALIDATION_ERROR",
        message="입력값 검증에 실패했습니다",
        errors=error_details,
        timestamp=datetime.now().isoformat(),
        path=path
    )

