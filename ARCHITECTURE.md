# Deks 1.0 아키텍처 설계

## 🏗️ 전체 시스템 구조

```
┌─────────────────┐    Wi-Fi TCP    ┌─────────────────────────────────────────┐    HTTP/WebSocket   ┌─────────────────┐
|                 |                 │            FastAPI Server               │                     |                 |
│                 │◄───────────────►│  ┌─────────────────────────────────────┐ │◄───────────────────►│  Web Browser    │
│   ESP32 S3      │                 │  │         REST API Layer             │ │                     │                 │
│ (마이크로파이썬)  │                 │  │  • Robot Control APIs              │ │                     │  (프론트엔드)    │
│                 │                 │  │  • Natural Language Processing     │ │                     │                 │
└─────────────────┘                 │  │  • User Experience APIs            │ │                     │                 │
         │                          │  └─────────────────────────────────────┘ │                     │                 │
         ▼                          │  ┌─────────────────────────────────────┐ │                     │                 │
┌─────────────────┐                 │  │        WebSocket Layer              │ │                     │                 │
│   하드웨어 센서   │                 │  │  • Real-time Communication         │ │                     │                 │
│   • FIT0405 모터 │                 │  │  • Live Sensor Data                 │ │                     │                 │
│   • 엔코더       │                 │  └─────────────────────────────────────┘ │                     │                 │
│   • 적외선 센서  │                 │  ┌─────────────────────────────────────┐ │                     │                 │
│   • 1588AS LED  │                 │  │       Socket Bridge Module          │ │                     │                 │
│   • 패시브 버저  │                 │  │  • TCP Socket Management           │ │                     │                 │
└─────────────────┘                 │  │  • ESP32 Communication             │ │                     │                 │
                                    │  │  • Message Protocol Handling       │ │                     │                 │
                                    │  └─────────────────────────────────────┘ │                     │                 │
                                    │  ┌─────────────────────────────────────┐ │                     │                 │
                                    │  │         Database Layer              │ │                     │                 │
                                    │  │  • SQLite Database                 │ │                     │                 │
                                    │  │  • User Analytics                  │ │                     │                 │
                                    │  └─────────────────────────────────────┘ │                     │                 │
                                    └─────────────────────────────────────────┘                     └─────────────────┘
```

## 🧩 컴포넌트별 상세 구조

### 1. ESP32 S3 (로봇 두뇌)
```
┌─────────────────────────────────────────┐
│              ESP32 S3                   │
├─────────────────────────────────────────┤
│  • 마이크로파이썬 펌웨어                   │
│  • Wi-Fi 클라이언트                       │
│  • TCP Socket 클라이언트                  │
├─────────────────────────────────────────┤
│              제어 모듈                   │
│  • 모터 제어 (L298N)                     │
│  • 엔코더 읽기                           │
│  • 센서 데이터 수집                       │
│  • 안전 시스템                           │
├─────────────────────────────────────────┤
│              통신 모듈                   │
│  • 명령 수신 및 처리                      │
│  • 센서 데이터 전송                       │
│  • 상태 보고                             │
└─────────────────────────────────────────┘
```

### 2. FastAPI 서버 (통합)
```
┌─────────────────────────────────────────┐
│            FastAPI Server               │
├─────────────────────────────────────────┤
│  • REST API 엔드포인트                    │
│  • WebSocket 연결 관리                    │
│  • 명령 처리 및 라우팅                     │
│  • 센서 데이터 저장/분석                   │
├─────────────────────────────────────────┤
│              핵심 모듈                    │
│  • 로봇 제어 API                          │
│  • 센서 데이터 API                        │
│  • 대화 처리 API                          │
│  • 채팅 상호작용 API                      │
│  • 매핑 데이터 API                        │
│  • 자연어 처리 모듈                       │
│  • SQLite 데이터베이스                     │
│  • Socket Bridge 모듈 (ESP32 통신)        │
├─────────────────────────────────────────┤
│            Socket Bridge 모듈            │
│  • TCP Socket 관리 (포트 8888)            │
│  • ESP32 연결 상태 모니터링                │
│  • 메시지 프로토콜 처리                    │
│  • 실시간 데이터 스트리밍                  │
│  • 명령 전송 및 응답 처리                  │
│  • 연결 품질 관리                         │
└─────────────────────────────────────────┘
```

### 3. 웹 프론트엔드
```
┌─────────────────────────────────────────┐
│           Web Frontend                  │
├─────────────────────────────────────────┤
│  • HTML5 + CSS3 + JavaScript            │
│  • WebSocket 클라이언트                   │
│  • 실시간 UI 업데이트                     │
│  • 사용자 인터랙션 처리                    │
├─────────────────────────────────────────┤
│              UI 컴포넌트                  │
│  • 채팅 인터페이스                        │
│  • 자연어 명령 입력                       │
│  • 로봇 상태 모니터                       │
│  • 수동 제어 패널                         │
│  • 센서 데이터 시각화                      │
│  • 매핑 뷰어                             │
└─────────────────────────────────────────┘
```

## 🔄 데이터 흐름

### 1. 자연어 명령 흐름
```
사용자 자연어 입력 → 웹 프론트엔드 → FastAPI (자연어 처리) → 명령 변환 → Socket Bridge 모듈 → TCP Socket → ESP32 → 하드웨어 제어
```

### 2. 센서 데이터 흐름
```
하드웨어 센서 → ESP32 → TCP Socket → Socket Bridge 모듈 → FastAPI → WebSocket → 웹 프론트엔드 → UI 표시
```

### 3. 안전 시스템 흐름
```
센서 감지 → ESP32 (즉시 처리) → TCP Socket → Socket Bridge 모듈 → FastAPI (상태 보고) → 웹 (알림 표시)
```

### 4. 대화 처리 흐름
```
사용자 메시지 → 웹 채팅 → FastAPI (자연어 파싱) → 로봇 응답 생성 → 웹 채팅 표시
```

## 🛡️ 안전 시스템 아키텍처

### 다층 안전 구조
```
1. 하드웨어 레벨 (ESP32)
   ├── 즉시 정지 (낙하 감지)
   ├── 모터 브레이크
   └── 비상 모드 진입

2. 소프트웨어 레벨 (FastAPI)
   ├── 센서 데이터 검증
   ├── 명령 안전성 검사
   └── 로봇 상태 모니터링

3. 사용자 레벨 (웹 인터페이스)
   ├── 수동 비상 정지 버튼
   ├── 위험 상태 알림
   └── 로봇 상태 실시간 표시
```

## 🤖 자연어 처리 아키텍처

### 규칙 기반 명령 파싱 시스템
```
┌─────────────────────────────────────────┐
│         자연어 입력 처리                  │
├─────────────────────────────────────────┤
│  • 텍스트 전처리 (소문자 변환, 공백 제거)  │
│  • 키워드 매칭                          │
│  • 의도 분류                           │
│  • 명령 검증                           │
├─────────────────────────────────────────┤
│         지원 명령어 패턴                  │
│  • move_forward: ["앞으로", "전진", ...] │
│  • turn_left: ["왼쪽", "좌회전", ...]    │
│  • turn_right: ["오른쪽", "우회전", ...] │
│  • stop: ["정지", "멈춰", ...]          │
│  • spin: ["빙글빙글", "돌아", ...]      │
└─────────────────────────────────────────┘
```

### 명령 처리 파이프라인
```
1. 자연어 입력 수신
   ↓
2. 텍스트 정규화 (소문자, 공백 처리)
   ↓
3. 패턴 매칭 (키워드 검색)
   ↓
4. 의도 분류 (가장 높은 신뢰도 선택)
   ↓
5. 명령 변환 (JSON 형식)
   ↓
6. 로봇 제어 명령 전송
```

### 응답 생성 시스템
```
┌─────────────────────────────────────────┐
│           응답 생성 모듈                  │
├─────────────────────────────────────────┤
│  • 성공 응답: "앞으로 이동합니다!"        │
│  • 실패 응답: "이해하지 못했습니다"        │
│  • 안전 알림: "낙하 감지! 정지합니다!"     │
│  • 상태 보고: "현재 위치: (10, 20)"       │
└─────────────────────────────────────────┘
```

## 🗄️ 데이터베이스 아키텍처

### SQLite 기반 사용자 경험 향상 시스템
```
┌─────────────────────────────────────────┐
│            SQLite Database              │
├─────────────────────────────────────────┤
│  • user_interactions                    │
│  • command_frequency                    │
│  • error_patterns                       │
│  • emotion_responses                    │
├─────────────────────────────────────────┤
│           데이터 처리 모듈                │
│  • 사용자 패턴 분석                      │
│  • 명령어 학습 시스템                     │
│  • 스마트 제안 엔진                      │
│  • 에러 패턴 분석                        │
└─────────────────────────────────────────┘
```

### 데이터 흐름 (사용자 경험 향상)
```
사용자 명령 → 자연어 처리 → SQLite 저장 → 패턴 분석 → 개인화된 제안
     ↓              ↓           ↓           ↓
명령 실행 → 결과 저장 → 빈도 업데이트 → 학습 데이터 → 향후 개선
```

### 데이터베이스 모듈 구조
```
┌─────────────────────────────────────────┐
│         Database Manager                │
├─────────────────────────────────────────┤
│  • Connection Pool                      │
│  • Query Builder                        │
│  • Data Validation                      │
├─────────────────────────────────────────┤
│         Analytics Engine                │
│  • Pattern Recognition                  │
│  • Frequency Analysis                   │
│  • Error Pattern Detection              │
│  • User Preference Learning             │
├─────────────────────────────────────────┤
│         Recommendation System           │
│  • Smart Suggestions                    │
│  • Personalized Commands                │
│  • Context-Aware Responses              │
└─────────────────────────────────────────┘
```

## 💬 채팅 상호작용 모듈 구조

### 채팅 시스템 아키텍처
```
┌─────────────────────────────────────────┐
│         Chat Interaction Module         │
├─────────────────────────────────────────┤
│  • Message Processing                   │
│  • Context Management                   │
│  • Emotion State Tracking               │
│  • Conversation History                 │
├─────────────────────────────────────────┤
│         Natural Language Processing     │
│  • Intent Recognition                   │
│  • Emotion Analysis                     │
│  • Context Understanding                │
│  • Response Generation                  │
├─────────────────────────────────────────┤
│         Conversation Manager            │
│  • Session Management                   │
│  • User Profile Tracking                │
│  • Conversation Flow Control            │
│  • Learning from Interactions           │
├─────────────────────────────────────────┤
│         Response Engine                 │
│  • Template-based Responses             │
│  • Dynamic Response Generation          │
│  • Personality Adaptation               │
│  • Multi-turn Conversation Support      │
└─────────────────────────────────────────┘
```

### 채팅 데이터베이스 스키마
```
┌─────────────────────────────────────────┐
│            Chat Database                │
├─────────────────────────────────────────┤
│  • chat_conversations                   │
│    - conversation_id                    │
│    - user_id                           │
│    - session_id                        │
│    - start_time                        │
│    - end_time                          │
│    - conversation_type                 │
├─────────────────────────────────────────┤
│  • chat_messages                       │
│    - message_id                        │
│    - conversation_id                   │
│    - user_message                      │
│    - robot_response                    │
│    - emotion_detected                  │
│    - emotion_responded                 │
│    - timestamp                         │
├─────────────────────────────────────────┤
│  • user_profiles                       │
│    - user_id                           │
│    - user_name                         │
│    - preferred_style                   │
│    - conversation_history_count        │
│    - last_interaction                  │
├─────────────────────────────────────────┤
│  • chat_contexts                       │
│    - context_id                        │
│    - user_id                           │
│    - session_id                        │
│    - current_topic                     │
│    - robot_mood                        │
│    - remembered_info                   │
└─────────────────────────────────────────┘
```

### 채팅 데이터 흐름
```
사용자 메시지 → 의도 분석 → 감정 분석 → 컨텍스트 조회 → 응답 생성 → 데이터베이스 저장
     ↓              ↓           ↓           ↓            ↓           ↓
로그 저장 → 패턴 학습 → 개인화 → 대화 기록 → 감정 상태 업데이트 → 다음 대화 준비
```

### 채팅 시나리오 처리 흐름
```
┌─────────────────────────────────────────┐
│         Scenario Handler                │
├─────────────────────────────────────────┤
│  1. 메시지 분류                         │
│     • 인사말 (greeting)                 │
│     • 자기소개 (introduction)           │
│     • 질문 (question)                   │
│     • 명령 (command)                    │
│     • 작별인사 (farewell)               │
├─────────────────────────────────────────┤
│  2. 컨텍스트 기반 응답                  │
│     • 사용자 이름 기억                  │
│     • 이전 대화 내용 참조               │
│     • 감정 상태 반영                    │
│     • 개인화된 스타일 적용              │
├─────────────────────────────────────────┤
│  3. 학습 및 개선                        │
│     • 사용자 피드백 수집                │
│     • 대화 패턴 분석                    │
│     • 응답 품질 개선                    │
│     • 개인화 레벨 향상                  │
└─────────────────────────────────────────┘
```

## 📊 성능 요구사항

### 실시간성
- **센서 데이터 수집**: 50Hz (20ms 간격)
- **명령 응답 시간**: < 100ms
- **안전 시스템 응답**: < 10ms
- **자연어 처리**: < 50ms

### 네트워크
- **Wi-Fi 연결**: 2.4GHz
- **데이터 전송량**: ~1KB/s
- **연결 안정성**: 자동 재연결 지원

## 🧠 TinyML 아키텍처 (7순위 계획)

### 전체 TinyML 시스템 구조
```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                              TinyML 시스템 아키텍처                                     │
└──────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐      ┌──────────────────────────┐      ┌──────────────────┐
│   데이터 수집 및 학습      │      │    모델 배포 파이프라인    │      │   온디바이스 추론  │
│      (PC/Server)        │      │        (PC)              │      │     (ESP32)      │
├─────────────────────────┤      ├──────────────────────────┤      ├──────────────────┤
│                         │      │                          │      │                  │
│ 1. 센서 데이터 수집       │─────►│ 4. 모델 최적화           │─────►│ 6. 모델 로딩     │
│    • ESP32 → Server     │      │    • Quantization        │      │    • 플래시 읽기  │
│    • SQLite 저장        │      │    • Pruning             │      │                  │
│                         │      │                          │      │ 7. 추론 실행     │
│ 2. 데이터 전처리         │      │ 5. TFLite 변환           │      │    • 센서 입력   │
│    • 정규화             │      │    • .h5 → .tflite       │      │    • 추론 결과   │
│    • 라벨링             │      │    • 모델 검증           │      │                  │
│                         │      │    • .cc 파일 생성       │      │ 8. 성능 모니터링 │
│ 3. 모델 학습            │      │                          │      │    • 지연시간    │
│    • TensorFlow/Keras   │      │                          │      │    • 메모리      │
│    • 모델 평가          │      │                          │      │    • 정확도      │
│                         │      │                          │      │                  │
└─────────────────────────┘      └──────────────────────────┘      └──────────────────┘
         │                                  │                              │
         │                                  │                              │
         ▼                                  ▼                              ▼
┌─────────────────────────┐      ┌──────────────────────────┐      ┌──────────────────┐
│   데이터베이스           │      │   모델 저장소             │      │   피드백 수집     │
│   • 센서 로그           │      │   • .tflite 파일          │      │   • 오답 케이스   │
│   • 추론 결과           │      │   • 모델 메타데이터       │      │   • 재학습 데이터 │
└─────────────────────────┘      └──────────────────────────┘      └──────────────────┘
```

### 1단계: 센서 데이터 수집 아키텍처

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        센서 데이터 수집 시스템                                     │
└─────────────────────────────────────────────────────────────────────────────────┘

ESP32 센서          →      Socket Bridge      →       FastAPI          →     SQLite
┌──────────────┐          ┌──────────────┐          ┌──────────────┐        ┌──────────┐
│ 센서 읽기     │          │ TCP 수신      │          │ 데이터 검증   │        │ 센서 로그 │
│ • IR 센서    │  JSON    │ • 포트 8888   │   REST   │ • 타입 체크  │   SQL  │ 테이블    │
│ • 엔코더     │ ────────►│ • 메시지 큐   │─────────►│ • 범위 검증  │───────►│          │
│ • 배터리     │  {data}  │              │          │              │        │ • 타임스탬프 │
│              │          │ 프로토콜 파싱 │          │ 라벨링       │        │ • 센서값   │
│ 50Hz 샘플링  │          │ • Type: data │          │ • 상황 분류  │        │ • 라벨     │
└──────────────┘          └──────────────┘          └──────────────┘        └──────────┘
```

#### 센서 데이터 수집 프로토콜
```python
# ESP32 → Server 센서 데이터 전송
{
    "type": "sensor_data",
    "timestamp": 1696780800000,
    "data": {
        "ir_front": 512,          # 적외선 센서 (0~1023)
        "ir_edge": 800,           # 낙하 감지 센서
        "encoder_left": 120,      # 왼쪽 엔코더 속도 (RPM)
        "encoder_right": 118,     # 오른쪽 엔코더 속도
        "battery_voltage": 7.4,   # 배터리 전압
        "current_direction": 0,   # 이동 방향 (0:전진, 1:좌회전, 2:우회전, 3:정지)
        "surface_friction": 0.8   # 표면 마찰 추정치
    },
    "label": "normal"             # 라벨 (normal, fall_risk, obstacle, low_battery)
}

# Server → SQLite 저장
CREATE TABLE ml_sensor_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    ir_front REAL,
    ir_edge REAL,
    encoder_left REAL,
    encoder_right REAL,
    battery_voltage REAL,
    current_direction INTEGER,
    surface_friction REAL,
    label TEXT,
    fall_occurred BOOLEAN DEFAULT 0,
    session_id TEXT
);
```

### 2단계: 모델 학습 파이프라인

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        모델 학습 파이프라인 (PC)                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

1. 데이터 로드              2. 전처리                3. 모델 학습
┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│ SQLite 쿼리  │          │ 정규화       │          │ TensorFlow   │
│ SELECT *     │─────────►│ • Min-Max    │─────────►│ • Keras API  │
│ FROM logs    │          │ • Z-Score    │          │ • 모델 정의  │
│              │          │              │          │ • Compile    │
│ Pandas       │          │ 데이터 분할  │          │ • Fit        │
│ DataFrame    │          │ • Train 80%  │          │              │
└──────────────┘          │ • Val 10%    │          └──────────────┘
                          │ • Test 10%   │                 │
                          └──────────────┘                 │
                                                          │
4. 모델 평가              ◄──────────────────────────────┘
┌──────────────┐
│ 정확도 측정  │
│ • Accuracy   │
│ • Precision  │
│ • Recall     │
│ • F1-Score   │
└──────────────┘
       │
       ▼
5. 모델 저장
┌──────────────┐
│ .h5 파일     │
│ • 가중치     │
│ • 구조       │
└──────────────┘
```

#### 학습 코드 예시
```python
# backend/ml/train_fall_detection.py

import tensorflow as tf
from tensorflow import keras
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 1. 데이터 로드
def load_training_data():
    """SQLite에서 학습 데이터 로드"""
    import sqlite3
    conn = sqlite3.connect('deks.db')
    df = pd.read_sql_query("""
        SELECT ir_front, ir_edge, encoder_left, encoder_right,
               current_direction, surface_friction, fall_occurred
        FROM ml_sensor_logs
        WHERE label IS NOT NULL
    """, conn)
    conn.close()
    return df

# 2. 데이터 전처리
def preprocess_data(df):
    """데이터 정규화 및 분할"""
    X = df[['ir_front', 'ir_edge', 'encoder_left', 'encoder_right', 
            'current_direction']].values
    y = df['fall_occurred'].values
    
    # 정규화
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 분할
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    
    return X_train, X_test, y_train, y_test, scaler

# 3. 모델 정의
def create_model(input_shape):
    """경량 낙하 예측 모델"""
    model = keras.Sequential([
        keras.layers.Input(shape=(input_shape,)),
        keras.layers.Dense(16, activation='relu'),
        keras.layers.Dense(8, activation='relu'),
        keras.layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy', 'precision', 'recall']
    )
    
    return model

# 4. 학습 실행
def train_model():
    df = load_training_data()
    X_train, X_test, y_train, y_test, scaler = preprocess_data(df)
    
    model = create_model(input_shape=5)
    
    # 학습
    history = model.fit(
        X_train, y_train,
        validation_split=0.1,
        epochs=50,
        batch_size=32,
        verbose=1
    )
    
    # 평가
    loss, acc, prec, rec = model.evaluate(X_test, y_test)
    print(f"정확도: {acc:.4f}, 정밀도: {prec:.4f}, 재현율: {rec:.4f}")
    
    # 저장
    model.save('models/fall_detection.h5')
    
    return model, scaler
```

### 3단계: 모델 최적화 및 변환

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        모델 최적화 파이프라인                                      │
└─────────────────────────────────────────────────────────────────────────────────┘

.h5 모델           →      양자화(Quantization)    →      TFLite 변환
┌──────────────┐          ┌──────────────────┐          ┌──────────────┐
│ 원본 모델     │          │ INT8 양자화       │          │ .tflite 파일 │
│ • FP32 가중치 │          │ • 8-bit 정수      │          │ • 크기 1/4   │
│ • 크기: 200KB │─────────►│ • Representative  │─────────►│ • 50KB       │
│              │          │   Dataset 사용    │          │              │
└──────────────┘          │ • 정확도 손실 <1% │          └──────────────┘
                          └──────────────────┘                 │
                                                              │
                          ┌──────────────────┐                │
                          │ C++ 배열 변환    │◄───────────────┘
                          │ • xxd 도구 사용  │
                          │ • .cc 파일 생성  │
                          └──────────────────┘
```

#### 모델 변환 코드
```python
# backend/ml/convert_to_tflite.py

import tensorflow as tf
import numpy as np

def convert_to_tflite(model_path, output_path):
    """모델을 TFLite로 변환 및 양자화"""
    
    # 1. 모델 로드
    model = tf.keras.models.load_model(model_path)
    
    # 2. Representative Dataset (양자화용 샘플 데이터)
    def representative_dataset_gen():
        """양자화를 위한 대표 데이터셋"""
        import sqlite3
        conn = sqlite3.connect('deks.db')
        cursor = conn.execute("""
            SELECT ir_front, ir_edge, encoder_left, encoder_right, current_direction
            FROM ml_sensor_logs LIMIT 100
        """)
        
        for row in cursor:
            data = np.array(row, dtype=np.float32).reshape(1, -1)
            yield [data]
        
        conn.close()
    
    # 3. TFLite 변환기 설정
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    
    # INT8 양자화 활성화
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = representative_dataset_gen
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8
    
    # 4. 변환 실행
    tflite_model = converter.convert()
    
    # 5. .tflite 파일 저장
    with open(output_path, 'wb') as f:
        f.write(tflite_model)
    
    # 6. 모델 크기 출력
    import os
    size_kb = os.path.getsize(output_path) / 1024
    print(f"변환 완료: {output_path} ({size_kb:.2f} KB)")
    
    return tflite_model

def convert_to_c_array(tflite_path, output_cc_path):
    """TFLite 모델을 C++ 배열로 변환"""
    import subprocess
    
    # xxd 명령어로 .tflite → .cc 변환
    # xxd -i model.tflite > model_data.cc
    with open(tflite_path, 'rb') as f:
        tflite_data = f.read()
    
    # C++ 헤더 생성
    with open(output_cc_path, 'w') as f:
        f.write('// Auto-generated model data\n')
        f.write('#include <cstdint>\n\n')
        f.write('alignas(16) const unsigned char fall_detection_model[] = {\n')
        
        # 16진수 배열로 변환
        for i, byte in enumerate(tflite_data):
            if i % 12 == 0:
                f.write('  ')
            f.write(f'0x{byte:02x}, ')
            if (i + 1) % 12 == 0:
                f.write('\n')
        
        f.write('\n};\n')
        f.write(f'const int fall_detection_model_len = {len(tflite_data)};\n')
    
    print(f"C++ 배열 생성 완료: {output_cc_path}")

# 실행
if __name__ == "__main__":
    convert_to_tflite('models/fall_detection.h5', 'models/fall_detection.tflite')
    convert_to_c_array('models/fall_detection.tflite', 'firmware/model_data.cc')
```

### 4단계: ESP32 플래시 메모리 업로드

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     ESP32 플래시 메모리 모델 배포                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

개발 PC                     USB 연결              ESP32 S3 플래시 메모리
┌──────────────┐          ┌──────────────┐          ┌──────────────────┐
│ .tflite 파일 │          │ esptool.py   │          │ 플래시 레이아웃   │
│ • 50KB       │          │ • 직렬 통신  │          │                  │
│              │  Upload  │ • 플래시 쓰기│   Write  │ 0x000000: 부트로더│
│ model_data.  │─────────►│              │─────────►│ 0x010000: 펌웨어  │
│   cc         │          │ mpremote     │          │ 0x3C0000: 모델    │
│              │          │ • 파일 전송  │          │   (50KB)         │
└──────────────┘          └──────────────┘          └──────────────────┘
                                                            │
                          ┌──────────────┐                 │
                          │ 파일시스템    │◄────────────────┘
                          │ /models/     │
                          │   fall.tflite│
                          └──────────────┘
```

#### ESP32 모델 업로드 방법

**방법 1: mpremote 사용 (권장)**
```bash
# 1. .tflite 파일을 ESP32 파일시스템에 복사
mpremote fs cp models/fall_detection.tflite :/models/fall_detection.tflite

# 2. 업로드 확인
mpremote fs ls /models/

# 3. 파일 크기 확인
mpremote exec "import os; print(os.stat('/models/fall_detection.tflite'))"
```

**방법 2: MicroPython 코드로 직접 포함**
```python
# firmware/ml_model.py
# C++ 배열을 Python bytes로 변환하여 포함

MODEL_DATA = bytes([
    0x1c, 0x00, 0x00, 0x00, 0x54, 0x46, 0x4c, 0x33,  # TFLite 헤더
    # ... (모델 데이터 계속)
])

def get_model():
    """모델 데이터 반환"""
    return MODEL_DATA
```

**방법 3: OTA (Over-the-Air) 업데이트**
```python
# firmware/ota_update.py
import urequests
import os

def download_model(model_url, local_path):
    """서버에서 모델 다운로드"""
    print("모델 다운로드 시작...")
    
    response = urequests.get(model_url)
    if response.status_code == 200:
        with open(local_path, 'wb') as f:
            f.write(response.content)
        print(f"모델 저장 완료: {local_path}")
        return True
    else:
        print(f"다운로드 실패: {response.status_code}")
        return False

# 사용 예시
# download_model('http://192.168.1.100:8000/models/fall_detection.tflite', 
#                '/models/fall_detection.tflite')
```

### 5단계: TFLite Micro 추론 실행

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     ESP32 TFLite Micro 추론 아키텍처                              │
└─────────────────────────────────────────────────────────────────────────────────┘

센서 입력          →      전처리              →      추론 엔진           →      결과
┌──────────────┐          ┌──────────────┐          ┌──────────────┐          ┌────────┐
│ 센서 읽기     │          │ 정규화       │          │ TFLite Micro │          │ 위험도 │
│ IR: 512      │   Raw    │ • Min-Max    │  Tensor  │ • 모델 로드  │  Output  │ 0.85   │
│ Enc_L: 120   │─────────►│ • 배열 변환  │─────────►│ • Invoke     │─────────►│        │
│ Enc_R: 118   │          │              │          │ • 추론 실행  │          │ 행동   │
│ Dir: 0       │          │ 입력 버퍼    │          │              │          │ STOP   │
└──────────────┘          │ float32[5]   │          └──────────────┘          └────────┘
                          └──────────────┘                 │
                                                          │
                          ┌──────────────────────────────┘
                          │
                          ▼
                ┌──────────────────┐
                │ 메모리 관리       │
                │ • 입력 텐서       │
                │ • 출력 텐서       │
                │ • Arena (20KB)   │
                └──────────────────┘
```

#### ESP32 추론 코드 (MicroPython)

**C 모듈 방식 (TFLite Micro C++)**
```cpp
// firmware/tflite_inference.cpp

#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "model_data.h"  // 모델 데이터

namespace {
    tflite::ErrorReporter* error_reporter = nullptr;
    const tflite::Model* model = nullptr;
    tflite::MicroInterpreter* interpreter = nullptr;
    TfLiteTensor* input = nullptr;
    TfLiteTensor* output = nullptr;
    
    // 20KB Arena (작업 메모리)
    constexpr int kTensorArenaSize = 20 * 1024;
    uint8_t tensor_arena[kTensorArenaSize];
}

// 초기화
void setup_tflite() {
    // 에러 리포터 설정
    static tflite::MicroErrorReporter micro_error_reporter;
    error_reporter = &micro_error_reporter;
    
    // 모델 로드
    model = tflite::GetModel(fall_detection_model);
    if (model->version() != TFLITE_SCHEMA_VERSION) {
        error_reporter->Report("모델 버전 불일치!");
        return;
    }
    
    // Ops Resolver (연산자 등록)
    static tflite::AllOpsResolver resolver;
    
    // 인터프리터 생성
    static tflite::MicroInterpreter static_interpreter(
        model, resolver, tensor_arena, kTensorArenaSize, error_reporter
    );
    interpreter = &static_interpreter;
    
    // 텐서 할당
    TfLiteStatus allocate_status = interpreter->AllocateTensors();
    if (allocate_status != kTfLiteOk) {
        error_reporter->Report("텐서 할당 실패!");
        return;
    }
    
    // 입력/출력 텐서 획득
    input = interpreter->input(0);
    output = interpreter->output(0);
    
    Serial.println("TFLite Micro 초기화 완료");
}

// 추론 실행
float predict_fall_risk(float ir_front, float ir_edge, 
                       float encoder_left, float encoder_right, 
                       int direction) {
    // 입력 데이터 정규화 및 설정
    input->data.f[0] = (ir_front - 512.0) / 512.0;        // 정규화
    input->data.f[1] = (ir_edge - 512.0) / 512.0;
    input->data.f[2] = (encoder_left - 100.0) / 50.0;
    input->data.f[3] = (encoder_right - 100.0) / 50.0;
    input->data.f[4] = (float)direction / 3.0;
    
    // 추론 실행
    TfLiteStatus invoke_status = interpreter->Invoke();
    if (invoke_status != kTfLiteOk) {
        error_reporter->Report("추론 실패!");
        return -1.0;
    }
    
    // 결과 반환 (낙하 위험도 0.0 ~ 1.0)
    float fall_risk = output->data.f[0];
    return fall_risk;
}
```

**MicroPython 래퍼 (실험적)**
```python
# firmware/ml_inference.py
import machine
import time

class FallDetectionModel:
    """낙하 위험 예측 모델"""
    
    def __init__(self, model_path='/models/fall_detection.tflite'):
        self.model_path = model_path
        self.model = None
        self.interpreter = None
        self.load_model()
    
    def load_model(self):
        """모델 로드 (C 모듈 사용)"""
        try:
            import tflite_runtime.interpreter as tflite
            self.interpreter = tflite.Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            
            # 입력/출력 정보
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            print("모델 로드 완료")
            print(f"입력 shape: {self.input_details[0]['shape']}")
            print(f"출력 shape: {self.output_details[0]['shape']}")
            
        except Exception as e:
            print(f"모델 로드 실패: {e}")
    
    def normalize_input(self, ir_front, ir_edge, encoder_left, encoder_right, direction):
        """입력 데이터 정규화"""
        import array
        
        # Min-Max 정규화 (학습 시와 동일한 방식)
        normalized = array.array('f', [
            (ir_front - 512.0) / 512.0,
            (ir_edge - 512.0) / 512.0,
            (encoder_left - 100.0) / 50.0,
            (encoder_right - 100.0) / 50.0,
            float(direction) / 3.0
        ])
        
        return normalized
    
    def predict(self, ir_front, ir_edge, encoder_left, encoder_right, direction):
        """낙하 위험도 예측"""
        start_time = time.ticks_ms()
        
        # 입력 정규화
        input_data = self.normalize_input(ir_front, ir_edge, encoder_left, 
                                          encoder_right, direction)
        
        # 입력 텐서 설정
        self.interpreter.set_tensor(self.input_details[0]['index'], [input_data])
        
        # 추론 실행
        self.interpreter.invoke()
        
        # 결과 획득
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        fall_risk = float(output_data[0][0])
        
        # 추론 시간 측정
        inference_time = time.ticks_diff(time.ticks_ms(), start_time)
        
        print(f"추론 완료: 위험도={fall_risk:.3f}, 시간={inference_time}ms")
        
        return fall_risk, inference_time
    
    def get_recommended_action(self, fall_risk):
        """위험도에 따른 권장 행동"""
        if fall_risk > 0.8:
            return "EMERGENCY_STOP"  # 즉시 정지
        elif fall_risk > 0.6:
            return "SLOW_DOWN"       # 감속
        elif fall_risk > 0.4:
            return "CAUTION"         # 주의
        else:
            return "CONTINUE"        # 계속 진행
```

#### 실시간 추론 통합
```python
# firmware/main.py (TinyML 통합)

from ml_inference import FallDetectionModel
from hardware_interface import HardwareInterface
import time

class SmartRobot:
    """TinyML 기반 스마트 로봇"""
    
    def __init__(self):
        self.hw = HardwareInterface()
        self.ml_model = FallDetectionModel()
        self.inference_interval = 100  # 100ms마다 추론
        self.last_inference_time = 0
    
    async def run_with_ml(self):
        """ML 기반 안전 시스템"""
        while True:
            current_time = time.ticks_ms()
            
            # 센서 읽기
            sensors = self.hw.read_all_sensors()
            
            # 주기적 추론
            if time.ticks_diff(current_time, self.last_inference_time) > self.inference_interval:
                # 낙하 위험도 예측
                fall_risk, inference_time = self.ml_model.predict(
                    sensors['ir_front'],
                    sensors['ir_edge'],
                    sensors['encoder_left'],
                    sensors['encoder_right'],
                    self.hw.current_direction
                )
                
                # 권장 행동
                action = self.ml_model.get_recommended_action(fall_risk)
                
                # 자동 안전 제어
                if action == "EMERGENCY_STOP":
                    print("ML 위험 감지: 긴급 정지!")
                    self.hw.emergency_stop()
                elif action == "SLOW_DOWN":
                    print("ML 주의: 속도 감소")
                    self.hw.set_speed(50)  # 50% 속도
                
                # 서버에 추론 결과 전송
                await self.send_ml_result(fall_risk, action, inference_time)
                
                self.last_inference_time = current_time
            
            await asyncio.sleep(0.01)  # 10ms
```

### 6단계: 성능 모니터링 및 재학습

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     성능 모니터링 및 재학습 파이프라인                              │
└─────────────────────────────────────────────────────────────────────────────────┘

ESP32 추론 결과    →     FastAPI 수집     →     성능 분석      →    재학습 트리거
┌──────────────┐         ┌─────────────┐        ┌──────────┐       ┌───────────┐
│ 추론 결과    │   TCP   │ 로그 저장   │  분석  │ 정확도   │ if    │ 재학습    │
│ • 예측값     │────────►│ • 예측값    │───────►│ • 오답률 │ 저하  │ • 데이터  │
│ • 실제값     │         │ • 실제값    │        │ • 지연   │──────►│ • 모델    │
│ • 지연시간   │         │ • 지연시간  │        │          │       │ • 배포    │
│ • 메모리     │         └─────────────┘        └──────────┘       └───────────┘
└──────────────┘                │                     │
                                │                     │
                                ▼                     ▼
                        ┌─────────────┐        ┌──────────┐
                        │ ML 성능 DB  │        │ 대시보드 │
                        │ • 추론 로그 │        │ • 차트   │
                        └─────────────┘        └──────────┘
```

#### 성능 모니터링 프로토콜
```python
# ESP32 → Server 추론 결과 전송
{
    "type": "ml_inference",
    "timestamp": 1696780800000,
    "model_name": "fall_detection",
    "model_version": "v1.0",
    "input": {
        "ir_front": 512,
        "ir_edge": 800,
        "encoder_left": 120,
        "encoder_right": 118,
        "direction": 0
    },
    "prediction": {
        "fall_risk": 0.85,
        "recommended_action": "EMERGENCY_STOP"
    },
    "performance": {
        "inference_time_ms": 8,
        "memory_used_kb": 25,
        "cpu_usage_percent": 15
    },
    "actual_result": {
        "fall_occurred": true,  # 실제 낙하 발생 여부
        "correct_prediction": true
    }
}

# Server DB 저장
CREATE TABLE ml_inference_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    model_name TEXT,
    model_version TEXT,
    input_data TEXT,              -- JSON
    predicted_risk REAL,
    recommended_action TEXT,
    actual_fall BOOLEAN,
    correct_prediction BOOLEAN,
    inference_time_ms REAL,
    memory_used_kb REAL,
    cpu_usage_percent REAL
);
```

#### 성능 분석 및 재학습 트리거
```python
# backend/ml/performance_monitor.py

import sqlite3
import pandas as pd
from datetime import datetime, timedelta

class MLPerformanceMonitor:
    """ML 모델 성능 모니터링"""
    
    def __init__(self, db_path='deks.db'):
        self.db_path = db_path
    
    def calculate_accuracy(self, days=7):
        """최근 N일간 정확도 계산"""
        conn = sqlite3.connect(self.db_path)
        
        query = f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN correct_prediction = 1 THEN 1 ELSE 0 END) as correct
            FROM ml_inference_logs
            WHERE timestamp >= datetime('now', '-{days} days')
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df['total'][0] > 0:
            accuracy = df['correct'][0] / df['total'][0]
            return accuracy
        return 1.0
    
    def calculate_avg_latency(self, days=7):
        """평균 추론 지연시간"""
        conn = sqlite3.connect(self.db_path)
        
        query = f"""
            SELECT AVG(inference_time_ms) as avg_latency
            FROM ml_inference_logs
            WHERE timestamp >= datetime('now', '-{days} days')
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df['avg_latency'][0] or 0.0
    
    def get_false_positives(self, days=7, limit=100):
        """오탐 케이스 수집 (재학습 데이터)"""
        conn = sqlite3.connect(self.db_path)
        
        query = f"""
            SELECT input_data, predicted_risk, actual_fall
            FROM ml_inference_logs
            WHERE correct_prediction = 0
              AND timestamp >= datetime('now', '-{days} days')
            LIMIT {limit}
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def should_retrain(self):
        """재학습 필요 여부 판단"""
        accuracy = self.calculate_accuracy(days=7)
        latency = self.calculate_avg_latency(days=7)
        
        # 재학습 조건
        if accuracy < 0.90:  # 정확도 90% 미만
            print(f"재학습 필요: 정확도 저하 ({accuracy:.2%})")
            return True, "low_accuracy"
        
        if latency > 50:  # 지연 50ms 초과
            print(f"재학습 필요: 지연시간 증가 ({latency:.2f}ms)")
            return True, "high_latency"
        
        return False, None
    
    def trigger_retraining(self):
        """재학습 파이프라인 실행"""
        print("재학습 시작...")
        
        # 1. 오답 케이스 수집
        false_cases = self.get_false_positives(days=30, limit=500)
        print(f"오답 케이스: {len(false_cases)}개")
        
        # 2. 기존 데이터와 병합
        # 3. 모델 재학습
        from backend.ml.train_fall_detection import train_model
        model, scaler = train_model()
        
        # 4. 모델 변환
        from backend.ml.convert_to_tflite import convert_to_tflite
        convert_to_tflite('models/fall_detection.h5', 
                         'models/fall_detection_v2.tflite')
        
        # 5. ESP32에 OTA 업데이트
        print("새 모델을 ESP32에 배포하세요")
        
        return True

# 주기적 모니터링 (FastAPI 백그라운드 태스크)
async def periodic_performance_check():
    """주기적 성능 점검"""
    monitor = MLPerformanceMonitor()
    
    while True:
        should_retrain, reason = monitor.should_retrain()
        
        if should_retrain:
            print(f"재학습 트리거: {reason}")
            monitor.trigger_retraining()
        
        # 24시간마다 점검
        await asyncio.sleep(24 * 3600)
```

#### 대시보드 시각화
```python
# backend/api/v1/endpoints/ml_dashboard.py

from fastapi import APIRouter
from typing import List, Dict
import sqlite3

router = APIRouter()

@router.get("/ml/performance")
async def get_ml_performance():
    """ML 모델 성능 대시보드"""
    monitor = MLPerformanceMonitor()
    
    return {
        "accuracy_7days": monitor.calculate_accuracy(days=7),
        "accuracy_30days": monitor.calculate_accuracy(days=30),
        "avg_latency_ms": monitor.calculate_avg_latency(days=7),
        "total_inferences": get_total_inferences(),
        "model_version": "v1.0",
        "last_retrain": get_last_retrain_date()
    }

@router.get("/ml/inference_history")
async def get_inference_history(limit: int = 100):
    """최근 추론 결과 이력"""
    conn = sqlite3.connect('deks.db')
    
    query = f"""
        SELECT timestamp, predicted_risk, actual_fall, 
               correct_prediction, inference_time_ms
        FROM ml_inference_logs
        ORDER BY timestamp DESC
        LIMIT {limit}
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df.to_dict(orient='records')
```

## 🔄 확장성 고려사항

### 현재 구현된 기능 (2025-10-08 기준)
1. ✅ **ESP32 하드웨어 연동**: 완전한 소프트웨어 통합 완료
2. ✅ **실시간 통신**: Socket Bridge + WebSocket 양방향 통신
3. ✅ **자연어 처리**: 규칙 기반 NLP 시스템
4. ✅ **에러 처리**: 40+ 커스텀 예외, 전역 에러 핸들러
5. ✅ **대화 시스템**: 장기 기억 + 16개 감정 상태
6. ✅ **Analytics**: 사용자 패턴 분석 및 스마트 제안
7. ✅ **Expression**: LED/버저 제어 및 자동 표현

### 향후 확장 계획 (우선순위 7~10)
1. **TinyML 도입** (7순위, 2025 Q4)
   - 온디바이스 ML 모델 추론
   - 음성 명령 인식 (I2S MEMS 마이크)
   - 낙하 위험 예측 모델
   - **상태**: 계획 단계

2. **환경 매핑 및 SLAM** (8순위)
   - 센서 융합 기반 매핑
   - 실시간 지도 작성
   - 위치 추정 및 추적
   - **상태**: 미개발

3. **경로 계획 및 자율 탐사** (9순위)
   - A*/RRT 경로 계획
   - 자율적 환경 탐색
   - **상태**: 미개발

4. **스마트 홈 연동** (10순위)
   - MQTT 프로토콜 통합
   - IoT 기기 제어
   - 홈 오토메이션
   - **상태**: 미개발

5. **멀티 로봇 지원** (향후)
   - 여러 Deks 로봇 동시 제어
   - 로봇 간 협업
   - **상태**: 미개발

6. **클라우드 연동** (향후)
   - 원격 모니터링 및 제어
   - 데이터 백업 및 동기화
   - **상태**: 미개발

### 모듈화 설계
- ✅ 각 컴포넌트는 독립적으로 교체 가능
- ✅ API 기반 통신으로 느슨한 결합
- ✅ 마이크로서비스 아키텍처 적용 가능
- 🔮 TinyML 모델 OTA 업데이트 지원 (향후)

---

**Deks 1.0 아키텍처** - 확장 가능하고 안전하며 지능적인 로봇 플랫폼
