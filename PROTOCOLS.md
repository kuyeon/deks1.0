# Deks 1.0 통신 프로토콜

## 🌐 전체 통신 구조

```
ESP32 S3 ←→ Socket ←→ WebSocket Bridge ←→ WebSocket ←→ FastAPI ←→ Web Browser
```

## 📡 프로토콜 계층

### 1. ESP32 ↔ Socket Bridge (Raw Socket)
- **포트**: 8080
- **프로토콜**: TCP Socket
- **데이터 형식**: JSON 문자열
- **인코딩**: UTF-8

### 2. Socket Bridge ↔ FastAPI (WebSocket)
- **포트**: 8001 (WebSocket Bridge)
- **프로토콜**: WebSocket
- **데이터 형식**: JSON

### 3. FastAPI ↔ Web Browser (HTTP/WebSocket)
- **포트**: 8000 (HTTP), 8001 (WebSocket)
- **프로토콜**: HTTP REST API + WebSocket
- **데이터 형식**: JSON

## 🔌 ESP32 ↔ Socket Bridge 통신

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

## 🛡️ 에러 처리

### 에러 메시지 형식
```json
{
  "type": "error",
  "robot_id": "deks_001",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "error_code": "SENSOR_FAILURE|MOTOR_ERROR|COMMUNICATION_ERROR",
    "error_message": "적외선 센서 오류",
    "severity": "warning|error|critical",
    "recovery_action": "자동 재시도|수동 점검 필요"
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
