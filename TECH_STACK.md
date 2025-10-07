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

## 🚨 주의사항

1. **ESP32 S3의 메모리 제한**: 마이크로파이썬은 메모리를 많이 사용하므로 효율적인 코딩 필요
2. **실시간성**: 센서 데이터 처리와 안전 시스템의 우선순위 관리 중요
3. **Wi-Fi 안정성**: 네트워크 연결 끊김 시 안전 모드로 전환하는 로직 필요
4. **전력 관리**: 배터리 사용 시 저전력 모드 구현 고려
5. **자연어 처리**: 규칙 기반 시스템의 한계로 인해 새로운 표현 학습 필요
6. **명령어 확장**: 사용자 피드백을 바탕으로 키워드 패턴 지속적 업데이트 필요

---

*최종 업데이트: 2025년 10월 7일 (1-3순위 작업 완료)*