"""
Deks 1.0 커스텀 예외 클래스
체계적이고 표준화된 에러 처리를 위한 예외 계층 구조
"""

from typing import Any, Dict, Optional
from enum import Enum


class ErrorCode(Enum):
    """에러 코드 열거형"""
    # 일반 에러 (1000번대)
    UNKNOWN_ERROR = 1000
    INTERNAL_SERVER_ERROR = 1001
    SERVICE_UNAVAILABLE = 1002
    TIMEOUT_ERROR = 1003
    CONFIGURATION_ERROR = 1004
    
    # 요청 관련 에러 (2000번대)
    INVALID_REQUEST = 2000
    VALIDATION_ERROR = 2001
    MISSING_PARAMETER = 2002
    INVALID_PARAMETER = 2003
    INVALID_FORMAT = 2004
    
    # 인증/권한 에러 (3000번대)
    UNAUTHORIZED = 3000
    FORBIDDEN = 3001
    INVALID_TOKEN = 3002
    TOKEN_EXPIRED = 3003
    
    # 리소스 에러 (4000번대)
    RESOURCE_NOT_FOUND = 4000
    RESOURCE_ALREADY_EXISTS = 4001
    RESOURCE_CONFLICT = 4002
    RESOURCE_LOCKED = 4003
    
    # 데이터베이스 에러 (5000번대)
    DATABASE_ERROR = 5000
    DATABASE_CONNECTION_ERROR = 5001
    DATABASE_QUERY_ERROR = 5002
    DATABASE_TRANSACTION_ERROR = 5003
    DATABASE_INTEGRITY_ERROR = 5004
    
    # 로봇 제어 에러 (6000번대)
    ROBOT_ERROR = 6000
    ROBOT_NOT_CONNECTED = 6001
    ROBOT_COMMAND_FAILED = 6002
    ROBOT_COMMAND_TIMEOUT = 6003
    ROBOT_INVALID_STATE = 6004
    ROBOT_SAFETY_VIOLATION = 6005
    ROBOT_HARDWARE_ERROR = 6006
    ROBOT_COMMUNICATION_ERROR = 6007
    
    # 센서 관련 에러 (7000번대)
    SENSOR_ERROR = 7000
    SENSOR_NOT_FOUND = 7001
    SENSOR_READ_ERROR = 7002
    SENSOR_CALIBRATION_ERROR = 7003
    SENSOR_OUT_OF_RANGE = 7004
    
    # 통신 관련 에러 (8000번대)
    COMMUNICATION_ERROR = 8000
    SOCKET_ERROR = 8001
    SOCKET_CONNECTION_ERROR = 8002
    SOCKET_DISCONNECTED = 8003
    SOCKET_TIMEOUT = 8004
    WEBSOCKET_ERROR = 8005
    MESSAGE_PARSE_ERROR = 8006
    MESSAGE_SEND_ERROR = 8007
    
    # NLP/채팅 에러 (9000번대)
    NLP_ERROR = 9000
    NLP_PARSE_ERROR = 9001
    CHAT_CONTEXT_ERROR = 9002
    INVALID_COMMAND = 9003


class DeksBaseException(Exception):
    """
    Deks 기본 예외 클래스
    모든 커스텀 예외의 부모 클래스
    """
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Args:
            message: 에러 메시지
            error_code: 에러 코드
            details: 추가 세부 정보
            original_exception: 원본 예외 (래핑하는 경우)
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.original_exception = original_exception
    
    def to_dict(self) -> Dict[str, Any]:
        """예외를 딕셔너리로 변환"""
        result = {
            "error_code": self.error_code.value,
            "error_name": self.error_code.name,
            "message": self.message,
            "details": self.details
        }
        
        if self.original_exception:
            result["original_error"] = {
                "type": type(self.original_exception).__name__,
                "message": str(self.original_exception)
            }
        
        return result


# ============================================================================
# 일반 에러
# ============================================================================

class InternalServerException(DeksBaseException):
    """내부 서버 에러"""
    def __init__(self, message: str = "내부 서버 에러가 발생했습니다", **kwargs):
        super().__init__(message, ErrorCode.INTERNAL_SERVER_ERROR, **kwargs)


class ServiceUnavailableException(DeksBaseException):
    """서비스 사용 불가"""
    def __init__(self, message: str = "서비스를 일시적으로 사용할 수 없습니다", **kwargs):
        super().__init__(message, ErrorCode.SERVICE_UNAVAILABLE, **kwargs)


class TimeoutException(DeksBaseException):
    """타임아웃 에러"""
    def __init__(self, message: str = "요청 시간이 초과되었습니다", **kwargs):
        super().__init__(message, ErrorCode.TIMEOUT_ERROR, **kwargs)


class ConfigurationException(DeksBaseException):
    """설정 에러"""
    def __init__(self, message: str = "설정 오류가 발생했습니다", **kwargs):
        super().__init__(message, ErrorCode.CONFIGURATION_ERROR, **kwargs)


# ============================================================================
# 요청 관련 에러
# ============================================================================

class InvalidRequestException(DeksBaseException):
    """유효하지 않은 요청"""
    def __init__(self, message: str = "유효하지 않은 요청입니다", **kwargs):
        super().__init__(message, ErrorCode.INVALID_REQUEST, **kwargs)


class ValidationException(DeksBaseException):
    """검증 에러"""
    def __init__(self, message: str = "입력값 검증에 실패했습니다", **kwargs):
        super().__init__(message, ErrorCode.VALIDATION_ERROR, **kwargs)


class MissingParameterException(DeksBaseException):
    """필수 파라미터 누락"""
    def __init__(self, parameter_name: str, **kwargs):
        message = f"필수 파라미터가 누락되었습니다: {parameter_name}"
        details = {"parameter_name": parameter_name}
        super().__init__(message, ErrorCode.MISSING_PARAMETER, details=details, **kwargs)


class InvalidParameterException(DeksBaseException):
    """유효하지 않은 파라미터"""
    def __init__(self, parameter_name: str, reason: str = "", **kwargs):
        message = f"유효하지 않은 파라미터입니다: {parameter_name}"
        if reason:
            message += f" ({reason})"
        details = {"parameter_name": parameter_name, "reason": reason}
        super().__init__(message, ErrorCode.INVALID_PARAMETER, details=details, **kwargs)


# ============================================================================
# 리소스 에러
# ============================================================================

class ResourceNotFoundException(DeksBaseException):
    """리소스를 찾을 수 없음"""
    def __init__(self, resource_type: str, resource_id: str = "", **kwargs):
        message = f"{resource_type}을(를) 찾을 수 없습니다"
        if resource_id:
            message += f": {resource_id}"
        details = {"resource_type": resource_type, "resource_id": resource_id}
        super().__init__(message, ErrorCode.RESOURCE_NOT_FOUND, details=details, **kwargs)


class ResourceAlreadyExistsException(DeksBaseException):
    """리소스가 이미 존재함"""
    def __init__(self, resource_type: str, resource_id: str = "", **kwargs):
        message = f"{resource_type}이(가) 이미 존재합니다"
        if resource_id:
            message += f": {resource_id}"
        details = {"resource_type": resource_type, "resource_id": resource_id}
        super().__init__(message, ErrorCode.RESOURCE_ALREADY_EXISTS, details=details, **kwargs)


# ============================================================================
# 데이터베이스 에러
# ============================================================================

class DatabaseException(DeksBaseException):
    """데이터베이스 에러"""
    def __init__(self, message: str = "데이터베이스 에러가 발생했습니다", **kwargs):
        super().__init__(message, ErrorCode.DATABASE_ERROR, **kwargs)


class DatabaseConnectionException(DatabaseException):
    """데이터베이스 연결 에러"""
    def __init__(self, message: str = "데이터베이스 연결에 실패했습니다", **kwargs):
        super().__init__(message, error_code=ErrorCode.DATABASE_CONNECTION_ERROR, **kwargs)


class DatabaseQueryException(DatabaseException):
    """데이터베이스 쿼리 에러"""
    def __init__(self, message: str = "데이터베이스 쿼리 실행에 실패했습니다", query: str = "", **kwargs):
        details = {"query": query} if query else {}
        super().__init__(message, error_code=ErrorCode.DATABASE_QUERY_ERROR, details=details, **kwargs)


class DatabaseIntegrityException(DatabaseException):
    """데이터베이스 무결성 에러"""
    def __init__(self, message: str = "데이터베이스 무결성 제약 조건 위반", **kwargs):
        super().__init__(message, error_code=ErrorCode.DATABASE_INTEGRITY_ERROR, **kwargs)


# ============================================================================
# 로봇 제어 에러
# ============================================================================

class RobotException(DeksBaseException):
    """로봇 에러 기본 클래스"""
    def __init__(self, message: str = "로봇 에러가 발생했습니다", error_code=ErrorCode.ROBOT_ERROR, **kwargs):
        super().__init__(message, error_code, **kwargs)


class RobotNotConnectedException(RobotException):
    """로봇이 연결되지 않음"""
    def __init__(self, robot_id: str = "", **kwargs):
        message = "로봇이 연결되지 않았습니다"
        if robot_id:
            message += f": {robot_id}"
        details = {"robot_id": robot_id}
        super().__init__(message, error_code=ErrorCode.ROBOT_NOT_CONNECTED, details=details, **kwargs)


class RobotCommandFailedException(RobotException):
    """로봇 명령 실행 실패"""
    def __init__(self, command: str, reason: str = "", **kwargs):
        message = f"로봇 명령 실행에 실패했습니다: {command}"
        if reason:
            message += f" ({reason})"
        details = {"command": command, "reason": reason}
        super().__init__(message, error_code=ErrorCode.ROBOT_COMMAND_FAILED, details=details, **kwargs)


class RobotCommandTimeoutException(RobotException):
    """로봇 명령 타임아웃"""
    def __init__(self, command: str, timeout: float, **kwargs):
        message = f"로봇 명령 타임아웃: {command} (제한시간: {timeout}초)"
        details = {"command": command, "timeout": timeout}
        super().__init__(message, error_code=ErrorCode.ROBOT_COMMAND_TIMEOUT, details=details, **kwargs)


class RobotInvalidStateException(RobotException):
    """로봇의 상태가 유효하지 않음"""
    def __init__(self, current_state: str, required_state: str = "", **kwargs):
        message = f"로봇의 현재 상태가 유효하지 않습니다: {current_state}"
        if required_state:
            message += f" (필요한 상태: {required_state})"
        details = {"current_state": current_state, "required_state": required_state}
        super().__init__(message, error_code=ErrorCode.ROBOT_INVALID_STATE, details=details, **kwargs)


class RobotSafetyViolationException(RobotException):
    """로봇 안전 규칙 위반"""
    def __init__(self, violation_type: str, **kwargs):
        message = f"로봇 안전 규칙 위반: {violation_type}"
        details = {"violation_type": violation_type}
        super().__init__(message, error_code=ErrorCode.ROBOT_SAFETY_VIOLATION, details=details, **kwargs)


class RobotHardwareException(RobotException):
    """로봇 하드웨어 에러"""
    def __init__(self, hardware_component: str, **kwargs):
        message = f"로봇 하드웨어 에러: {hardware_component}"
        details = {"hardware_component": hardware_component}
        super().__init__(message, error_code=ErrorCode.ROBOT_HARDWARE_ERROR, details=details, **kwargs)


class RobotCommunicationException(RobotException):
    """로봇 통신 에러"""
    def __init__(self, message: str = "로봇과의 통신에 실패했습니다", **kwargs):
        super().__init__(message, error_code=ErrorCode.ROBOT_COMMUNICATION_ERROR, **kwargs)


# ============================================================================
# 센서 관련 에러
# ============================================================================

class SensorException(DeksBaseException):
    """센서 에러 기본 클래스"""
    def __init__(self, message: str = "센서 에러가 발생했습니다", error_code=ErrorCode.SENSOR_ERROR, **kwargs):
        super().__init__(message, error_code, **kwargs)


class SensorNotFoundException(SensorException):
    """센서를 찾을 수 없음"""
    def __init__(self, sensor_name: str, **kwargs):
        message = f"센서를 찾을 수 없습니다: {sensor_name}"
        details = {"sensor_name": sensor_name}
        super().__init__(message, error_code=ErrorCode.SENSOR_NOT_FOUND, details=details, **kwargs)


class SensorReadException(SensorException):
    """센서 읽기 에러"""
    def __init__(self, sensor_name: str, reason: str = "", **kwargs):
        message = f"센서 데이터 읽기에 실패했습니다: {sensor_name}"
        if reason:
            message += f" ({reason})"
        details = {"sensor_name": sensor_name, "reason": reason}
        super().__init__(message, error_code=ErrorCode.SENSOR_READ_ERROR, details=details, **kwargs)


class SensorOutOfRangeException(SensorException):
    """센서 값이 범위를 벗어남"""
    def __init__(self, sensor_name: str, value: float, min_value: float, max_value: float, **kwargs):
        message = f"센서 값이 유효 범위를 벗어났습니다: {sensor_name} = {value} (범위: {min_value}~{max_value})"
        details = {
            "sensor_name": sensor_name,
            "value": value,
            "min_value": min_value,
            "max_value": max_value
        }
        super().__init__(message, error_code=ErrorCode.SENSOR_OUT_OF_RANGE, details=details, **kwargs)


# ============================================================================
# 통신 관련 에러
# ============================================================================

class CommunicationException(DeksBaseException):
    """통신 에러 기본 클래스"""
    def __init__(self, message: str = "통신 에러가 발생했습니다", error_code=ErrorCode.COMMUNICATION_ERROR, **kwargs):
        super().__init__(message, error_code, **kwargs)


class SocketException(CommunicationException):
    """소켓 에러"""
    def __init__(self, message: str = "소켓 에러가 발생했습니다", error_code=ErrorCode.SOCKET_ERROR, **kwargs):
        super().__init__(message, error_code=error_code, **kwargs)


class SocketConnectionException(SocketException):
    """소켓 연결 에러"""
    def __init__(self, host: str, port: int, reason: str = "", **kwargs):
        message = f"소켓 연결에 실패했습니다: {host}:{port}"
        if reason:
            message += f" ({reason})"
        details = {"host": host, "port": port, "reason": reason}
        super().__init__(message, error_code=ErrorCode.SOCKET_CONNECTION_ERROR, details=details, **kwargs)


class SocketDisconnectedException(SocketException):
    """소켓 연결 끊김"""
    def __init__(self, client_id: str = "", **kwargs):
        message = "소켓 연결이 끊어졌습니다"
        if client_id:
            message += f": {client_id}"
        details = {"client_id": client_id}
        super().__init__(message, error_code=ErrorCode.SOCKET_DISCONNECTED, details=details, **kwargs)


class SocketTimeoutException(SocketException):
    """소켓 타임아웃"""
    def __init__(self, operation: str, timeout: float, **kwargs):
        message = f"소켓 타임아웃: {operation} (제한시간: {timeout}초)"
        details = {"operation": operation, "timeout": timeout}
        super().__init__(message, error_code=ErrorCode.SOCKET_TIMEOUT, details=details, **kwargs)


class WebSocketException(CommunicationException):
    """WebSocket 에러"""
    def __init__(self, message: str = "WebSocket 에러가 발생했습니다", **kwargs):
        super().__init__(message, error_code=ErrorCode.WEBSOCKET_ERROR, **kwargs)


class MessageParseException(CommunicationException):
    """메시지 파싱 에러"""
    def __init__(self, message_data: str = "", reason: str = "", **kwargs):
        message = "메시지 파싱에 실패했습니다"
        if reason:
            message += f": {reason}"
        details = {"message_data": message_data[:100], "reason": reason}  # 최대 100자만 저장
        super().__init__(message, error_code=ErrorCode.MESSAGE_PARSE_ERROR, details=details, **kwargs)


class MessageSendException(CommunicationException):
    """메시지 전송 에러"""
    def __init__(self, destination: str = "", reason: str = "", **kwargs):
        message = "메시지 전송에 실패했습니다"
        if destination:
            message += f" (대상: {destination})"
        if reason:
            message += f": {reason}"
        details = {"destination": destination, "reason": reason}
        super().__init__(message, error_code=ErrorCode.MESSAGE_SEND_ERROR, details=details, **kwargs)


# ============================================================================
# NLP/채팅 에러
# ============================================================================

class NLPException(DeksBaseException):
    """NLP 에러 기본 클래스"""
    def __init__(self, message: str = "NLP 처리 중 에러가 발생했습니다", error_code=ErrorCode.NLP_ERROR, **kwargs):
        super().__init__(message, error_code, **kwargs)


class NLPParseException(NLPException):
    """NLP 파싱 에러"""
    def __init__(self, text: str, reason: str = "", **kwargs):
        message = "자연어 파싱에 실패했습니다"
        if reason:
            message += f": {reason}"
        details = {"text": text[:100], "reason": reason}  # 최대 100자만 저장
        super().__init__(message, error_code=ErrorCode.NLP_PARSE_ERROR, details=details, **kwargs)


class ChatContextException(NLPException):
    """채팅 컨텍스트 에러"""
    def __init__(self, message: str = "채팅 컨텍스트 처리 중 에러가 발생했습니다", **kwargs):
        super().__init__(message, error_code=ErrorCode.CHAT_CONTEXT_ERROR, **kwargs)


class InvalidCommandException(NLPException):
    """유효하지 않은 명령"""
    def __init__(self, command: str, reason: str = "", **kwargs):
        message = f"유효하지 않은 명령입니다: {command}"
        if reason:
            message += f" ({reason})"
        details = {"command": command, "reason": reason}
        super().__init__(message, error_code=ErrorCode.INVALID_COMMAND, details=details, **kwargs)


# ============================================================================
# 에러 유틸리티 함수
# ============================================================================

def wrap_exception(
    exception: Exception,
    wrapper_class: type[DeksBaseException] = InternalServerException,
    message: str = ""
) -> DeksBaseException:
    """
    일반 예외를 Deks 커스텀 예외로 래핑
    
    Args:
        exception: 래핑할 원본 예외
        wrapper_class: 사용할 래퍼 클래스
        message: 추가 메시지 (없으면 원본 메시지 사용)
    
    Returns:
        래핑된 Deks 예외
    """
    if isinstance(exception, DeksBaseException):
        return exception
    
    final_message = message or str(exception)
    return wrapper_class(final_message, original_exception=exception)


def get_http_status_code(exception: DeksBaseException) -> int:
    """
    Deks 예외에 해당하는 HTTP 상태 코드 반환
    
    Args:
        exception: Deks 예외
    
    Returns:
        HTTP 상태 코드
    """
    error_code = exception.error_code
    
    # 4xx 클라이언트 에러
    if error_code in [
        ErrorCode.INVALID_REQUEST,
        ErrorCode.VALIDATION_ERROR,
        ErrorCode.MISSING_PARAMETER,
        ErrorCode.INVALID_PARAMETER,
        ErrorCode.INVALID_FORMAT,
        ErrorCode.INVALID_COMMAND,
    ]:
        return 400  # Bad Request
    
    if error_code in [ErrorCode.UNAUTHORIZED, ErrorCode.INVALID_TOKEN, ErrorCode.TOKEN_EXPIRED]:
        return 401  # Unauthorized
    
    if error_code in [ErrorCode.FORBIDDEN]:
        return 403  # Forbidden
    
    if error_code in [
        ErrorCode.RESOURCE_NOT_FOUND,
        ErrorCode.SENSOR_NOT_FOUND,
        ErrorCode.ROBOT_NOT_CONNECTED,
    ]:
        return 404  # Not Found
    
    if error_code in [ErrorCode.RESOURCE_ALREADY_EXISTS, ErrorCode.RESOURCE_CONFLICT]:
        return 409  # Conflict
    
    if error_code in [ErrorCode.RESOURCE_LOCKED]:
        return 423  # Locked
    
    # 5xx 서버 에러
    if error_code in [ErrorCode.SERVICE_UNAVAILABLE]:
        return 503  # Service Unavailable
    
    if error_code in [ErrorCode.TIMEOUT_ERROR, ErrorCode.ROBOT_COMMAND_TIMEOUT, ErrorCode.SOCKET_TIMEOUT]:
        return 504  # Gateway Timeout
    
    # 기본값: 500 Internal Server Error
    return 500

