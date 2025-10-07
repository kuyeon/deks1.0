# Deks 1.0 에러 처리 시스템

## 📋 개요

Deks 1.0 프로젝트의 **Error Handling (에러 처리)** 시스템이 성공적으로 구축되었습니다. 이 문서는 에러 처리 시스템의 구조, 사용법, 그리고 모범 사례를 설명합니다.

## 🎯 주요 기능

### ✅ 완료된 기능

1. **커스텀 예외 계층 구조** - 체계적이고 의미 있는 예외 클래스
2. **표준화된 에러 응답** - 일관된 JSON 에러 응답 형식
3. **전역 에러 핸들러** - FastAPI 애플리케이션 레벨 예외 처리
4. **에러 추적 및 통계** - 실시간 에러 모니터링
5. **HTTP 상태 코드 매핑** - 적절한 HTTP 상태 코드 자동 할당
6. **원본 예외 래핑** - 디버깅을 위한 상세 정보 보존

## 🏗️ 시스템 구조

### 1. 커스텀 예외 클래스 (`app/core/exceptions.py`)

#### 예외 계층 구조

```
DeksBaseException (기본 클래스)
├── 일반 에러 (1000번대)
│   ├── InternalServerException
│   ├── ServiceUnavailableException
│   ├── TimeoutException
│   └── ConfigurationException
├── 요청 관련 에러 (2000번대)
│   ├── InvalidRequestException
│   ├── ValidationException
│   ├── MissingParameterException
│   └── InvalidParameterException
├── 리소스 에러 (4000번대)
│   ├── ResourceNotFoundException
│   └── ResourceAlreadyExistsException
├── 데이터베이스 에러 (5000번대)
│   ├── DatabaseException
│   ├── DatabaseConnectionException
│   ├── DatabaseQueryException
│   └── DatabaseIntegrityException
├── 로봇 제어 에러 (6000번대)
│   ├── RobotNotConnectedException
│   ├── RobotCommandFailedException
│   ├── RobotCommandTimeoutException
│   ├── RobotInvalidStateException
│   ├── RobotSafetyViolationException
│   ├── RobotHardwareException
│   └── RobotCommunicationException
├── 센서 관련 에러 (7000번대)
│   ├── SensorNotFoundException
│   ├── SensorReadException
│   └── SensorOutOfRangeException
├── 통신 관련 에러 (8000번대)
│   ├── SocketConnectionException
│   ├── SocketDisconnectedException
│   ├── SocketTimeoutException
│   ├── WebSocketException
│   ├── MessageParseException
│   └── MessageSendException
└── NLP/채팅 에러 (9000번대)
    ├── NLPParseException
    ├── ChatContextException
    └── InvalidCommandException
```

#### 에러 코드 규칙

- **1000번대**: 일반 에러 (시스템 레벨)
- **2000번대**: 요청/검증 에러 (클라이언트 입력)
- **3000번대**: 인증/권한 에러
- **4000번대**: 리소스 에러
- **5000번대**: 데이터베이스 에러
- **6000번대**: 로봇 제어 에러
- **7000번대**: 센서 에러
- **8000번대**: 통신 에러
- **9000번대**: NLP/채팅 에러

### 2. 에러 응답 모델 (`app/models/error_models.py`)

#### 표준 에러 응답

```json
{
  "success": false,
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
```

#### 검증 에러 응답

```json
{
  "success": false,
  "error_code": 2001,
  "error_name": "VALIDATION_ERROR",
  "message": "입력값 검증에 실패했습니다",
  "errors": [
    {
      "field": "speed",
      "message": "속도는 0에서 100 사이여야 합니다",
      "code": "value_error.number.not_gt"
    }
  ],
  "timestamp": "2024-01-01T12:00:00.000Z",
  "path": "/api/v1/robot/move/forward"
}
```

### 3. 전역 에러 핸들러 (`app/core/error_handlers.py`)

#### 등록된 핸들러

1. **Deks 커스텀 예외 핸들러** - `DeksBaseException` 처리
2. **Pydantic 검증 에러 핸들러** - `RequestValidationError` 처리
3. **HTTP 예외 핸들러** - `HTTPException` 처리
4. **일반 예외 핸들러** - 모든 예외의 최종 fallback

#### 에러 추적 기능

- 에러 발생 횟수 카운팅
- 에러 코드별 통계
- 엔드포인트별 에러 통계
- 최근 에러 로그 (최대 100개)

## 📖 사용 가이드

### 1. 예외 발생시키기

#### 기본 사용법

```python
from app.core.exceptions import RobotNotConnectedException

# 로봇이 연결되지 않았을 때
raise RobotNotConnectedException(robot_id="deks_001")
```

#### 상세 정보 포함

```python
from app.core.exceptions import RobotCommandFailedException

# 명령 실패 시
raise RobotCommandFailedException(
    command="move_forward",
    reason="타임아웃 발생",
    details={"timeout": 10.0}
)
```

#### 원본 예외 래핑

```python
from app.core.exceptions import wrap_exception, DatabaseException

try:
    # 데이터베이스 작업
    db.execute(query)
except Exception as e:
    # 원본 예외를 래핑하여 던짐
    raise DatabaseException(
        message="쿼리 실행 실패",
        original_exception=e
    )
```

### 2. 서비스 레이어에서 사용

```python
from app.core.exceptions import (
    InvalidParameterException,
    RobotCommandFailedException
)

class RobotController:
    async def move_forward(self, speed: int, distance: int):
        # 파라미터 검증
        if speed < 0 or speed > 100:
            raise InvalidParameterException(
                parameter_name="speed",
                reason=f"속도는 0에서 100 사이여야 합니다 (입력값: {speed})"
            )
        
        try:
            # 로봇 명령 실행
            await self._send_command(...)
        except Exception as e:
            raise RobotCommandFailedException(
                command="move_forward",
                reason=str(e),
                original_exception=e
            )
```

### 3. API 엔드포인트에서 사용

```python
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()

class MoveRequest(BaseModel):
    speed: int = Field(ge=0, le=100, description="속도 (0-100)")
    distance: int = Field(ge=0, le=200, description="거리 (0-200)")

@router.post("/move/forward")
async def move_forward(request: MoveRequest):
    # 예외는 자동으로 전역 핸들러가 처리
    # Pydantic 검증도 자동으로 처리됨
    socket_bridge = await get_socket_bridge()
    await socket_bridge.robot_controller.move_forward(
        request.speed,
        request.distance
    )
    
    return {"success": True, "message": "명령 전송 완료"}
```

### 4. 에러 통계 조회

```bash
# HTTP GET 요청
GET /errors/statistics

# 응답
{
  "success": true,
  "statistics": {
    "total_errors": 42,
    "errors_by_code": {
      "ROBOT_COMMAND_FAILED": 15,
      "VALIDATION_ERROR": 12,
      "SOCKET_DISCONNECTED": 8
    },
    "errors_by_endpoint": {
      "/api/v1/robot/move/forward": 15,
      "/api/v1/sensors/latest": 7
    },
    "last_error_time": "2024-01-01T12:00:00.000Z"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## 🎨 HTTP 상태 코드 매핑

| 에러 유형 | HTTP 상태 코드 | 설명 |
|---------|--------------|------|
| `VALIDATION_ERROR`, `INVALID_PARAMETER` | 400 | 잘못된 요청 |
| `UNAUTHORIZED`, `INVALID_TOKEN` | 401 | 인증 실패 |
| `FORBIDDEN` | 403 | 권한 없음 |
| `RESOURCE_NOT_FOUND`, `ROBOT_NOT_CONNECTED` | 404 | 리소스를 찾을 수 없음 |
| `RESOURCE_CONFLICT` | 409 | 리소스 충돌 |
| `INTERNAL_SERVER_ERROR`, `DATABASE_ERROR` | 500 | 내부 서버 에러 |
| `SERVICE_UNAVAILABLE` | 503 | 서비스 사용 불가 |
| `TIMEOUT_ERROR`, `ROBOT_COMMAND_TIMEOUT` | 504 | 타임아웃 |

## 🧪 테스트

### 단위 테스트

```bash
# 에러 처리 단위 테스트
python -m pytest tests/test_error_handling.py -v
```

### 통합 테스트

```bash
# API 에러 처리 통합 테스트
python -m pytest tests/test_error_api_integration.py -v
```

### 주요 테스트 케이스

- ✅ 커스텀 예외 생성 및 변환
- ✅ HTTP 상태 코드 매핑
- ✅ 에러 응답 형식 검증
- ✅ 검증 에러 처리
- ✅ 원본 예외 래핑
- ✅ 에러 통계 추적

## 📊 모니터링

### 로그 확인

```bash
# 에러 로그 확인
tail -f backend/logs/deks.log | grep ERROR

# 경고 로그 확인
tail -f backend/logs/deks.log | grep WARNING
```

### 에러 통계 API

```bash
# 실시간 에러 통계 조회
curl http://localhost:8000/errors/statistics
```

## 🔧 모범 사례

### 1. 적절한 예외 선택

```python
# ✅ 좋은 예: 명확한 예외 사용
raise RobotNotConnectedException(robot_id="deks_001")

# ❌ 나쁜 예: 일반적인 예외 사용
raise Exception("로봇이 연결되지 않음")
```

### 2. 상세한 에러 메시지

```python
# ✅ 좋은 예: 구체적인 정보 제공
raise InvalidParameterException(
    parameter_name="speed",
    reason=f"속도는 0에서 100 사이여야 합니다 (입력값: {speed})"
)

# ❌ 나쁜 예: 애매한 메시지
raise InvalidParameterException("잘못된 파라미터")
```

### 3. 원본 예외 보존

```python
# ✅ 좋은 예: 원본 예외 래핑
try:
    risky_operation()
except Exception as e:
    raise RobotCommandFailedException(
        command="test",
        reason="실패",
        original_exception=e  # 디버깅 정보 보존
    )

# ❌ 나쁜 예: 원본 예외 손실
try:
    risky_operation()
except Exception:
    raise RobotCommandFailedException("실패")
```

### 4. 계층별 에러 처리

```python
# 서비스 레이어: 비즈니스 로직 예외
class RobotController:
    def move_forward(self, speed: int):
        if speed < 0:
            raise InvalidParameterException(...)

# API 레이어: 예외를 그대로 전파 (전역 핸들러가 처리)
@router.post("/move")
async def move(request: MoveRequest):
    await robot_controller.move_forward(request.speed)
    return {"success": True}
```

## 🚀 향후 개선 사항

### 계획 중인 기능

- [ ] **Circuit Breaker 패턴** - 연속적인 에러 시 서비스 보호
- [ ] **Retry 메커니즘** - 일시적 에러 자동 재시도
- [ ] **에러 알림 시스템** - 심각한 에러 발생 시 알림
- [ ] **에러 대시보드** - 실시간 에러 모니터링 UI
- [ ] **에러 분석 리포트** - 주기적인 에러 분석 보고서

## 📝 관련 문서

- [API 문서](/docs) - FastAPI 자동 생성 문서
- [테스트 문서](../tests/README.md) - 테스트 시스템 가이드
- [아키텍처 문서](../../ARCHITECTURE.md) - 시스템 전체 구조

## 🎉 결론

Deks 1.0의 2순위 개발 작업인 **Error Handling 시스템**이 성공적으로 구축되었습니다:

- ✅ **체계적인 예외 계층** 완성
- ✅ **표준화된 에러 응답** 구현
- ✅ **전역 에러 핸들러** 설정
- ✅ **에러 추적 및 통계** 시스템 구축
- ✅ **포괄적인 테스트** 작성

이제 안정적이고 유지보수가 쉬운 에러 처리 시스템이 마련되었으며, 프로덕션 환경에서도 안심하고 사용할 수 있습니다.

---

*에러 처리 시스템 구축 완료 - 2025년 10월*

