"""
Deks 1.0 에러 처리 시스템 테스트
"""

import pytest
from app.core.exceptions import (
    DeksBaseException,
    ErrorCode,
    RobotNotConnectedException,
    RobotCommandFailedException,
    RobotInvalidStateException,
    InvalidParameterException,
    DatabaseException,
    SensorNotFoundException,
    SocketConnectionException,
    NLPParseException,
    get_http_status_code,
    wrap_exception
)
from app.models.error_models import (
    create_error_response,
    create_validation_error_response,
    ErrorDetail
)


class TestCustomExceptions:
    """커스텀 예외 클래스 테스트"""
    
    def test_base_exception_creation(self):
        """기본 예외 생성 테스트"""
        exc = DeksBaseException(
            message="테스트 에러",
            error_code=ErrorCode.UNKNOWN_ERROR,
            details={"key": "value"}
        )
        
        assert exc.message == "테스트 에러"
        assert exc.error_code == ErrorCode.UNKNOWN_ERROR
        assert exc.details == {"key": "value"}
    
    def test_base_exception_to_dict(self):
        """예외를 딕셔너리로 변환 테스트"""
        exc = DeksBaseException(
            message="테스트 에러",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            details={"detail": "test"}
        )
        
        result = exc.to_dict()
        
        assert result["error_code"] == ErrorCode.INTERNAL_SERVER_ERROR.value
        assert result["error_name"] == ErrorCode.INTERNAL_SERVER_ERROR.name
        assert result["message"] == "테스트 에러"
        assert result["details"] == {"detail": "test"}
    
    def test_robot_not_connected_exception(self):
        """로봇 미연결 예외 테스트"""
        exc = RobotNotConnectedException(robot_id="deks_001")
        
        assert "로봇이 연결되지 않았습니다" in exc.message
        assert exc.error_code == ErrorCode.ROBOT_NOT_CONNECTED
        assert exc.details["robot_id"] == "deks_001"
    
    def test_robot_command_failed_exception(self):
        """로봇 명령 실패 예외 테스트"""
        exc = RobotCommandFailedException(
            command="move_forward",
            reason="타임아웃"
        )
        
        assert "move_forward" in exc.message
        assert "타임아웃" in exc.message
        assert exc.error_code == ErrorCode.ROBOT_COMMAND_FAILED
        assert exc.details["command"] == "move_forward"
        assert exc.details["reason"] == "타임아웃"
    
    def test_robot_invalid_state_exception(self):
        """로봇 상태 무효 예외 테스트"""
        exc = RobotInvalidStateException(
            current_state="error",
            required_state="idle"
        )
        
        assert "error" in exc.message
        assert "idle" in exc.message
        assert exc.error_code == ErrorCode.ROBOT_INVALID_STATE
    
    def test_invalid_parameter_exception(self):
        """파라미터 무효 예외 테스트"""
        exc = InvalidParameterException(
            parameter_name="speed",
            reason="범위를 벗어남"
        )
        
        assert "speed" in exc.message
        assert "범위를 벗어남" in exc.message
        assert exc.error_code == ErrorCode.INVALID_PARAMETER
        assert exc.details["parameter_name"] == "speed"
    
    def test_database_exception(self):
        """데이터베이스 예외 테스트"""
        exc = DatabaseException(message="DB 연결 실패")
        
        assert exc.message == "DB 연결 실패"
        assert exc.error_code == ErrorCode.DATABASE_ERROR
    
    def test_sensor_not_found_exception(self):
        """센서 미발견 예외 테스트"""
        exc = SensorNotFoundException(sensor_name="temperature")
        
        assert "temperature" in exc.message
        assert exc.error_code == ErrorCode.SENSOR_NOT_FOUND
        assert exc.details["sensor_name"] == "temperature"
    
    def test_socket_connection_exception(self):
        """소켓 연결 예외 테스트"""
        exc = SocketConnectionException(
            host="192.168.1.100",
            port=8888,
            reason="연결 거부"
        )
        
        assert "192.168.1.100" in exc.message
        assert "8888" in exc.message
        assert "연결 거부" in exc.message
        assert exc.error_code == ErrorCode.SOCKET_CONNECTION_ERROR
    
    def test_nlp_parse_exception(self):
        """NLP 파싱 예외 테스트"""
        exc = NLPParseException(
            text="안녕하세요",
            reason="의도 파악 실패"
        )
        
        assert exc.error_code == ErrorCode.NLP_PARSE_ERROR
        assert exc.details["text"] == "안녕하세요"
        assert exc.details["reason"] == "의도 파악 실패"
    
    def test_exception_with_original_exception(self):
        """원본 예외를 포함한 예외 테스트"""
        original = ValueError("원본 에러")
        exc = RobotCommandFailedException(
            command="test",
            reason="실패",
            original_exception=original
        )
        
        result = exc.to_dict()
        assert "original_error" in result
        assert result["original_error"]["type"] == "ValueError"
        assert result["original_error"]["message"] == "원본 에러"


class TestExceptionWrapping:
    """예외 래핑 테스트"""
    
    def test_wrap_exception_general(self):
        """일반 예외 래핑 테스트"""
        original = ValueError("테스트 에러")
        wrapped = wrap_exception(original)
        
        assert isinstance(wrapped, DeksBaseException)
        assert wrapped.original_exception == original
        assert "테스트 에러" in wrapped.message
    
    def test_wrap_exception_with_custom_message(self):
        """커스텀 메시지로 예외 래핑 테스트"""
        original = RuntimeError("내부 에러")
        wrapped = wrap_exception(
            original,
            message="커스텀 메시지"
        )
        
        assert wrapped.message == "커스텀 메시지"
        assert wrapped.original_exception == original
    
    def test_wrap_exception_already_wrapped(self):
        """이미 래핑된 예외는 그대로 반환"""
        original = RobotNotConnectedException()
        wrapped = wrap_exception(original)
        
        assert wrapped is original


class TestHTTPStatusCodeMapping:
    """HTTP 상태 코드 매핑 테스트"""
    
    def test_validation_error_400(self):
        """검증 에러는 400 상태 코드"""
        exc = InvalidParameterException("test", "invalid")
        status_code = get_http_status_code(exc)
        assert status_code == 400
    
    def test_not_found_404(self):
        """미발견 에러는 404 상태 코드"""
        exc = RobotNotConnectedException()
        status_code = get_http_status_code(exc)
        assert status_code == 404
    
    def test_internal_error_500(self):
        """내부 에러는 500 상태 코드"""
        exc = DatabaseException()
        status_code = get_http_status_code(exc)
        assert status_code == 500


class TestErrorResponseModels:
    """에러 응답 모델 테스트"""
    
    def test_create_error_response(self):
        """에러 응답 생성 테스트"""
        response = create_error_response(
            error_code=6002,
            error_name="ROBOT_COMMAND_FAILED",
            message="로봇 명령 실패",
            details={"command": "move_forward"},
            path="/api/v1/robot/move/forward",
            request_id="req_123"
        )
        
        assert response.success is False
        assert response.error_code == 6002
        assert response.error_name == "ROBOT_COMMAND_FAILED"
        assert response.message == "로봇 명령 실패"
        assert response.details["command"] == "move_forward"
        assert response.path == "/api/v1/robot/move/forward"
        assert response.request_id == "req_123"
        assert response.timestamp is not None
    
    def test_create_validation_error_response(self):
        """검증 에러 응답 생성 테스트"""
        errors = [
            {
                "loc": ["body", "speed"],
                "msg": "속도는 0에서 100 사이여야 합니다",
                "type": "value_error.number.range"
            },
            {
                "loc": ["body", "distance"],
                "msg": "필수 필드입니다",
                "type": "value_error.missing"
            }
        ]
        
        response = create_validation_error_response(
            errors=errors,
            path="/api/v1/robot/move/forward"
        )
        
        assert response.success is False
        assert response.error_code == 2001
        assert response.error_name == "VALIDATION_ERROR"
        assert len(response.errors) == 2
        
        # 첫 번째 에러 확인
        first_error = response.errors[0]
        assert first_error.field == "body.speed"
        assert "속도는 0에서 100 사이여야 합니다" in first_error.message
        assert first_error.code == "value_error.number.range"
        
        # 두 번째 에러 확인
        second_error = response.errors[1]
        assert second_error.field == "body.distance"
        assert "필수 필드입니다" in second_error.message


class TestErrorCodeEnum:
    """에러 코드 열거형 테스트"""
    
    def test_error_code_values(self):
        """에러 코드 값 범위 테스트"""
        # 일반 에러 (1000번대)
        assert 1000 <= ErrorCode.UNKNOWN_ERROR.value < 2000
        
        # 요청 관련 에러 (2000번대)
        assert 2000 <= ErrorCode.INVALID_REQUEST.value < 3000
        
        # 리소스 에러 (4000번대)
        assert 4000 <= ErrorCode.RESOURCE_NOT_FOUND.value < 5000
        
        # 데이터베이스 에러 (5000번대)
        assert 5000 <= ErrorCode.DATABASE_ERROR.value < 6000
        
        # 로봇 제어 에러 (6000번대)
        assert 6000 <= ErrorCode.ROBOT_ERROR.value < 7000
        
        # 센서 에러 (7000번대)
        assert 7000 <= ErrorCode.SENSOR_ERROR.value < 8000
        
        # 통신 에러 (8000번대)
        assert 8000 <= ErrorCode.COMMUNICATION_ERROR.value < 9000
        
        # NLP 에러 (9000번대)
        assert 9000 <= ErrorCode.NLP_ERROR.value < 10000
    
    def test_error_code_names(self):
        """에러 코드 이름 테스트"""
        assert ErrorCode.ROBOT_NOT_CONNECTED.name == "ROBOT_NOT_CONNECTED"
        assert ErrorCode.INVALID_PARAMETER.name == "INVALID_PARAMETER"
        assert ErrorCode.DATABASE_ERROR.name == "DATABASE_ERROR"


class TestErrorDetails:
    """에러 상세 정보 테스트"""
    
    def test_error_detail_model(self):
        """에러 상세 모델 테스트"""
        detail = ErrorDetail(
            field="speed",
            message="범위를 벗어났습니다",
            code="value_error.range"
        )
        
        assert detail.field == "speed"
        assert detail.message == "범위를 벗어났습니다"
        assert detail.code == "value_error.range"
    
    def test_error_detail_optional_fields(self):
        """에러 상세 선택 필드 테스트"""
        detail = ErrorDetail(
            field=None,
            message="일반 에러",
            code=None
        )
        
        assert detail.field is None
        assert detail.message == "일반 에러"
        assert detail.code is None


@pytest.mark.asyncio
class TestErrorHandlerIntegration:
    """에러 핸들러 통합 테스트"""
    
    async def test_deks_exception_handler(self):
        """Deks 예외 핸들러 테스트"""
        # 이 테스트는 FastAPI TestClient를 사용한 통합 테스트에서 수행
        # 여기서는 예외 생성만 테스트
        exc = RobotCommandFailedException(
            command="test",
            reason="테스트"
        )
        
        assert exc.error_code == ErrorCode.ROBOT_COMMAND_FAILED
        assert "test" in exc.message
    
    async def test_validation_exception_handler(self):
        """검증 예외 핸들러 테스트"""
        # Pydantic 모델 검증은 통합 테스트에서 수행
        exc = InvalidParameterException(
            parameter_name="speed",
            reason="유효하지 않은 값"
        )
        
        assert exc.error_code == ErrorCode.INVALID_PARAMETER

