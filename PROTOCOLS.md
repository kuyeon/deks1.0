# Deks 1.0 통신 프로토콜

## 🌐 전체 통신 구조

```
ESP32 S3 ←→ TCP Socket ←→ FastAPI Server (Socket Bridge 통합) ←→ Web Browser
```

## 📡 프로토콜 계층

### 1. ESP32 ↔ FastAPI Server (TCP Socket)
- **포트**: 8888 (ESP32 연결용)
- **프로토콜**: TCP Socket
- **데이터 형식**: JSON 문자열
- **인코딩**: UTF-8
- **모듈**: FastAPI 내 Socket Bridge 모듈

### 2. FastAPI ↔ Web Browser (HTTP/WebSocket)
- **포트**: 8000 (HTTP), 8001 (WebSocket)
- **프로토콜**: HTTP REST API + WebSocket
- **데이터 형식**: JSON

## 🔌 ESP32 ↔ FastAPI Server 통신

### 연결 설정
```python
# ESP32에서 연결
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.1.100', 8080))
```

### 메시지 형식
```json
{
  "type": "sensor_data|command_response|status_update|error",
  "robot_id": "deks_001",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    // 메시지 타입별 데이터
  }
}
```

### ESP32 → Socket Bridge (센서 데이터)
```json
{
  "type": "sensor_data",
  "robot_id": "deks_001",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "sensors": {
      "encoder_left": 1234,
      "encoder_right": 1235,
      "ir_drop_sensor": 850,
      "ir_obstacle_sensor": 200,
      "battery_level": 85
    },
    "position": {
      "x": 10.5,
      "y": 20.3,
      "theta": 1.57
    },
    "status": "moving"
  }
}
```

### ESP32 → Socket Bridge (명령 응답)
```json
{
  "type": "command_response",
  "robot_id": "deks_001",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "command_id": "cmd_123",
    "status": "success|error",
    "message": "앞으로 이동 시작",
    "result": {
      "action": "move_forward",
      "speed": 50
    }
  }
}
```

### ESP32 → Socket Bridge (상태 업데이트)
```json
{
  "type": "status_update",
  "robot_id": "deks_001",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "status": "moving|stopped|error|safe_mode",
    "message": "낙하 감지! 안전 모드 진입",
    "safety_triggered": true
  }
}
```

### Socket Bridge → ESP32 (명령)
```json
{
  "type": "robot_command",
  "command_id": "cmd_123",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "action": "move_forward|move_backward|turn_left|turn_right|stop|emergency_stop",
    "parameters": {
      "speed": 50,
      "duration": 2000,
      "angle": 90
    }
  }
}
```

## 🌐 WebSocket Bridge ↔ FastAPI 통신

### WebSocket 연결
```javascript
// 브라우저에서 연결
const ws = new WebSocket('ws://localhost:8001');
```

### 메시지 형식 (WebSocket)
```json
{
  "type": "robot_command|sensor_data|status_update|user_message",
  "source": "esp32|web|bridge",
  "target": "esp32|web|all",
  "robot_id": "deks_001",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    // 메시지 타입별 데이터
  }
}
```

### Bridge → FastAPI (센서 데이터 전달)
```json
{
  "type": "sensor_data",
  "source": "esp32",
  "target": "web",
  "robot_id": "deks_001",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "sensors": {
      "encoder_left": 1234,
      "encoder_right": 1235,
      "ir_drop_sensor": 850,
      "ir_obstacle_sensor": 200,
      "battery_level": 85
    },
    "position": {
      "x": 10.5,
      "y": 20.3,
      "theta": 1.57
    },
    "status": "moving"
  }
}
```

### FastAPI → Bridge (사용자 명령 전달)
```json
{
  "type": "robot_command",
  "source": "web",
  "target": "esp32",
  "robot_id": "deks_001",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "command_id": "cmd_456",
    "action": "move_forward",
    "parameters": {
      "speed": 50,
      "duration": 2000
    }
  }
}
```

## 🚀 FastAPI REST API

### Base URL
```
http://localhost:8000/api/v1
```

### 로봇 제어 API

#### 로봇 상태 조회
```http
GET /robot/status
```

**응답:**
```json
{
  "robot_id": "deks_001",
  "status": "moving",
  "position": {
    "x": 10.5,
    "y": 20.3,
    "theta": 1.57
  },
  "sensors": {
    "ir_drop_sensor": 850,
    "ir_obstacle_sensor": 200,
    "battery_level": 85
  },
  "last_update": "2024-01-01T12:00:00Z"
}
```

#### 로봇 명령 전송
```http
POST /robot/command
Content-Type: application/json

{
  "action": "move_forward",
  "parameters": {
    "speed": 50,
    "duration": 2000
  }
}
```

**응답:**
```json
{
  "command_id": "cmd_789",
  "status": "sent",
  "message": "명령이 로봇으로 전송되었습니다"
}
```

#### 로봇 비상 정지
```http
POST /robot/emergency_stop
```

**응답:**
```json
{
  "status": "emergency_stop",
  "message": "비상 정지 명령 전송됨"
}
```

### 센서 데이터 API

#### 최신 센서 데이터 조회
```http
GET /sensors/latest
```

#### 센서 데이터 히스토리
```http
GET /sensors/history?limit=100&offset=0
```

### 대화 API

#### 메시지 전송
```http
POST /chat/message
Content-Type: application/json

{
  "message": "앞으로 가줘",
  "user_id": "user_001"
}
```

**응답:**
```json
{
  "message_id": "msg_123",
  "response": "앞으로 이동합니다!",
  "action": "move_forward",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 자연어 명령 파싱
```http
POST /api/v1/parse-command
Content-Type: application/json

{
  "message": "오른쪽으로 돌아줘",
  "user_id": "user_001",
  "session_id": "session_123"
}
```

**응답 (성공):**
```json
{
  "command_id": "cmd_456",
  "action": "turn_right",
  "confidence": 0.95,
  "response": "오른쪽으로 회전합니다!",
  "parameters": {
    "angle": 90,
    "speed": 50
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**응답 (실패):**
```json
{
  "command_id": "cmd_457",
  "action": "unknown",
  "confidence": 0.0,
  "response": "이해하지 못했습니다. 다시 말씀해 주세요.",
  "suggestions": [
    "앞으로 가줘",
    "왼쪽으로 돌아줘",
    "정지해줘"
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 지원 명령어 목록 조회
```http
GET /api/v1/commands/supported
```

**응답:**
```json
{
  "commands": {
    "move_forward": {
      "keywords": ["앞으로", "전진", "가줘", "이동해"],
      "description": "로봇을 앞으로 이동시킵니다"
    },
    "turn_left": {
      "keywords": ["왼쪽", "좌회전", "왼쪽으로"],
      "description": "로봇을 왼쪽으로 회전시킵니다"
    },
    "turn_right": {
      "keywords": ["오른쪽", "우회전", "오른쪽으로"],
      "description": "로봇을 오른쪽으로 회전시킵니다"
    },
    "stop": {
      "keywords": ["정지", "멈춰", "그만"],
      "description": "로봇을 정지시킵니다"
    },
    "spin": {
      "keywords": ["빙글빙글", "돌아", "회전해"],
      "description": "로봇을 제자리에서 회전시킵니다"
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 사용자 경험 향상 API

#### 사용자 패턴 분석
```http
GET /api/v1/analytics/user-patterns?user_id=user_001&days=7
```

**응답:**
```json
{
  "user_id": "user_001",
  "analysis_period": "7_days",
  "frequent_commands": [
    {
      "command": "앞으로 가줘",
      "frequency": 15,
      "success_rate": 0.93
    },
    {
      "command": "오른쪽으로 돌아",
      "frequency": 8,
      "success_rate": 0.87
    }
  ],
  "preferred_time_slots": ["morning", "evening"],
  "common_error_patterns": [
    {
      "error_type": "unknown_command",
      "frequency": 3,
      "suggestions": ["앞으로 가줘", "정지해줘"]
    }
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 스마트 제안 조회
```http
GET /api/v1/suggestions/smart?context=idle&user_id=user_001
```

**응답:**
```json
{
  "context": "idle",
  "user_id": "user_001",
  "suggestions": [
    {
      "command": "앞으로 가줘",
      "confidence": 0.85,
      "reason": "자주 사용하는 명령어",
      "time_based": true
    },
    {
      "command": "빙글빙글 돌아",
      "confidence": 0.72,
      "reason": "시간대별 선호 패턴",
      "time_based": true
    }
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 사용자 만족도 평가
```http
POST /api/v1/feedback/satisfaction
Content-Type: application/json

{
  "command_id": "cmd_123",
  "user_satisfaction": 4,
  "emotion": "happy",
  "feedback": "정말 잘 작동해요!"
}
```

**응답:**
```json
{
  "feedback_id": "fb_456",
  "status": "recorded",
  "message": "피드백이 저장되었습니다",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 명령어 학습 데이터 조회
```http
GET /api/v1/learning/command-frequency
```

**응답:**
```json
{
  "global_statistics": {
    "total_commands": 1250,
    "success_rate": 0.89,
    "most_popular": "앞으로 가줘"
  },
  "command_frequency": [
    {
      "command": "앞으로 가줘",
      "count": 450,
      "success_rate": 0.95
    },
    {
      "command": "오른쪽으로 돌아",
      "count": 320,
      "success_rate": 0.91
    }
  ],
  "learning_insights": [
    {
      "pattern": "morning_preference",
      "description": "아침 시간대에 이동 명령을 더 자주 사용",
      "confidence": 0.78
    }
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🔄 실시간 데이터 스트림

### WebSocket 이벤트

#### 센서 데이터 스트림
```json
{
  "event": "sensor_data",
  "data": {
    "robot_id": "deks_001",
    "timestamp": "2024-01-01T12:00:00Z",
    "sensors": {
      "encoder_left": 1234,
      "encoder_right": 1235,
      "ir_drop_sensor": 850,
      "ir_obstacle_sensor": 200
    },
    "position": {
      "x": 10.5,
      "y": 20.3,
      "theta": 1.57
    }
  }
}
```

#### 로봇 상태 변경
```json
{
  "event": "status_change",
  "data": {
    "robot_id": "deks_001",
    "old_status": "moving",
    "new_status": "stopped",
    "reason": "낙하 감지",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### 명령 실행 완료
```json
{
  "event": "command_completed",
  "data": {
    "robot_id": "deks_001",
    "command_id": "cmd_123",
    "status": "success",
    "message": "이동 완료",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### 자연어 명령 파싱 결과
```json
{
  "event": "command_parsed",
  "data": {
    "user_id": "user_001",
    "original_message": "앞으로 가줘",
    "parsed_command": {
      "action": "move_forward",
      "confidence": 0.95,
      "parameters": {
        "speed": 50
      }
    },
    "response": "앞으로 이동합니다!",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### 자연어 파싱 실패
```json
{
  "event": "command_parse_failed",
  "data": {
    "user_id": "user_001",
    "original_message": "어쩌고 저쩌고",
    "error": "명령을 이해하지 못했습니다",
    "suggestions": [
      "앞으로 가줘",
      "왼쪽으로 돌아줘",
      "정지해줘"
    ],
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### 채팅 메시지
```json
{
  "event": "chat_message",
  "data": {
    "user_id": "user_001",
    "message": "안녕 Deks!",
    "response": "안녕하세요! 무엇을 도와드릴까요?",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## 🛡️ 에러 처리

### 에러 메시지 형식
```json
{
  "type": "error",
  "robot_id": "deks_001",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "error_code": "SENSOR_FAILURE|MOTOR_ERROR|COMMUNICATION_ERROR|NLP_PARSE_ERROR|NLP_UNKNOWN_COMMAND",
    "error_message": "적외선 센서 오류",
    "severity": "warning|error|critical",
    "recovery_action": "자동 재시도|수동 점검 필요"
  }
}
```

### 자연어 처리 에러 예시
```json
{
  "type": "error",
  "robot_id": "deks_001",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "error_code": "NLP_UNKNOWN_COMMAND",
    "error_message": "지원하지 않는 명령어입니다",
    "severity": "warning",
    "recovery_action": "명령어 목록 조회 권장",
    "original_input": "어쩌고 저쩌고",
    "suggestions": ["앞으로 가줘", "정지해줘"]
  }
}
```

```json
{
  "type": "error",
  "robot_id": "deks_001",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "error_code": "NLP_PARSE_ERROR",
    "error_message": "자연어 파싱 중 오류 발생",
    "severity": "error",
    "recovery_action": "다시 시도 또는 수동 제어 사용"
  }
}
```

### 연결 끊김 처리
```json
{
  "type": "connection_lost",
  "robot_id": "deks_001",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "component": "esp32|bridge|fastapi",
    "reconnect_attempt": 1,
    "max_attempts": 5
  }
}
```

## 📊 성능 요구사항

### 통신 지연시간
- **ESP32 → Bridge**: < 10ms
- **Bridge → FastAPI**: < 5ms
- **FastAPI → Web**: < 5ms
- **전체 지연**: < 50ms

### 데이터 전송량
- **센서 데이터**: ~500 bytes/sec
- **명령 데이터**: ~100 bytes/sec
- **상태 업데이트**: ~200 bytes/sec

### 연결 안정성
- **자동 재연결**: 3초 간격으로 최대 5회 시도
- **하트비트**: 30초 간격
- **타임아웃**: 5초

---

**Deks 1.0 통신 프로토콜** - 안정적이고 실시간 통신을 위한 프로토콜 명세
