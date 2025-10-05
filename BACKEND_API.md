# Deks 1.0 백엔드 API 명세서

## 📋 개요

Deks 1.0 로봇의 백엔드 API는 FastAPI 기반으로 구축되며, 다음과 같은 기능을 제공합니다:

- **로봇 제어**: 이동, 정지, 회전 등의 기본 동작 제어
- **센서 데이터**: 실시간 센서 정보 수집 및 제공
- **자연어 처리**: 사용자 명령을 로봇 제어 명령으로 변환
- **사용자 경험**: 개인화된 서비스 및 학습 기능
- **실시간 통신**: WebSocket을 통한 실시간 데이터 스트리밍

## 🏗️ 아키텍처

```
┌─────────────────┐    ┌─────────────────────────────────────────┐    ┌─────────────────┐
│   Web Client    │◄──►│            FastAPI Server               │◄──►│   ESP32 Robot   │
│   (Browser)     │    │  ┌─────────────────────────────────────┐ │    │   (MicroPython) │
└─────────────────┘    │  │         REST API Layer             │ │    └─────────────────┘
                       │  │  • Robot Control APIs              │ │              │
                       │  │  • Natural Language Processing     │ │              │
                       │  │  • User Experience APIs            │ │              │
                       │  └─────────────────────────────────────┘ │              │
                       │  ┌─────────────────────────────────────┐ │              │
                       │  │        WebSocket Layer              │ │              │
                       │  │  • Real-time Communication         │ │              │
                       │  │  • Live Sensor Data                 │ │              │
                       │  └─────────────────────────────────────┘ │              │
                       │  ┌─────────────────────────────────────┐ │              │
                       │  │       Socket Bridge Module          │ │              │
                       │  │  • TCP Socket Management           │ │              │
                       │  │  • ESP32 Communication             │ │              │
                       │  │  • Message Protocol Handling       │ │              │
                       │  └─────────────────────────────────────┘ │              │
                       │  ┌─────────────────────────────────────┐ │              │
                       │  │         Database Layer              │ │              │
                       │  │  • SQLite Database                 │ │              │
                       │  │  • User Analytics                  │ │              │
                       │  └─────────────────────────────────────┘ │              │
                       └─────────────────────────────────────────┘              │
                                                                              │
                                                                              ▼
                                                                     ┌─────────────────┐
                                                                     │   Wi-Fi TCP     │
                                                                     │   Socket        │
                                                                     │   Connection    │
                                                                     └─────────────────┘
```

## 🌐 API 기본 정보

- **Base URL**: `http://localhost:8000`
- **API Version**: `v1`
- **Content-Type**: `application/json`
- **Authentication**: 현재 미구현 (향후 JWT 토큰 예정)

## 🤖 로봇 제어 API

### 1. 로봇 이동 제어

#### 전진
```http
POST /api/v1/robot/move/forward
Content-Type: application/json

{
  "speed": 50,
  "distance": 100,
  "user_id": "user_001"
}
```

**응답 (성공)**:
```json
{
  "success": true,
  "command_id": "cmd_123",
  "message": "전진 명령을 실행합니다",
  "timestamp": "2024-01-01T12:00:00Z",
  "robot_status": {
    "position": {"x": 0, "y": 0},
    "battery": 85,
    "sensors": {
      "front_distance": 25.5,
      "left_distance": 30.2,
      "right_distance": 28.8
    }
  }
}
```

#### 회전
```http
POST /api/v1/robot/move/turn
Content-Type: application/json

{
  "direction": "left",
  "angle": 90,
  "speed": 30,
  "user_id": "user_001"
}
```

**응답 (성공)**:
```json
{
  "success": true,
  "command_id": "cmd_124",
  "message": "왼쪽으로 90도 회전합니다",
  "timestamp": "2024-01-01T12:01:00Z",
  "robot_status": {
    "position": {"x": 0, "y": 0},
    "orientation": 90,
    "battery": 84,
    "sensors": {
      "front_distance": 25.5,
      "left_distance": 30.2,
      "right_distance": 28.8
    }
  }
}
```

#### 정지
```http
POST /api/v1/robot/stop
Content-Type: application/json

{
  "user_id": "user_001"
}
```

**응답 (성공)**:
```json
{
  "success": true,
  "command_id": "cmd_125",
  "message": "로봇을 정지합니다",
  "timestamp": "2024-01-01T12:02:00Z",
  "robot_status": {
    "position": {"x": 0, "y": 0},
    "battery": 84,
    "sensors": {
      "front_distance": 25.5,
      "left_distance": 30.2,
      "right_distance": 28.8
    }
  }
}
```

### 2. 로봇 상태 조회

#### 현재 상태
```http
GET /api/v1/robot/status
```

**응답**:
```json
{
  "success": true,
  "robot_status": {
    "position": {"x": 10.5, "y": 15.2},
    "orientation": 45,
    "battery": 85,
    "is_moving": false,
    "safety_mode": "normal",
    "sensors": {
      "front_distance": 25.5,
      "left_distance": 30.2,
      "right_distance": 28.8,
      "drop_detected": false
    },
    "led_expression": "happy",
    "buzzer_active": false,
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## 🎯 자연어 처리 API

### 1. 명령 파싱

```http
POST /api/v1/nlp/parse-command
Content-Type: application/json

{
  "message": "오른쪽으로 돌아줘",
  "user_id": "user_001",
  "session_id": "session_123"
}
```

**응답 (성공)**:
```json
{
  "success": true,
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

**응답 (실패)**:
```json
{
  "success": false,
  "error": "NLP_PARSE_ERROR",
  "message": "명령을 이해할 수 없습니다",
  "suggestions": [
    "앞으로 가줘",
    "왼쪽으로 돌아줘",
    "정지해줘"
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 2. 지원 명령어 목록

```http
GET /api/v1/nlp/commands
```

**응답**:
```json
{
  "success": true,
  "supported_commands": [
    {
      "action": "move_forward",
      "patterns": ["앞으로", "전진", "가줘", "이동해"],
      "description": "로봇을 앞으로 이동시킵니다"
    },
    {
      "action": "turn_left",
      "patterns": ["왼쪽", "좌회전", "왼쪽으로"],
      "description": "로봇을 왼쪽으로 회전시킵니다"
    },
    {
      "action": "turn_right",
      "patterns": ["오른쪽", "우회전", "오른쪽으로"],
      "description": "로봇을 오른쪽으로 회전시킵니다"
    },
    {
      "action": "stop",
      "patterns": ["정지", "멈춰", "그만"],
      "description": "로봇을 정지시킵니다"
    },
    {
      "action": "spin",
      "patterns": ["빙글빙글", "돌아", "회전해"],
      "description": "로봇을 제자리에서 회전시킵니다"
    }
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 📊 센서 데이터 API

### 1. 거리 센서 데이터

```http
GET /api/v1/sensors/distance
```

**응답**:
```json
{
  "success": true,
  "sensor_data": {
    "front": 25.5,
    "left": 30.2,
    "right": 28.8,
    "unit": "cm",
    "timestamp": "2024-01-01T12:00:00Z",
    "status": "normal"
  }
}
```

### 2. 위치 데이터

```http
GET /api/v1/sensors/position
```

**응답**:
```json
{
  "success": true,
  "position_data": {
    "x": 10.5,
    "y": 15.2,
    "orientation": 45,
    "unit": "cm",
    "timestamp": "2024-01-01T12:00:00Z",
    "accuracy": "high"
  }
}
```

### 3. 배터리 상태

```http
GET /api/v1/sensors/battery
```

**응답**:
```json
{
  "success": true,
  "battery_data": {
    "level": 85,
    "voltage": 3.7,
    "status": "good",
    "estimated_runtime": "2.5 hours",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## 🎭 표현 제어 API

### 1. LED 표정 설정

```http
POST /api/v1/expression/led
Content-Type: application/json

{
  "expression": "happy",
  "duration": 3000,
  "user_id": "user_001"
}
```

**지원하는 표정**:
- `happy`: 행복한 표정
- `sad`: 슬픈 표정
- `surprised`: 놀란 표정
- `neutral`: 평범한 표정
- `heart`: 하트 표정

### 2. 버저 소리 제어

```http
POST /api/v1/expression/buzzer
Content-Type: application/json

{
  "sound": "beep",
  "frequency": 1000,
  "duration": 500,
  "user_id": "user_001"
}
```

**지원하는 소리**:
- `beep`: 기본 비프음
- `melody`: 멜로디
- `alarm`: 경보음
- `success`: 성공음
- `error`: 에러음

**응답 (성공)**:
```json
{
  "success": true,
  "message": "버저 소리가 재생되었습니다",
  "sound_info": {
    "type": "beep",
    "frequency": 1000,
    "duration": 500
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 💬 채팅 상호작용 API

### 1. 메시지 전송 및 응답

```http
POST /api/v1/chat/message
Content-Type: application/json

{
  "message": "안녕 덱스",
  "user_id": "user_001",
  "session_id": "session_123"
}
```

**응답 (성공)**:
```json
{
  "success": true,
  "message_id": "msg_456",
  "response": "안녕하세요! 저는 덱스에요. 당신은 누구신가요?",
  "emotion": "happy",
  "timestamp": "2024-01-01T12:00:00Z",
  "context": {
    "conversation_type": "greeting",
    "user_name": null,
    "robot_mood": "friendly"
  }
}
```

### 2. 대화 기록 조회

```http
GET /api/v1/chat/history?user_id=user_001&limit=20&offset=0
```

**응답**:
```json
{
  "success": true,
  "conversations": [
    {
      "message_id": "msg_456",
      "user_message": "안녕 덱스",
      "robot_response": "안녕하세요! 저는 덱스에요. 당신은 누구신가요?",
      "timestamp": "2024-01-01T12:00:00Z",
      "emotion": "happy"
    }
  ],
  "total_count": 1,
  "has_more": false
}
```

### 3. 대화 컨텍스트 관리

```http
GET /api/v1/chat/context?user_id=user_001&session_id=session_123
```

**응답**:
```json
{
  "success": true,
  "context": {
    "user_id": "user_001",
    "session_id": "session_123",
    "user_name": "김철수",
    "conversation_count": 5,
    "last_interaction": "2024-01-01T12:00:00Z",
    "robot_mood": "friendly",
    "current_topic": "introduction",
    "remembered_info": {
      "user_preferences": ["친근한 대화", "간단한 설명"],
      "recent_commands": ["앞으로 가줘", "돌아줘"]
    }
  }
}
```

### 4. 감정 상태 관리

```http
POST /api/v1/chat/emotion
Content-Type: application/json

{
  "emotion": "happy",
  "user_id": "user_001",
  "reason": "사용자가 인사했음"
}
```

**지원하는 감정 상태**:
- `happy`: 행복함
- `sad`: 슬픔
- `excited`: 흥분
- `calm`: 평온함
- `curious`: 호기심
- `confused`: 혼란

### 5. 대화 패턴 학습

```http
POST /api/v1/chat/learning
Content-Type: application/json

{
  "user_id": "user_001",
  "interaction_data": {
    "user_message": "안녕 덱스",
    "robot_response": "안녕하세요! 저는 덱스에요.",
    "user_feedback": "positive",
    "context": "greeting"
  }
}
```

### 6. 대화 시나리오 예시

#### 인사 시나리오
```json
{
  "user_input": "안녕 덱스",
  "robot_response": "안녕하세요! 저는 덱스에요. 당신은 누구신가요?",
  "follow_up": "오늘은 어떤 도움이 필요하신가요?"
}
```

#### 자기소개 시나리오
```json
{
  "user_input": "나는 김철수야",
  "robot_response": "안녕하세요 김철수님! 만나서 반가워요. 저는 덱스라고 해요.",
  "follow_up": "김철수님, 저는 로봇이에요. 이동하고 센서로 주변을 감지할 수 있어요."
}
```

#### 질문 응답 시나리오
```json
{
  "user_input": "넌 뭐야?",
  "robot_response": "저는 덱스라는 로봇이에요! 이동하고 센서로 주변을 감지할 수 있어요.",
  "follow_up": "앞으로 가달라고 하시면 이동할 수 있어요. 한번 해보실래요?"
}
```

#### 작별 인사 시나리오
```json
{
  "user_input": "안녕히 가",
  "robot_response": "안녕히 가세요 김철수님! 또 만나요. 좋은 하루 되세요!",
  "follow_up": null,
  "emotion": "happy"
}
```

## 👤 사용자 경험 API

### 1. 사용자 패턴 분석

```http
GET /api/v1/analytics/user-patterns?user_id=user_001&days=7
```

**응답**:
```json
{
  "success": true,
  "user_id": "user_001",
  "analysis_period": "7_days",
  "frequent_commands": [
    {
      "command": "앞으로 가줘",
      "frequency": 15,
      "success_rate": 0.93
    },
    {
      "command": "오른쪽으로 돌아줘",
      "frequency": 8,
      "success_rate": 0.88
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

### 2. 스마트 제안

```http
GET /api/v1/analytics/suggestions?user_id=user_001&context=idle
```

**응답**:
```json
{
  "success": true,
  "user_id": "user_001",
  "context": "idle",
  "suggestions": [
    {
      "command": "앞으로 가줘",
      "confidence": 0.85,
      "reason": "자주 사용하는 명령어입니다"
    },
    {
      "command": "빙글빙글 돌아줘",
      "confidence": 0.72,
      "reason": "이 시간대에 자주 사용합니다"
    }
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 3. 사용자 피드백

```http
POST /api/v1/analytics/feedback
Content-Type: application/json

{
  "user_id": "user_001",
  "command_id": "cmd_123",
  "satisfaction": 4,
  "feedback": "정확하게 실행되었습니다",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🌉 Socket Bridge 통신 (FastAPI 통합)

### 개요

Socket Bridge는 FastAPI 서버 내부의 모듈로 통합되어 ESP32 로봇과의 TCP Socket 통신을 담당합니다. 별도의 프로세스가 아닌 FastAPI 애플리케이션의 일부로 동작합니다.

### 통합 아키텍처

```
FastAPI Server (통합)
├── REST API Layer
├── WebSocket Layer  
├── Socket Bridge Module ← ESP32 통신 담당
└── Database Layer
```

### 통합의 장점

1. **단일 프로세스**: 관리가 간단하고 리소스 효율적
2. **공유 상태**: 메모리 내에서 로봇 상태 공유
3. **동기화**: API와 Socket 통신 간 완벽한 동기화
4. **에러 처리**: 통합된 에러 처리 및 로깅
5. **확장성**: FastAPI의 비동기 처리 활용

### FastAPI 내 Socket Bridge 모듈 구조

```python
# FastAPI 애플리케이션 구조
from fastapi import FastAPI
from .socket_bridge import SocketBridgeManager
from .robot_controller import RobotController

app = FastAPI()

# Socket Bridge 매니저 초기화
socket_bridge = SocketBridgeManager()
robot_controller = RobotController(socket_bridge)

# API 라우터 등록
app.include_router(robot_controller.router)
```

### Socket Bridge 설정

- **포트**: 8888 (ESP32 연결용)
- **프로토콜**: TCP Socket
- **인코딩**: UTF-8
- **메시지 형식**: JSON

### ESP32 ↔ Socket Bridge 메시지 형식

#### 1. 명령 전송 (FastAPI → ESP32)

**형식**:
```json
{
  "type": "command",
  "command_id": "cmd_123",
  "action": "move_forward",
  "parameters": {
    "speed": 50,
    "distance": 100
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**지원 명령어**:
```json
{
  "move_forward": {
    "parameters": {
      "speed": "int (0-100)",
      "distance": "int (cm)"
    }
  },
  "turn": {
    "parameters": {
      "direction": "string (left/right)",
      "angle": "int (degrees)",
      "speed": "int (0-100)"
    }
  },
  "stop": {
    "parameters": {}
  },
  "set_led": {
    "parameters": {
      "expression": "string (happy/sad/surprised/neutral/heart)"
    }
  },
  "set_buzzer": {
    "parameters": {
      "sound": "string (beep/melody/alarm/success/error)",
      "frequency": "int (Hz)",
      "duration": "int (ms)"
    }
  }
}
```

#### 2. 센서 데이터 수신 (ESP32 → FastAPI)

**형식**:
```json
{
  "type": "sensor_data",
  "robot_id": "deks_001",
  "data": {
    "position": {"x": 10.5, "y": 15.2},
    "orientation": 45,
    "battery": 85,
    "is_moving": false,
    "sensors": {
      "front_distance": 25.5,
      "left_distance": 30.2,
      "right_distance": 28.8,
      "drop_detected": false
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 3. 명령 실행 결과 (ESP32 → FastAPI)

**성공 응답**:
```json
{
  "type": "command_result",
  "command_id": "cmd_123",
  "success": true,
  "message": "전진 명령이 완료되었습니다",
  "data": {
    "final_position": {"x": 15.5, "y": 15.2},
    "distance_traveled": 5.0
  },
  "timestamp": "2024-01-01T12:00:05Z"
}
```

**실패 응답**:
```json
{
  "type": "command_result",
  "command_id": "cmd_123",
  "success": false,
  "error": "SAFETY_VIOLATION",
  "message": "낙하 위험으로 인해 명령을 중단했습니다",
  "data": {
    "reason": "drop_detected",
    "position": {"x": 10.5, "y": 15.2}
  },
  "timestamp": "2024-01-01T12:00:02Z"
}
```

#### 4. 안전 경고 (ESP32 → FastAPI)

```json
{
  "type": "safety_warning",
  "robot_id": "deks_001",
  "warning_type": "drop_detected",
  "message": "낙하 위험 감지! 즉시 정지합니다",
  "action_taken": "emergency_stop",
  "data": {
    "sensor_reading": 5.2,
    "threshold": 10.0,
    "position": {"x": 10.5, "y": 15.2}
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 5. 연결 상태 (ESP32 ↔ Socket Bridge)

**연결 확인**:
```json
{
  "type": "ping",
  "robot_id": "deks_001",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**연결 응답**:
```json
{
  "type": "pong",
  "robot_id": "deks_001",
  "status": "connected",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### FastAPI 통합 Socket Bridge API

#### 1. 로봇 연결 관리 (내부 API)

**로봇 연결 상태 조회**:
```http
GET /api/v1/robots/status
```

**응답**:
```json
{
  "success": true,
  "connected_robots": [
    {
      "robot_id": "deks_001",
      "ip_address": "192.168.1.100",
      "port": 8888,
      "status": "connected",
      "last_seen": "2024-01-01T12:00:00Z",
      "battery_level": 85,
      "connection_quality": "excellent"
    }
  ],
  "total_connected": 1,
  "socket_bridge_status": "active",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**특정 로봇 상세 상태**:
```http
GET /api/v1/robots/{robot_id}/status
```

**응답**:
```json
{
  "success": true,
  "robot": {
    "robot_id": "deks_001",
    "ip_address": "192.168.1.100",
    "port": 8888,
    "status": "connected",
    "connection_time": "2024-01-01T11:30:00Z",
    "last_seen": "2024-01-01T12:00:00Z",
    "commands_sent": 15,
    "commands_completed": 14,
    "commands_failed": 1,
    "battery_level": 85,
    "connection_quality": "excellent",
    "socket_bridge_metrics": {
      "avg_response_time": 8.5,
      "packet_loss": 0.0,
      "last_ping": "2024-01-01T12:00:00Z"
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 2. 내부 명령 전송 (Socket Bridge)

**로봇 제어 명령 (내부적으로 Socket Bridge 사용)**:
```http
POST /api/v1/robot/move/forward
Content-Type: application/json

{
  "speed": 50,
  "distance": 100,
  "user_id": "user_001"
}
```

**내부 처리 과정**:
1. FastAPI가 요청을 받음
2. Socket Bridge 모듈이 ESP32에 명령 전송
3. ESP32가 명령 실행
4. 결과를 Socket Bridge가 수신
5. FastAPI가 클라이언트에 응답

**응답**:
```json
{
  "success": true,
  "command_id": "cmd_123",
  "message": "전진 명령을 실행합니다",
  "socket_bridge_status": "command_sent",
  "timestamp": "2024-01-01T12:00:00Z",
  "estimated_completion": "2024-01-01T12:00:05Z"
}
```

#### 3. 통합 실시간 데이터 스트림

**FastAPI WebSocket 연결 (Socket Bridge 통합)**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/robot');
```

**실시간 센서 데이터**:
```json
{
  "type": "sensor_stream",
  "robot_id": "deks_001",
  "data": {
    "front_distance": 25.5,
    "left_distance": 30.2,
    "right_distance": 28.8,
    "battery": 85,
    "position": {"x": 10.5, "y": 15.2}
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**명령 실행 진행 상황**:
```json
{
  "type": "command_progress",
  "command_id": "cmd_123",
  "robot_id": "deks_001",
  "progress": 60,
  "message": "전진 중... (60% 완료)",
  "current_position": {"x": 13.0, "y": 15.2},
  "timestamp": "2024-01-01T12:00:03Z"
}
```

### 에러 처리

#### Socket Bridge 에러 코드

| 코드 | 설명 |
|------|------|
| `ROBOT_NOT_CONNECTED` | 로봇이 연결되지 않음 |
| `CONNECTION_TIMEOUT` | 연결 시간 초과 |
| `COMMAND_TIMEOUT` | 명령 실행 시간 초과 |
| `INVALID_COMMAND` | 잘못된 명령 형식 |
| `ROBOT_BUSY` | 로봇이 다른 명령 실행 중 |
| `SOCKET_ERROR` | 소켓 통신 오류 |

#### 에러 응답 예시

```json
{
  "success": false,
  "error": "ROBOT_NOT_CONNECTED",
  "message": "로봇 'deks_001'이 연결되지 않았습니다",
  "details": {
    "robot_id": "deks_001",
    "last_seen": "2024-01-01T11:55:00Z",
    "retry_count": 3
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 통합 성능 요구사항

- **전체 응답 시간**: < 100ms (API 요청 → ESP32 응답)
- **Socket Bridge 지연**: < 10ms (FastAPI ↔ ESP32)
- **명령 전송**: < 5ms
- **데이터 수신**: < 5ms
- **연결 유지**: 지속적 핑/퐁 (30초 간격)
- **동시 연결**: 최대 5개 로봇
- **FastAPI 처리**: < 50ms (비동기 처리)
- **메모리 사용**: < 100MB (통합 프로세스)

## 🔌 WebSocket 실시간 통신

### 연결 설정

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/robot');
```

### 이벤트 타입

#### 1. 로봇 상태 업데이트
```json
{
  "type": "robot_status_update",
  "data": {
    "position": {"x": 10.5, "y": 15.2},
    "orientation": 45,
    "battery": 85,
    "is_moving": true,
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### 2. 센서 데이터 스트림
```json
{
  "type": "sensor_data",
  "data": {
    "front_distance": 25.5,
    "left_distance": 30.2,
    "right_distance": 28.8,
    "drop_detected": false,
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### 3. 명령 실행 결과
```json
{
  "type": "command_result",
  "data": {
    "command_id": "cmd_123",
    "success": true,
    "message": "전진 명령이 완료되었습니다",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### 4. 안전 경고
```json
{
  "type": "safety_warning",
  "data": {
    "warning_type": "drop_detected",
    "message": "낙하 위험 감지! 즉시 정지합니다",
    "action_taken": "emergency_stop",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### 5. 자연어 처리 결과
```json
{
  "type": "nlp_result",
  "data": {
    "command_id": "cmd_456",
    "action": "turn_right",
    "confidence": 0.95,
    "response": "오른쪽으로 회전합니다!",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## ⚠️ 에러 처리

### 에러 코드

| 코드 | 설명 |
|------|------|
| `ROBOT_NOT_CONNECTED` | 로봇 연결 실패 |
| `SENSOR_ERROR` | 센서 오류 |
| `BATTERY_LOW` | 배터리 부족 |
| `SAFETY_VIOLATION` | 안전 규칙 위반 |
| `NLP_PARSE_ERROR` | 자연어 파싱 오류 |
| `NLP_UNKNOWN_COMMAND` | 알 수 없는 명령 |
| `DATABASE_ERROR` | 데이터베이스 오류 |
| `VALIDATION_ERROR` | 요청 데이터 검증 오류 |

### 에러 응답 형식

```json
{
  "success": false,
  "error": "ROBOT_NOT_CONNECTED",
  "message": "로봇과의 연결이 끊어졌습니다",
  "details": {
    "last_seen": "2024-01-01T11:55:00Z",
    "retry_count": 3
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 📝 요청/응답 예시

### 성공적인 명령 실행 플로우

1. **자연어 명령 파싱**:
```http
POST /api/v1/nlp/parse-command
{
  "message": "앞으로 가줘",
  "user_id": "user_001"
}
```

2. **로봇 제어 명령 실행**:
```http
POST /api/v1/robot/move/forward
{
  "speed": 50,
  "distance": 100,
  "user_id": "user_001"
}
```

3. **WebSocket으로 실시간 상태 업데이트**:
```json
{
  "type": "robot_status_update",
  "data": {
    "position": {"x": 5.0, "y": 0.0},
    "is_moving": true,
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

4. **명령 완료 알림**:
```json
{
  "type": "command_result",
  "data": {
    "command_id": "cmd_123",
    "success": true,
    "message": "전진 명령이 완료되었습니다",
    "timestamp": "2024-01-01T12:00:05Z"
  }
}
```

## 🚀 성능 요구사항

- **응답 시간**: < 100ms (일반 API)
- **자연어 처리**: < 50ms
- **WebSocket 지연**: < 20ms
- **동시 연결**: 최대 10개 클라이언트
- **데이터베이스**: SQLite, < 10ms 쿼리 시간

## 🔒 보안 고려사항

- **입력 검증**: 모든 사용자 입력 검증
- **Rate Limiting**: API 호출 제한
- **CORS**: 적절한 CORS 설정
- **데이터 암호화**: 민감한 데이터 암호화
- **로깅**: 모든 API 호출 로깅

---

**Deks 1.0 백엔드 API** - 안전하고 효율적인 로봇 제어를 위한 완전한 API 명세서
