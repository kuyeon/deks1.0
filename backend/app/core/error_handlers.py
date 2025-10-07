"""
Deks 1.0 전역 에러 핸들러
FastAPI 애플리케이션의 전역 예외 처리
"""

import traceback
import uuid
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from loguru import logger
from datetime import datetime

from app.core.exceptions import (
    DeksBaseException,
    get_http_status_code,
    InternalServerException,
    ErrorCode
)
from app.models.error_models import (
    create_error_response,
    create_validation_error_response
)


class ErrorTracker:
    """에러 추적 및 통계 관리"""
    
    def __init__(self):
        """에러 추적기 초기화"""
        self.error_count: int = 0
        self.errors_by_code: dict[str, int] = {}
        self.errors_by_endpoint: dict[str, int] = {}
        self.last_errors: list[dict] = []  # 최근 에러 로그 (최대 100개)
        self.max_last_errors = 100
    
    def track_error(
        self,
        error_code: str,
        endpoint: str,
        error_details: dict
    ):
        """
        에러 추적
        
        Args:
            error_code: 에러 코드
            endpoint: 엔드포인트 경로
            error_details: 에러 상세 정보
        """
        self.error_count += 1
        
        # 에러 코드별 카운트
        self.errors_by_code[error_code] = self.errors_by_code.get(error_code, 0) + 1
        
        # 엔드포인트별 카운트
        self.errors_by_endpoint[endpoint] = self.errors_by_endpoint.get(endpoint, 0) + 1
        
        # 최근 에러 로그
        error_log = {
            "timestamp": datetime.now().isoformat(),
            "error_code": error_code,
            "endpoint": endpoint,
            **error_details
        }
        self.last_errors.append(error_log)
        
        # 최대 개수 유지
        if len(self.last_errors) > self.max_last_errors:
            self.last_errors.pop(0)
    
    def get_statistics(self) -> dict:
        """
        에러 통계 조회
        
        Returns:
            에러 통계 딕셔너리
        """
        return {
            "total_errors": self.error_count,
            "errors_by_code": self.errors_by_code.copy(),
            "errors_by_endpoint": self.errors_by_endpoint.copy(),
            "last_errors": self.last_errors[-10:],  # 최근 10개만
            "last_error_time": self.last_errors[-1]["timestamp"] if self.last_errors else None
        }
    
    def reset_statistics(self):
        """통계 초기화"""
        self.error_count = 0
        self.errors_by_code.clear()
        self.errors_by_endpoint.clear()
        self.last_errors.clear()


# 전역 에러 추적기 인스턴스
error_tracker = ErrorTracker()


def generate_request_id() -> str:
    """요청 ID 생성"""
    return f"req_{uuid.uuid4().hex[:12]}"


async def deks_exception_handler(
    request: Request,
    exc: DeksBaseException
) -> JSONResponse:
    """
    Deks 커스텀 예외 핸들러
    
    Args:
        request: FastAPI 요청 객체
        exc: Deks 커스텀 예외
    
    Returns:
        JSON 에러 응답
    """
    # 요청 ID 생성
    request_id = generate_request_id()
    
    # HTTP 상태 코드 결정
    http_status_code = get_http_status_code(exc)
    
    # 에러 응답 생성
    error_response = create_error_response(
        error_code=exc.error_code.value,
        error_name=exc.error_code.name,
        message=exc.message,
        details=exc.details,
        path=str(request.url.path),
        request_id=request_id
    )
    
    # 에러 추적
    error_tracker.track_error(
        error_code=exc.error_code.name,
        endpoint=str(request.url.path),
        error_details={
            "message": exc.message,
            "request_id": request_id,
            "http_status": http_status_code
        }
    )
    
    # 로깅
    log_level = "error" if http_status_code >= 500 else "warning"
    log_message = (
        f"[{request_id}] {exc.error_code.name} - {exc.message} "
        f"(Path: {request.url.path}, Status: {http_status_code})"
    )
    
    if log_level == "error":
        logger.error(log_message)
        if exc.original_exception:
            logger.error(f"원본 예외: {exc.original_exception}")
            logger.error(traceback.format_exc())
    else:
        logger.warning(log_message)
    
    return JSONResponse(
        status_code=http_status_code,
        content=error_response.model_dump()
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Pydantic 검증 에러 핸들러
    
    Args:
        request: FastAPI 요청 객체
        exc: 검증 에러
    
    Returns:
        JSON 에러 응답
    """
    # 요청 ID 생성
    request_id = generate_request_id()
    
    # 검증 에러 응답 생성
    validation_response = create_validation_error_response(
        errors=exc.errors(),
        path=str(request.url.path)
    )
    
    # 에러 추적
    error_tracker.track_error(
        error_code="VALIDATION_ERROR",
        endpoint=str(request.url.path),
        error_details={
            "errors": exc.errors(),
            "request_id": request_id
        }
    )
    
    # 로깅
    logger.warning(
        f"[{request_id}] 검증 에러 - {len(exc.errors())}개의 필드 에러 "
        f"(Path: {request.url.path})"
    )
    logger.debug(f"검증 에러 세부사항: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=validation_response.model_dump()
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
) -> JSONResponse:
    """
    HTTP 예외 핸들러 (Starlette/FastAPI 기본 예외)
    
    Args:
        request: FastAPI 요청 객체
        exc: HTTP 예외
    
    Returns:
        JSON 에러 응답
    """
    # 요청 ID 생성
    request_id = generate_request_id()
    
    # 상태 코드에 따른 에러 코드 매핑
    error_code_map = {
        400: ErrorCode.INVALID_REQUEST,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.RESOURCE_NOT_FOUND,
        500: ErrorCode.INTERNAL_SERVER_ERROR,
        503: ErrorCode.SERVICE_UNAVAILABLE,
    }
    
    error_code = error_code_map.get(exc.status_code, ErrorCode.UNKNOWN_ERROR)
    
    # 에러 응답 생성
    error_response = create_error_response(
        error_code=error_code.value,
        error_name=error_code.name,
        message=str(exc.detail),
        details={},
        path=str(request.url.path),
        request_id=request_id
    )
    
    # 에러 추적
    error_tracker.track_error(
        error_code=error_code.name,
        endpoint=str(request.url.path),
        error_details={
            "message": str(exc.detail),
            "request_id": request_id,
            "http_status": exc.status_code
        }
    )
    
    # 로깅
    log_level = "error" if exc.status_code >= 500 else "warning"
    log_message = (
        f"[{request_id}] HTTP {exc.status_code} - {exc.detail} "
        f"(Path: {request.url.path})"
    )
    
    if log_level == "error":
        logger.error(log_message)
    else:
        logger.warning(log_message)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    일반 예외 핸들러 (모든 예외의 최종 fallback)
    
    Args:
        request: FastAPI 요청 객체
        exc: 예외
    
    Returns:
        JSON 에러 응답
    """
    # 요청 ID 생성
    request_id = generate_request_id()
    
    # 내부 서버 에러로 래핑
    wrapped_exc = InternalServerException(
        message="예상치 못한 에러가 발생했습니다",
        details={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc)
        },
        original_exception=exc
    )
    
    # 에러 응답 생성
    error_response = create_error_response(
        error_code=wrapped_exc.error_code.value,
        error_name=wrapped_exc.error_code.name,
        message=wrapped_exc.message,
        details=wrapped_exc.details,
        path=str(request.url.path),
        request_id=request_id
    )
    
    # 에러 추적
    error_tracker.track_error(
        error_code=wrapped_exc.error_code.name,
        endpoint=str(request.url.path),
        error_details={
            "message": wrapped_exc.message,
            "exception_type": type(exc).__name__,
            "request_id": request_id
        }
    )
    
    # 로깅 (상세한 스택 트레이스 포함)
    logger.error(
        f"[{request_id}] 예상치 못한 에러 - {type(exc).__name__}: {str(exc)} "
        f"(Path: {request.url.path})"
    )
    logger.error(f"스택 트레이스:\n{traceback.format_exc()}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )


def get_error_statistics() -> dict:
    """
    에러 통계 조회
    
    Returns:
        에러 통계 딕셔너리
    """
    return error_tracker.get_statistics()


def reset_error_statistics():
    """에러 통계 초기화"""
    error_tracker.reset_statistics()
    logger.info("에러 통계가 초기화되었습니다")


# 에러 핸들러 등록 헬퍼 함수
def register_error_handlers(app):
    """
    FastAPI 애플리케이션에 에러 핸들러 등록
    
    Args:
        app: FastAPI 애플리케이션 인스턴스
    """
    # Deks 커스텀 예외 핸들러
    app.add_exception_handler(DeksBaseException, deks_exception_handler)
    
    # Pydantic 검증 에러 핸들러
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # HTTP 예외 핸들러
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # 일반 예외 핸들러 (fallback)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("에러 핸들러 등록 완료")

