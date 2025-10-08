# Deks 1.0 기술 스택

## 📱 ESP32 S3 (마이크로파이썬) 관련

### 필요한 라이브러리
- **machine** - GPIO, PWM, ADC 제어
- **time** - 타이밍 제어
- **network** - Wi-Fi 연결
- **socket** - TCP 클라이언트 소켓 통신
- **json** - JSON 데이터 처리
- **uasyncio** - 비동기 프로그래밍

## 🎛️ 하드웨어 제어 라이브러리

- **모터 제어**: L298N 드라이버용 PWM 제어
- **엔코더**: 인터럽트 기반 엔코더 읽기
- **1588AS LED 매트릭스**: I2C 또는 SPI 통신
- **적외선 센서**: 아날로그/디지털 입력 처리
- **패시브 버저**: PWM으로 음계 생성

## 🌐 웹 서버 (파이썬 FastAPI)

- **FastAPI** - REST API 서버
- **WebSocket** - 실시간 통신
- **uvicorn** - ASGI 서버
- **pydantic** - 데이터 검증
- **websockets** - WebSocket 클라이언트/서버

## 🔌 통신 및 브리지

- **HTTP 클라이언트** - ESP32 ↔ FastAPI Server 통신
- **Socket 클라이언트** - ESP32에서 실시간 데이터 전송
- **Socket Bridge 모듈** - FastAPI 내 ESP32 통신 모듈
- **WebSocket 서버** - FastAPI 내 실시간 통신
- **JSON 직렬화/역직렬화** - 데이터 포맷 변환

## 🧠 제어 알고리즘

- **PID 제어** - 모터 속도/위치 제어
- **센서 융합** - 엔코더 + 적외선 데이터 결합
- **상태 머신** - 로봇 동작 상태 관리
- **안전 로직** - 낙하/장애물 감지 시 동작

## 🧠 TinyML (On-Device Machine Learning) 🚧 2025 Q4 예정

### 머신러닝 프레임워크
- **TensorFlow Lite for Microcontrollers** - ESP32에서 ML 모델 추론
- **TensorFlow** 2.x - 모델 학습 및 개발 (PC)
- **Edge Impulse** (선택사항) - End-to-End TinyML 개발 플랫폼
- **TinyML 라이브러리** - 경량화 ML 알고리즘

### 모델 개발 및 학습 도구
- **Python** 3.9+ - 모델 개발 환경
- **Jupyter Notebook** - 실험 및 데이터 분석
- **TensorFlow/Keras** - 모델 설계 및 학습
- **Scikit-learn** - 데이터 전처리 및 평가
- **NumPy/Pandas** - 센서 데이터 처리
- **Matplotlib/Seaborn** - 데이터 시각화

### 모델 최적화 기술
- **Quantization (양자화)**
  - Post-training quantization (학습 후 양자화)
  - Quantization-aware training (양자화 인식 학습)
  - 8-bit integer quantization (INT8)
  - 16-bit float quantization (FP16)
  
- **Pruning (가지치기)**
  - Weight pruning - 불필요한 가중치 제거
  - Structured pruning - 구조적 가지치기
  - Magnitude-based pruning - 크기 기반 가지치기
  
- **Knowledge Distillation (지식 증류)**
  - Teacher-Student 모델
  - 큰 모델 → 작은 모델로 지식 전이
  
- **Model Compression**
  - TFLite Converter - .h5/.pb → .tflite 변환
  - Flatbuffers - 경량 직렬화 포맷

### ESP32 추론 라이브러리
- **TensorFlow Lite Micro** - C++ 기반 추론 엔진
- **MicroPython TensorFlow** - 파이썬 바인딩 (실험적)
- **ESP-NN** - ESP32 최적화 신경망 라이브러리
- **ulab** - MicroPython용 NumPy 대체

### 모델 아키텍처 (경량 모델)
- **MobileNet V1/V2** - 모바일 최적화 CNN
- **SqueezeNet** - 경량 이미지 분류
- **Tiny YOLO** - 경량 객체 탐지 (필요시)
- **1D CNN** - 센서 시계열 데이터 분석
- **LSTM/GRU (경량)** - 시퀀스 패턴 인식
- **Fully Connected Networks** - 간단한 분류/회귀

### 학습 데이터 관리
- **SQLite** - 센서 데이터 로깅 및 저장
- **CSV/JSON** - 데이터셋 저장 및 전송
- **Label Studio** (선택사항) - 데이터 라벨링 도구
- **Data Augmentation** - 데이터 증강 기법
  - 노이즈 추가
  - 시간 축 변환
  - 스케일링/정규화

### 음성 처리 (2단계 예정)
- **I2S MEMS 마이크** - 디지털 마이크 입력
- **MFCC (Mel-Frequency Cepstral Coefficients)** - 음성 특징 추출
- **Keyword Spotting** - 웨이크 워드 감지
- **TensorFlow Audio** - 오디오 ML 라이브러리

### 성능 측정 및 프로파일링
- **TensorFlow Lite Benchmark** - 추론 속도 측정
- **Memory Profiler** - 메모리 사용량 분석
- **Power Profiler** - 전력 소비 측정
- **Confusion Matrix** - 모델 정확도 평가
- **ROC/AUC** - 분류 성능 평가

### 배포 파이프라인
```python
# 모델 개발 → 최적화 → 배포 흐름
1. 데이터 수집 (SQLite/CSV)
2. 모델 학습 (TensorFlow/Keras)
3. 모델 평가 (scikit-learn)
4. 양자화 (TFLite Converter + INT8)
5. .tflite 파일 생성
6. ESP32 플래시 메모리에 업로드
7. TFLite Micro로 추론 실행
8. 성능 모니터링 및 재학습
```

### TinyML 모델 사례 (계획)

#### 1단계: 낙하 위험 예측 모델
```python
# 입력: 센서 데이터
inputs = {
    "ir_sensor_value": float,      # 적외선 센서 값 (0~1023)
    "encoder_left_speed": float,   # 왼쪽 엔코더 속도
    "encoder_right_speed": float,  # 오른쪽 엔코더 속도
    "direction": int,              # 이동 방향 (0~3)
    "surface_type": int            # 표면 타입 (0~2)
}

# 출력
output = {
    "fall_risk_score": float,      # 낙하 위험도 (0.0 ~ 1.0)
    "recommended_action": int      # 권장 행동 (0: 계속, 1: 감속, 2: 정지, 3: 후진)
}

# 모델 사양
- 아키텍처: Fully Connected (Dense)
- 레이어: Input(5) → Dense(16, ReLU) → Dense(8, ReLU) → Dense(2, Softmax)
- 파라미터: ~500개
- 모델 크기: <50KB (INT8 양자화)
- 추론 시간: <10ms
- 정확도 목표: >95%
```

#### 2단계: 음성 명령 인식 모델
```python
# 입력: MFCC 특징
inputs = {
    "mfcc_features": array[13, 40],  # 13 MFCC x 40 프레임
}

# 출력
output = {
    "command_class": int,  # 0: 앞, 1: 뒤, 2: 왼쪽, 3: 오른쪽, 4: 정지, 5: 배경
    "confidence": float    # 신뢰도 (0.0 ~ 1.0)
}

# 모델 사양
- 아키텍처: 1D CNN + LSTM
- 레이어: Conv1D(32) → MaxPool → LSTM(32) → Dense(6, Softmax)
- 파라미터: ~15,000개
- 모델 크기: <80KB (INT8 양자화)
- 추론 시간: <50ms
- 정확도 목표: >90%
```

#### 3단계: 이상 패턴 감지 모델
```python
# 입력: 시계열 센서 데이터
inputs = {
    "sensor_sequence": array[10, 6],  # 최근 10개 타임스텝 x 6개 센서
}

# 출력
output = {
    "anomaly_score": float,     # 이상 점수 (0.0 ~ 1.0)
    "anomaly_type": int,        # 이상 유형 (0: 정상, 1: 센서 오류, 2: 배터리, 3: 모터)
}

# 모델 사양
- 아키텍처: Autoencoder (LSTM-based)
- 파라미터: ~8,000개
- 모델 크기: <60KB (INT8 양자화)
- 추론 시간: <30ms
```

### ESP32 S3 하드웨어 제약사항
```python
# ESP32 S3 사양
ESP32_S3_SPECS = {
    "CPU": "Xtensa LX7 Dual-core 240MHz",
    "SRAM": "512KB",           # 모델 + 변수 저장
    "PSRAM": "2MB~8MB",        # 외부 RAM (선택사항)
    "Flash": "4MB~16MB",       # 모델 파일 저장
    "FPU": "Single-precision", # 부동소수점 연산
}

# TinyML 권장 사양
TINYML_CONSTRAINTS = {
    "model_size": "<100KB",          # 플래시 메모리 제약
    "runtime_memory": "<200KB",      # SRAM 제약
    "inference_time": "<100ms",      # 실시간성 요구
    "power_consumption": "<5% 증가", # 배터리 수명
    "accuracy": ">90%",              # 실용성
}
```

### 추가 하드웨어 요구사항
- **I2S MEMS 마이크** (음성 인식용)
  - 모델: INMP441, SPH0645
  - 인터페이스: I2S
  - 샘플링: 16kHz
  
- **외부 PSRAM** (대형 모델용, 선택사항)
  - 용량: 2MB~8MB
  - 인터페이스: SPI/Octal SPI

### 참고 자료 및 도구
- **TensorFlow Lite Micro 문서**: https://www.tensorflow.org/lite/microcontrollers
- **Edge Impulse**: https://edgeimpulse.com/
- **ESP-IDF ML 예제**: https://github.com/espressif/esp-idf/tree/master/examples/machine_learning
- **TinyML 서적**: "TinyML: Machine Learning with TensorFlow Lite"
- **MicroPython TensorFlow**: https://github.com/mocleiri/tensorflow-micropython-examples

## 🤖 자연어 처리 (규칙 기반)

- **명령 파싱** - 자연어를 로봇 제어 명령으로 변환
- **키워드 매칭** - 패턴 기반 의도 인식
- **명령 검증** - 유효한 명령인지 확인
- **응답 생성** - 사용자에게 적절한 피드백 제공

### 지원 명령어 패턴
```python
command_patterns = {
    "move_forward": ["앞으로", "전진", "가줘", "이동해", "앞으로 가"],
    "turn_left": ["왼쪽", "좌회전", "왼쪽으로", "왼쪽으로 돌아"],
    "turn_right": ["오른쪽", "우회전", "오른쪽으로", "오른쪽으로 돌아"],
    "stop": ["정지", "멈춰", "그만", "정지해"],
    "spin": ["빙글빙글", "돌아", "회전해", "빙글빙글 돌아"]
}
```

## 💬 채팅 상호작용 기술 스택

### 자연어 처리 라이브러리
- **spaCy** (선택사항) - 고급 자연어 처리
- **NLTK** (선택사항) - 자연어 처리 툴킷
- **transformers** (선택사항) - 사전 훈련된 언어 모델
- **정규표현식 (re)** - 기본 패턴 매칭
- **한국어 형태소 분석기** (선택사항) - KoNLPy, Mecab

### 채팅 시스템 구성 요소
- **메시지 처리기** - 사용자 입력 분석 및 분류
- **의도 인식 엔진** - 대화 의도 파악 (인사, 질문, 명령, 작별)
- **감정 분석 모듈** - 사용자 감정 상태 감지
- **컨텍스트 관리자** - 대화 맥락 유지 및 관리
- **응답 생성기** - 상황별 적절한 응답 생성
- **학습 시스템** - 사용자 패턴 학습 및 개선

### 대화 시나리오 패턴
```python
conversation_patterns = {
    "greeting": {
        "keywords": ["안녕", "하이", "헬로", "덱스"],
        "responses": [
            "안녕하세요! 저는 덱스에요. 당신은 누구신가요?",
            "안녕하세요! 만나서 반가워요. 저는 덱스라고 해요.",
            "안녕하세요! 저는 덱스 로봇이에요. 오늘은 어떤 도움이 필요하신가요?"
        ]
    },
    "introduction": {
        "keywords": ["나는", "내 이름은", "저는"],
        "responses": [
            "안녕하세요 {user_name}님! 만나서 반가워요. 저는 덱스라고 해요.",
            "반가워요 {user_name}님! 저는 덱스라는 로봇이에요."
        ]
    },
    "question_about_robot": {
        "keywords": ["넌 뭐야", "너는 누구", "뭐하는", "할 수 있는"],
        "responses": [
            "저는 덱스라는 로봇이에요! 이동하고 센서로 주변을 감지할 수 있어요.",
            "저는 로봇 덱스예요. 앞으로 가달라고 하시면 이동할 수 있어요.",
            "저는 덱스 로봇이에요. 움직이고 주변을 탐지하는 것이 제 특기예요."
        ]
    },
    "farewell": {
        "keywords": ["안녕히", "잘 가", "또 봐", "바이"],
        "responses": [
            "안녕히 가세요 {user_name}님! 또 만나요. 좋은 하루 되세요!",
            "안녕히 가세요! 언제든지 다시 찾아주세요.",
            "좋은 하루 보내세요! 또 봐요 {user_name}님."
        ]
    }
}
```

### 강화된 감정 상태 관리 (3순위 작업 완료)
16개 감정 상태 + 강도/카테고리 시스템

```python
# 감정 카테고리
EmotionCategory = {
    POSITIVE,    # 긍정적 (joyful, excited, happy, pleased)
    NEGATIVE,    # 부정적 (sad, frustrated, worried)
    NEUTRAL,     # 중립적 (neutral, confused, curious)
    MIXED        # 복합적 (bittersweet)
}

# 감정 강도 (5단계)
EmotionIntensity = {
    VERY_LOW: 1, LOW: 2, MEDIUM: 3, HIGH: 4, VERY_HIGH: 5
}

# 지원 감정 (16개)
emotion_states = {
    "joyful", "excited", "happy", "pleased",        # 긍정
    "curious", "interested",                        # 호기심
    "helpful", "supportive", "proud", "friendly",   # 도움/자랑
    "sad", "frustrated", "worried",                 # 부정
    "confused", "neutral", "bittersweet"            # 중립/복합
}

# 감정 응답 매핑
EmotionResponse = {
    emotion_state,     # EmotionState 객체
    led_expression,    # LED 표현
    buzzer_sound,      # 버저 소리
    response_modifier, # 응답 스타일
    animation          # 애니메이션 (선택)
}
```

### 강화된 대화 컨텍스트 관리 (3순위 작업 완료)
장기 기억 + 맥락 유지 시스템

```python
# 사용자 장기 기억
UserMemory = {
    "user_id": "string",
    "user_name": "string",
    "preferred_name": "string",
    "personality_traits": {"polite": 0.8, "curious": 0.6},
    "interests": ["로봇", "AI", "코딩"],
    "preferences": {"response_style": "casual"},
    "learned_patterns": {"greeting": 15, "command": 30},
    "total_interactions": "integer",
    "first_met": "datetime",
    "last_met": "datetime"
}

# 대화 컨텍스트 (세션 기반)
ConversationContext = {
    "user_id": "string",
    "session_id": "string",
    "user_memory": "UserMemory",
    "current_topics": ["주제1", "주제2"],
    "recent_messages": [{"timestamp", "message", "intent"}],
    "robot_mood": "happy",
    "conversation_phase": "conversation",  # greeting/introduction/conversation/command/farewell
    "last_intent": "praise",
    "last_emotion": "happy"
}

# 대화 주제 추적
ConversationTopic = {
    "topic": "로봇 이동",
    "started_at": "datetime",
    "last_mentioned": "datetime",
    "mention_count": 5,
    "related_keywords": ["앞으로", "이동", "전진"]
}
```

## 🎨 웹 인터페이스

- **HTML5** - 웹 페이지 구조
- **CSS3** - 스타일링 및 반응형 디자인
- **JavaScript (ES6+)** - 프론트엔드 로직
- **WebSocket API** - 실시간 통신
- **Fetch API** - HTTP 요청

## 📊 데이터 처리

### 사용자 경험 향상용 DB
- **SQLite** - 사용자 패턴 학습 및 개인화 (권장)
- **Redis** - 실시간 성능 향상 (선택사항)
- **PostgreSQL** - 클라우드 확장 (향후 계획)

### UX 향상 기능
- **명령어 학습**: 자주 사용하는 명령어 자동완성
- **스마트 제안**: 상황별 맞춤 제안
- **에러 분석**: 실패 패턴 학습 및 개선
- **감정 추적**: 사용자 만족도 기반 개성 발달

### 데이터 분석 도구
- **NumPy** (선택사항) - 수치 계산
- **Pandas** (선택사항) - 센서 데이터 분석
- **Matplotlib** (선택사항) - 매핑 데이터 시각화

### SQLite 스키마
```sql
-- 사용자 상호작용 테이블
CREATE TABLE user_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    command TEXT NOT NULL,
    response TEXT,
    success BOOLEAN,
    user_id TEXT DEFAULT 'default_user',
    session_id TEXT
);

-- 명령어 빈도 테이블
CREATE TABLE command_frequency (
    command TEXT PRIMARY KEY,
    count INTEGER DEFAULT 1,
    last_used DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 에러 패턴 테이블
CREATE TABLE error_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    failed_command TEXT,
    error_type TEXT,
    user_id TEXT
);

-- 감정 반응 테이블
CREATE TABLE emotion_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    emotion TEXT,
    trigger_command TEXT,
    user_satisfaction INTEGER CHECK(user_satisfaction >= 1 AND user_satisfaction <= 5)
);

-- 사용자 장기 기억 테이블 (3순위 추가)
CREATE TABLE user_long_term_memory (
    user_id TEXT PRIMARY KEY,
    user_name TEXT,
    preferred_name TEXT,
    personality_traits TEXT,  -- JSON
    interests TEXT,           -- JSON
    preferences TEXT,         -- JSON
    learned_patterns TEXT,    -- JSON
    total_interactions INTEGER DEFAULT 0,
    first_met DATETIME,
    last_met DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 개발 도구

- **mpremote** - 스크립트 삭제/업로드
- **esptool** - esp32 펌웨어 삭제/업로드
- **Git** - 버전 관리
- **CursorAI** - 파이썬 개발

## 🎯 완료된 기술 스택 개선 (우선순위 작업)

### ✅ 1순위: Testing (2025-10-05)
- **pytest** 8.4.2 - 테스트 프레임워크
- **pytest-asyncio** 1.2.0 - 비동기 테스트
- **FastAPI TestClient** - API 테스트
- **총 284개 테스트** (95% 통과율)

### ✅ 2순위: Error Handling (2025-10-07)
- **커스텀 예외 클래스** 40+개
- **전역 에러 핸들러** 4개
- **표준화된 에러 응답** 모델
- **에러 추적 및 통계** API

### ✅ 3순위: Chat Interaction Enhanced (2025-10-07)
- **ConversationContextManager** - 장기 기억 시스템
- **EmotionAnalyzer** - 16개 감정 + 강도/카테고리
- **20개 대화 시나리오** (기존 12개 + 신규 8개)
- **개인화 시스템** - 선호도/관심사 학습
- **user_long_term_memory** DB 테이블

### ✅ 4순위: Analytics (2025-10-07)
- **Analytics 서비스** - 사용자 행동 분석 및 통계
- **스마트 제안 시스템** - 패턴 기반 자동 제안
- **에러 분석** - 에러 패턴 추적 및 개선
- **사용자 프로필링** - 학습 레벨 및 선호도 분석

### ✅ 5순위: Expression API (2025-10-07)
- **LED 표정 제어** - 감정별 LED 매트릭스 패턴
- **버저 소리 제어** - 상황별 효과음
- **자동 표현 시스템** - 감정 상태 기반 자동 표현

### ✅ 6순위: ESP32 하드웨어 연동 (2025-10-08)
- **ESP32 S3 MicroPython 펌웨어** - 완전 작동
- **Socket Bridge** - FastAPI ↔ ESP32 통신
- **자연어 → 하드웨어** - End-to-End 통합 완료
- **Wi-Fi 자동 재연결** - 1~2초 내 복구

### 🚧 7순위: TinyML 도입 (계획 - 2025 Q4)
- **TensorFlow Lite for Microcontrollers** - ESP32 추론 환경
- **낙하 위험 예측 모델** - 첫 번째 TinyML 모델
- **센서 데이터 수집 시스템** - 학습 데이터셋 구축
- **모델 최적화 파이프라인** - Quantization + Pruning

## 🚨 주의사항

1. **ESP32 S3의 메모리 제한**: 마이크로파이썬은 메모리를 많이 사용하므로 효율적인 코딩 필요
2. **실시간성**: 센서 데이터 처리와 안전 시스템의 우선순위 관리 중요
3. **Wi-Fi 안정성**: 네트워크 연결 끊김 시 안전 모드로 전환하는 로직 필요
4. **전력 관리**: 배터리 사용 시 저전력 모드 구현 고려
5. **자연어 처리**: 규칙 기반 시스템의 한계로 인해 새로운 표현 학습 필요
6. **명령어 확장**: 사용자 피드백을 바탕으로 키워드 패턴 지속적 업데이트 필요
7. **TinyML 제약**: ESP32 메모리 제한으로 모델 크기 <100KB, 추론 시간 <100ms 필수

---

## 📊 개발 현황 요약 (2025-10-08)

### ✅ 완료된 개발 (1-6순위)
- **1순위 Testing**: 305개 테스트, 96% 통과율
- **2순위 Error Handling**: 40+ 커스텀 예외, 전역 에러 핸들러
- **3순위 Chat Interaction**: 장기 기억 + 16개 감정 상태
- **4순위 Analytics**: 사용자 패턴 분석 및 스마트 제안
- **5순위 Expression**: LED/버저 제어 및 자동 표현
- **6순위 ESP32 연동**: 펌웨어 + 통신 프로토콜 완성

### 🔮 향후 계획 (7-10순위)
- **7순위 TinyML**: 계획 단계 (2025 Q4)
- **8순위 SLAM**: 미개발
- **9순위 경로 계획**: 미개발
- **10순위 스마트 홈**: 미개발

---

*최종 업데이트: 2025년 10월 8일 (1-6순위 작업 완료, 7순위 TinyML 계획 수립)*