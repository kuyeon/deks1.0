# Deks 1.0 강화된 Chat Interaction 시스템

## 📋 개요

Deks 1.0 프로젝트의 **3순위 작업: Chat Interaction API 고도화**가 성공적으로 완료되었습니다. 이 문서는 개선된 대화 시스템의 구조, 기능, 그리고 사용법을 설명합니다.

## 🎯 주요 개선 사항

### ✅ 완료된 기능

1. **강화된 대화 컨텍스트 관리** - 장기 기억 및 맥락 유지
2. **고도화된 감정 분석 시스템** - 15+ 감정 상태, 강도 및 카테고리
3. **확장된 대화 시나리오** - 8개 신규 시나리오 추가
4. **개인화 시스템** - 사용자별 선호도 및 관심사 학습
5. **스마트 응답 생성** - 컨텍스트 기반 맞춤 응답
6. **대화 흐름 관리** - 주제 추적 및 대화 단계 관리

## 🏗️ 시스템 구조

### 1. 대화 컨텍스트 관리자 (`conversation_context_manager.py`)

#### 주요 기능

**장기 기억 시스템 (UserMemory)**
```python
@dataclass
class UserMemory:
    user_id: str
    user_name: Optional[str]              # 사용자 이름
    preferred_name: Optional[str]         # 선호하는 호칭
    personality_traits: Dict[str, float]  # 성격 특성
    interests: List[str]                  # 관심사
    preferences: Dict[str, Any]           # 선호도
    learned_patterns: Dict[str, int]      # 학습된 패턴
    total_interactions: int               # 총 상호작용 수
    first_met: datetime                   # 첫 만남 시각
    last_met: datetime                    # 마지막 만남 시각
```

**대화 컨텍스트 (ConversationContext)**
```python
@dataclass
class ConversationContext:
    user_id: str
    session_id: str
    user_memory: UserMemory               # 장기 기억
    current_topics: List[ConversationTopic]  # 현재 주제들
    recent_messages: List[Dict]           # 최근 10개 메시지
    robot_mood: str                       # 로봇 분위기
    conversation_phase: str               # 대화 단계
    last_intent: Optional[str]            # 마지막 의도
    last_emotion: Optional[str]           # 마지막 감정
```

**대화 주제 추적 (ConversationTopic)**
```python
@dataclass
class ConversationTopic:
    topic: str                    # 주제 이름
    started_at: datetime         # 시작 시각
    last_mentioned: datetime     # 마지막 언급 시각
    mention_count: int           # 언급 횟수
    related_keywords: List[str]  # 관련 키워드
```

### 2. 강화된 감정 분석기 (`emotion_analyzer.py`)

#### 감정 카테고리
- **POSITIVE**: 긍정적 (happy, joyful, excited, pleased)
- **NEGATIVE**: 부정적 (sad, frustrated, worried)
- **NEUTRAL**: 중립적 (neutral, confused, curious)
- **MIXED**: 복합적 (bittersweet)

#### 감정 강도
- **VERY_LOW** (1): 매우 약함
- **LOW** (2): 약함
- **MEDIUM** (3): 보통
- **HIGH** (4): 강함
- **VERY_HIGH** (5): 매우 강함

#### 감정 상태 (EmotionState)
```python
@dataclass
class EmotionState:
    primary_emotion: str          # 주 감정
    secondary_emotion: Optional[str]  # 부 감정
    category: EmotionCategory     # 카테고리
    intensity: EmotionIntensity   # 강도
    sentiment_score: float        # 감정 점수 (-1.0 ~ 1.0)
    confidence: float             # 신뢰도
    triggers: List[str]           # 유발 키워드
```

#### 지원 감정 (15+)
1. **joyful** - 기쁨 (매우 긍정적)
2. **excited** - 흥분
3. **happy** - 행복
4. **pleased** - 만족
5. **curious** - 호기심
6. **interested** - 관심
7. **helpful** - 도움주려는
8. **supportive** - 지지하는
9. **proud** - 자랑스러운
10. **friendly** - 친근한
11. **sad** - 슬픔
12. **frustrated** - 좌절
13. **worried** - 걱정
14. **confused** - 혼란
15. **neutral** - 중립
16. **bittersweet** - 씁쓸한

### 3. 확장된 대화 시나리오 (`chat_service.py`)

#### 기존 시나리오 (12개)
- greeting (인사)
- introduction (자기소개)
- question_about_robot (로봇 질문)
- question_capabilities (능력 질문)
- request_help (도움 요청)
- praise (칭찬)
- compliment (칭찬)
- farewell (작별)
- confused (혼란)
- robot_move_forward (전진)
- robot_turn (회전)
- robot_stop (정지)
- robot_spin (빙글빙글)

#### 신규 시나리오 (8개) 🆕
- **question_about_feelings** - 기분/상태 질문
- **question_about_name** - 이름 질문
- **casual_chat** - 일상 대화
- **encouragement** - 응원/격려
- **apology** - 사과
- **love_expression** - 사랑/좋아함 표현
- **joke_request** - 장난/재미 요청
- **weather_question** - 날씨 질문
- **time_question** - 시간 질문

## 📖 사용 가이드

### 1. 컨텍스트 기반 대화

#### 첫 만남 시나리오
```python
# 사용자 첫 방문
user: "안녕"
deks: "안녕하세요! 저는 덱스에요. 처음 뵙겠습니다! 당신은 누구신가요?"

# 자기소개
user: "저는 김철수예요"
deks: "안녕하세요 김철수님! 만나서 반가워요. 저는 덱스라고 해요."
```

#### 재방문 사용자 시나리오
```python
# 10회 이상 상호작용한 사용자
user: "안녕"
deks: "안녕하세요 김철수님! 또 만나서 반가워요!"  # 이름을 기억함
```

### 2. 감정 기반 응답

#### 긍정적 감정
```python
user: "정말 최고야! 너무 좋아!"
deks: (joyful 감정으로 응답)
     LED: happy_animated
     Buzzer: success_melody
     Animation: rainbow
```

#### 부정적 감정
```python
user: "짜증나요..."
deks: (supportive 감정으로 응답)
     "괜찮아요! 제가 도와드릴게요."
     LED: warm
     Buzzer: success
```

### 3. 주제 추적

```python
# 대화 흐름
user: "너 뭐 할 수 있어?"
deks: "이동하고 센서로 주변을 감지할 수 있어요."
      Topics: ["로봇 능력"]

user: "앞으로 가줘"
deks: "앞으로 이동하겠습니다!"
      Topics: ["로봇 능력", "로봇 이동"]

# 5분 후 주제가 변경되면 이전 주제는 자동 제거
```

### 4. 개인화 기능

```python
# 사용자 관심사 학습
context_manager = await get_context_manager()
await context_manager.add_user_interest(session_id, "로봇")
await context_manager.add_user_interest(session_id, "AI")

# 사용자 선호도 설정
await context_manager.add_user_preference(
    session_id,
    "response_style",
    "casual"  # 캐주얼한 응답 선호
)

# 특정 정보 기억
await context_manager.remember_info(
    session_id,
    "favorite_color",
    "파란색"
)
```

### 5. 대화 통계 조회

```python
# 대화 요약
summary = await context_manager.get_conversation_summary(session_id)

{
    "user_id": "user_001",
    "session_id": "session_123",
    "user_name": "김철수",
    "conversation_phase": "conversation",
    "robot_mood": "happy",
    "current_topics": ["로봇 이동", "칭찬"],
    "message_count": 5,
    "total_interactions": 15,
    "interests": ["로봇", "AI"],
    "last_intent": "praise",
    "last_emotion": "happy"
}
```

## 🎨 대화 단계 (Conversation Phase)

### 1. **greeting** - 인사 단계
- 첫 만남 시 활성화
- 사용자 정보 파악에 집중

### 2. **introduction** - 소개 단계
- 자기소개 진행
- 이름, 관심사 학습

### 3. **conversation** - 대화 단계
- 일반적인 대화 진행
- 다양한 주제 탐색

### 4. **command** - 명령 단계
- 로봇 제어 명령 처리
- 즉각적인 피드백 제공

### 5. **farewell** - 작별 단계
- 대화 종료 준비
- 다음 만남 약속

## 📊 데이터베이스 스키마

### user_long_term_memory 테이블 🆕
```sql
CREATE TABLE user_long_term_memory (
    user_id TEXT PRIMARY KEY,
    user_name TEXT,
    preferred_name TEXT,
    personality_traits TEXT,      -- JSON
    interests TEXT,               -- JSON
    preferences TEXT,             -- JSON
    learned_patterns TEXT,        -- JSON
    total_interactions INTEGER,
    first_met DATETIME,
    last_met DATETIME,
    created_at DATETIME,
    updated_at DATETIME
)
```

## 🧪 테스트

### 테스트 파일
- `test_chat_interaction_enhanced.py` - 강화된 채팅 시스템 테스트

### 테스트 실행
```bash
cd backend
python -m pytest tests/test_chat_interaction_enhanced.py -v
```

### 테스트 범위
- ✅ 대화 컨텍스트 관리 (7개 테스트)
- ✅ 감정 분석 시스템 (10개 테스트)
- ✅ 강화된 시나리오 (7개 테스트)
- ✅ 사용자 기억 시스템 (4개 테스트)
- ✅ 감정 응답 시스템 (3개 테스트)
- ✅ 채팅 서비스 통합 (3개 테스트)
- ✅ 대화 흐름 (2개 테스트)

**총 36개 테스트**

## 🎨 응답 예제

### 1. 기분 질문
```
사용자: "기분 어때?"
덱스: "저는 정말 좋아요! 당신과 대화하는 게 즐거워요."
감정: happy
LED: happy
```

### 2. 이름 질문
```
사용자: "너 이름이 뭐야?"
덱스: "제 이름은 덱스예요! 책상(Desk)에서 이름을 따왔어요."
감정: proud
LED: happy
```

### 3. 사랑 표현
```
사용자: "정말 귀여워!"
덱스: "저도 당신이 좋아요! 정말 고마워요!"
감정: joyful
LED: happy_animated
Buzzer: success_melody
```

### 4. 응원
```
사용자: "파이팅!"
덱스: "파이팅! 당신은 할 수 있어요!"
감정: supportive
LED: warm
```

### 5. 컨텍스트 기반 응답
```
# 첫 방문
사용자: "안녕"
덱스: "안녕하세요! 저는 덱스에요. 처음 뵙겠습니다! 당신은 누구신가요?"

# 10회 이상 방문 후
사용자: "안녕"
덱스: "안녕하세요 김철수님! 또 만나서 반가워요!"
```

## 🔧 API 사용법

### 강화된 채팅 메시지 API

```bash
POST /api/v1/chat/message
Content-Type: application/json

{
  "message": "기분 어때?",
  "user_id": "user_001",
  "session_id": "session_123"
}
```

**응답 (강화됨):**
```json
{
  "success": true,
  "message_id": "msg_456",
  "response": "저는 정말 좋아요! 당신과 대화하는 게 즐거워요.",
  "emotion": "happy",
  "conversation_type": "question_about_feelings",
  "timestamp": "2025-10-07T12:00:00Z",
  "context": {
    "user_name": "김철수",
    "robot_mood": "happy",
    "follow_up": "오늘은 어떤 도움이 필요하신가요?",
    "conversation_phase": "conversation",
    "current_topics": ["인사", "기분 질문"],
    "total_interactions": 15
  },
  "nlp_analysis": {
    "intent_confidence": 0.85,
    "emotion_confidence": 0.92,
    "sentiment_score": 0.7,
    "keywords": ["기분", "어때"],
    "is_question": true,
    "question_type": "state"
  }
}
```

## 📈 개선 전후 비교

| 기능 | 개선 전 | 개선 후 |
|------|---------|---------|
| **감정 종류** | 8개 | **16개** (+8) |
| **대화 시나리오** | 12개 | **20개** (+8) |
| **컨텍스트 관리** | 기본 | **장기 기억 + 맥락 유지** |
| **감정 분석** | 키워드 기반 | **다차원 분석 (카테고리/강도/점수)** |
| **개인화** | 제한적 | **선호도/관심사 학습** |
| **응답 품질** | 랜덤 선택 | **컨텍스트 기반 맞춤** |
| **대화 흐름** | 없음 | **주제 추적 + 단계 관리** |
| **데이터베이스** | 6개 테이블 | **7개 테이블** (+1) |

## 🎯 활용 시나리오

### 시나리오 1: 신규 사용자 첫 만남
```
1. 사용자: "안녕"
   덱스: "안녕하세요! 저는 덱스에요. 처음 뵙겠습니다! 당신은 누구신가요?"
   
2. 사용자: "저는 김철수예요"
   덱스: "안녕하세요 김철수님! 만나서 반가워요. 저는 덱스라고 해요."
   [장기 기억에 "김철수" 저장]
   
3. 사용자: "넌 뭐 할 수 있어?"
   덱스: "저는 이동하고 센서로 주변을 감지할 수 있어요. 명령을 내려보세요!"
   [주제: "로봇 능력" 추적]
   
4. 사용자: "앞으로 가줘"
   덱스: "앞으로 이동하겠습니다!"
   [대화 단계: command로 전환]
```

### 시나리오 2: 재방문 사용자
```
1. 사용자: "안녕"
   덱스: "안녕하세요 김철수님! 또 만나서 반가워요!"
   [이름을 기억하고 있음]
   
2. 사용자: "기분 어때?"
   덱스: "저는 정말 좋아요! 당신과 대화하는 게 즐거워요."
   [감정: happy, 친밀한 응답]
```

### 시나리오 3: 감정적 상호작용
```
1. 사용자: "정말 귀여워!"
   덱스: "와! 정말 기뻐요! 저도 당신을 좋아해요!"
   [감정: joyful, LED: happy_animated, 애니메이션: rainbow]
   
2. 사용자: "잘했어!"
   덱스: "고마워요! 정말 기뻐요!"
   [감정: excited, 칭찬에 반응]
```

## 🔧 모범 사례

### 1. 컨텍스트 활용

```python
# 컨텍스트 관리자 조회
context_manager = await get_context_manager()

# 컨텍스트 생성
context = await context_manager.get_or_create_context(
    user_id="user_001",
    session_id="session_123"
)

# 정보 조회
user_name = await context_manager.get_contextual_info(
    "session_123",
    "user_name"
)
```

### 2. 감정 분석

```python
# 감정 분석기 조회
emotion_analyzer = get_emotion_analyzer()

# 감정 분석
emotion_state = emotion_analyzer.analyze_emotion(
    text="정말 좋아요!",
    intent="praise"
)

# 감정 응답 생성
emotion_response = emotion_analyzer.get_emotion_response(emotion_state)
```

### 3. 채팅 서비스 사용

```python
chat_service = ChatService()

# 메시지 처리
response = await chat_service.process_message(
    message="안녕",
    user_id="user_001",
    session_id="session_123"
)
```

## 🚀 향후 개선 계획

### 계획 중인 기능
- [ ] **대화 학습 AI** - 머신러닝 기반 응답 생성
- [ ] **다국어 지원** - 영어, 일본어 등 추가
- [ ] **음성 인식 통합** - 음성으로 대화하기
- [ ] **감정 표현 애니메이션** - LED 매트릭스 동적 표현
- [ ] **대화 요약 기능** - 긴 대화 자동 요약
- [ ] **추천 시스템** - 사용자 패턴 기반 제안

## 📝 관련 문서

- [테스트 문서](../tests/README.md) - 테스트 시스템 가이드
- [에러 처리 가이드](ERROR_HANDLING.md) - 에러 처리 시스템
- [API 문서](/docs) - FastAPI 자동 생성 문서

## 🎉 결론

Deks 1.0의 3순위 개발 작업인 **Chat Interaction API 고도화**가 성공적으로 완료되었습니다:

- ✅ **강화된 컨텍스트 관리** - 장기 기억 + 맥락 유지
- ✅ **고도화된 감정 분석** - 16개 감정 상태 + 강도/카테고리
- ✅ **확장된 대화 시나리오** - 20개 시나리오 (기존 12개 + 신규 8개)
- ✅ **개인화 시스템** - 사용자별 선호도 및 관심사 학습
- ✅ **스마트 응답 생성** - 컨텍스트 기반 맞춤 응답
- ✅ **대화 흐름 관리** - 주제 추적 + 대화 단계 관리
- ✅ **36개 신규 테스트** 작성

이제 더욱 자연스럽고 지능적인 대화가 가능한 로봇이 되었습니다!

---

*Chat Interaction 시스템 고도화 완료 - 2025년 10월 7일*

