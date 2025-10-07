

# Deks 1.0 Analytics API 시스템

## 📋 개요

Deks 1.0 프로젝트의 **4순위 작업: Analytics API (사용자 분석 및 패턴 학습)**가 성공적으로 완료되었습니다. 이 문서는 사용자 분석 시스템의 구조, 기능, 그리고 사용법을 설명합니다.

## 🎯 주요 기능

### ✅ 완료된 기능

1. **사용자 행동 추적** - 명령 빈도, 시간대별 패턴, 에러 분석
2. **스마트 제안 시스템** - 4가지 알고리즘 기반 지능형 추천
3. **사용자 프로필 분석** - 학습 레벨, 선호도, 통계
4. **패턴 학습 시스템** - 시퀀스 패턴, 에러 패턴 감지
5. **피드백 관리** - 사용자 만족도 추적

## 🏗️ 시스템 구조

### 1. Analytics 서비스 (`analytics_service.py`)

#### 주요 데이터 모델

**CommandFrequency** - 명령 빈도 분석
```python
@dataclass
class CommandFrequency:
    command: str              # 명령 이름
    count: int                # 실행 횟수
    success_count: int        # 성공 횟수
    failure_count: int        # 실패 횟수
    success_rate: float       # 성공률 (%)
    last_used: datetime       # 마지막 사용 시각
    avg_execution_time: float # 평균 실행 시간 (초)
```

**TimeSlotPattern** - 시간대별 사용 패턴
```python
@dataclass
class TimeSlotPattern:
    time_slot: str           # morning, afternoon, evening, night
    command_count: int       # 명령 실행 횟수
    most_common_command: str # 가장 많이 사용한 명령
    avg_satisfaction: float  # 평균 만족도
```

**UserBehaviorProfile** - 사용자 행동 프로필
```python
@dataclass
class UserBehaviorProfile:
    user_id: str
    total_interactions: int       # 총 상호작용 수
    total_commands: int           # 총 명령 수
    favorite_commands: List[str]  # 자주 사용하는 명령 (상위 5개)
    command_success_rate: float   # 명령 성공률
    avg_session_duration: float   # 평균 세션 시간 (초)
    most_active_time_slot: str    # 가장 활동적인 시간대
    learning_level: str           # beginner/intermediate/advanced
    preferences: Dict[str, Any]   # 사용자 선호도
```

**SmartSuggestion** - 스마트 제안
```python
@dataclass
class SmartSuggestion:
    command: str          # 제안 명령
    confidence: float     # 신뢰도 (0.0 ~ 1.0)
    reason: str           # 제안 이유
    category: str         # frequency_based, time_based, error_prevention, sequence_optimization
```

### 2. 시간대 구분

| 시간대 | 시간 범위 | 설명 |
|--------|----------|------|
| **morning** | 06:00 - 11:59 | 아침 |
| **afternoon** | 12:00 - 17:59 | 오후 |
| **evening** | 18:00 - 22:59 | 저녁 |
| **night** | 23:00 - 05:59 | 밤 |

### 3. 학습 레벨 기준

| 레벨 | 상호작용 횟수 | 설명 |
|------|--------------|------|
| **beginner** | 0 - 20회 | 초보자 |
| **intermediate** | 21 - 100회 | 중급자 |
| **advanced** | 101회 이상 | 고급자 |

## 📖 API 엔드포인트 가이드

### 1. 사용자 패턴 분석

**GET `/api/v1/analytics/user-patterns`**

사용자의 행동 패턴을 종합적으로 분석합니다.

**파라미터:**
- `user_id` (required): 사용자 ID
- `days` (optional, default=7): 분석 기간 (1-365일)

**응답:**
```json
{
  "success": true,
  "user_id": "user_001",
  "analysis_period": "7_days",
  "behavior_profile": {
    "total_interactions": 45,
    "total_commands": 30,
    "success_rate": 93.33,
    "learning_level": "intermediate",
    "most_active_time": "evening",
    "avg_session_duration": 285.5
  },
  "frequent_commands": [
    {
      "command": "move_forward",
      "frequency": 12,
      "success_rate": 100.0
    },
    {
      "command": "turn_right",
      "frequency": 8,
      "success_rate": 87.5
    }
  ],
  "time_slot_patterns": [
    {
      "time_slot": "evening",
      "command_count": 18,
      "most_common_command": "move_forward"
    }
  ],
  "error_patterns": [
    {
      "command_type": "move_forward",
      "error_message": "로봇 미연결",
      "frequency": 2,
      "suggestions": ["로봇 연결 상태를 확인하세요"]
    }
  ],
  "timestamp": "2025-10-07T12:00:00Z"
}
```

### 2. 스마트 제안

**GET `/api/v1/analytics/suggestions`**

사용자 패턴 기반 지능형 명령 제안을 제공합니다.

**파라미터:**
- `user_id` (required): 사용자 ID
- `context` (optional, default="idle"): 현재 컨텍스트
- `limit` (optional, default=5): 제안 개수 (1-10)

**응답:**
```json
{
  "user_id": "user_001",
  "context": "idle",
  "suggestions": [
    {
      "command": "move_forward",
      "confidence": 0.85,
      "reason": "가장 자주 사용하는 명령입니다 (12회)"
    },
    {
      "command": "turn_right",
      "confidence": 0.72,
      "reason": "evening 시간대에 자주 사용합니다"
    },
    {
      "command": "stop",
      "confidence": 0.65,
      "reason": "'move_forward' 명령 시 에러가 자주 발생합니다"
    }
  ],
  "timestamp": "2025-10-07T12:00:00Z"
}
```

### 3. 사용자 통계

**GET `/api/v1/analytics/user-stats/{user_id}`**

특정 사용자의 상세 통계를 조회합니다.

**파라미터:**
- `user_id` (path): 사용자 ID
- `include_details` (optional, default=false): 상세 정보 포함 여부

**응답:**
```json
{
  "success": true,
  "user_stats": {
    "user_id": "user_001",
    "total_interactions": 45,
    "total_commands": 30,
    "success_rate": 93.33,
    "first_visit": "2025-10-01T10:00:00Z",
    "last_visit": "2025-10-07T18:30:00Z",
    "learning_level": "intermediate",
    "is_active": true
  },
  "command_frequencies": [  // include_details=true 시
    {
      "command": "move_forward",
      "count": 12,
      "success_rate": 100.0
    }
  ],
  "timestamp": "2025-10-07T12:00:00Z"
}
```

### 4. 명령 빈도

**GET `/api/v1/analytics/command-frequency`**

명령어 사용 빈도를 상세하게 조회합니다.

**파라미터:**
- `user_id` (required): 사용자 ID
- `limit` (optional, default=10): 결과 개수 (1-50)

**응답:**
```json
{
  "success": true,
  "user_id": "user_001",
  "command_frequencies": [
    {
      "command": "move_forward",
      "count": 12,
      "success_count": 12,
      "failure_count": 0,
      "success_rate": 100.0,
      "last_used": "2025-10-07T18:30:00Z",
      "avg_execution_time": 0.523
    }
  ],
  "timestamp": "2025-10-07T12:00:00Z"
}
```

### 5. 에러 패턴

**GET `/api/v1/analytics/error-patterns`**

에러 발생 패턴을 분석하고 해결 방법을 제안합니다.

**파라미터:**
- `user_id` (optional): 사용자 ID (없으면 전체)
- `days` (optional, default=7): 분석 기간 (1-90일)

**응답:**
```json
{
  "success": true,
  "user_id": "user_001",
  "analysis_period": "7_days",
  "error_patterns": [
    {
      "command_type": "move_forward",
      "error_message": "로봇이 연결되지 않았습니다",
      "frequency": 3,
      "suggestions": [
        "로봇 연결 상태를 확인하세요",
        "Wi-Fi 연결을 확인하세요"
      ]
    }
  ],
  "total_errors": 3,
  "timestamp": "2025-10-07T12:00:00Z"
}
```

### 6. 전체 통계

**GET `/api/v1/analytics/statistics`**

전체 시스템의 통계를 조회합니다.

**응답:**
```json
{
  "success": true,
  "statistics": {
    "total_users": 12,
    "total_commands": 456,
    "success_rate": 94.52,
    "most_popular_command": "move_forward",
    "avg_session_duration_seconds": 287.3,
    "error_rate": 5.48,
    "timestamp": "2025-10-07T12:00:00Z"
  },
  "timestamp": "2025-10-07T12:00:00Z"
}
```

### 7. 피드백 제출

**POST `/api/v1/analytics/feedback`**

사용자 피드백을 제출합니다.

**요청 body:**
```json
{
  "user_id": "user_001",
  "command_id": "cmd_12345",
  "satisfaction": 5,
  "feedback": "정말 잘 작동해요!",
  "timestamp": "2025-10-07T12:00:00Z"
}
```

**응답:**
```json
{
  "success": true,
  "message": "피드백이 성공적으로 제출되었습니다",
  "feedback_id": "fb_1696680000",
  "timestamp": "2025-10-07T12:00:00Z"
}
```

## 🔍 스마트 제안 알고리즘

### 1. 빈도 기반 제안 (Frequency-Based)
- 가장 자주 사용하는 명령어 우선 추천
- 신뢰도: 0.5 ~ 0.95 (사용 횟수에 비례)

### 2. 시간대 기반 제안 (Time-Based)
- 현재 시간대에 자주 사용하는 명령 추천
- 신뢰도: 0.7

### 3. 에러 방지 제안 (Error Prevention)
- 최근 에러가 발생한 명령의 대안 제안
- 신뢰도: 0.65

### 4. 시퀀스 최적화 제안 (Sequence Optimization)
- 명령 시퀀스 패턴 분석하여 다음 명령 예측
- 신뢰도: 0.6

## 📊 데이터베이스 스키마

### user_feedback 테이블 🆕
```sql
CREATE TABLE user_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feedback_id TEXT UNIQUE NOT NULL,
    user_id TEXT NOT NULL,
    command_id TEXT,
    satisfaction INTEGER CHECK(satisfaction >= 1 AND satisfaction <= 5),
    feedback TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT 0
)
```

## 🧪 테스트

### 테스트 파일
- `test_analytics.py` - Analytics 시스템 테스트

### 테스트 실행
```bash
cd backend
python -m pytest tests/test_analytics.py -v
```

### 테스트 범위 (21개 테스트, 100% 통과)
- ✅ Analytics 서비스 초기화 (1개)
- ✅ 시간대 감지 (1개)
- ✅ 학습 레벨 결정 (1개)
- ✅ 데이터 모델 (4개)
- ✅ 에러 수정 제안 (3개)
- ✅ 전체 통계 (2개)
- ✅ 사용자 통계 (2개)
- ✅ 스마트 제안 (3개)
- ✅ 파라미터 검증 (2개)
- ✅ API 통합 (2개)

## 🎨 사용 예제

### 1. 사용자 패턴 분석

```bash
curl "http://localhost:8000/api/v1/analytics/user-patterns?user_id=user_001&days=7"
```

### 2. 스마트 제안 받기

```bash
curl "http://localhost:8000/api/v1/analytics/suggestions?user_id=user_001&limit=5"
```

### 3. 피드백 제출

```bash
curl -X POST "http://localhost:8000/api/v1/analytics/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "command_id": "cmd_123",
    "satisfaction": 5,
    "feedback": "완벽해요!"
  }'
```

### 4. 전체 통계 조회

```bash
curl "http://localhost:8000/api/v1/analytics/statistics"
```

## 📈 분석 기능 상세

### 사용자 행동 추적

**추적 항목:**
- 명령 실행 빈도 (어떤 명령을 얼마나 자주 사용하는가)
- 시간대별 패턴 (언제 가장 활동적인가)
- 성공률 (명령이 얼마나 잘 실행되는가)
- 세션 시간 (평균적으로 얼마나 오래 사용하는가)
- 학습 레벨 (얼마나 숙련되었는가)

**활용:**
- 사용자 맞춤 UI/UX 제공
- 개인화된 응답 생성
- 학습 레벨별 가이드 제공

### 스마트 제안 시스템

**제안 카테고리:**

1. **빈도 기반** (frequency_based)
   - 예: "가장 자주 사용하는 명령입니다 (12회)"
   - 신뢰도: 높음

2. **시간대 기반** (time_based)
   - 예: "evening 시간대에 자주 사용합니다"
   - 신뢰도: 중간

3. **에러 방지** (error_prevention)
   - 예: "'move_forward' 명령 시 에러가 자주 발생합니다"
   - 신뢰도: 중간

4. **시퀀스 최적화** (sequence_optimization)
   - 예: "탐색을 위해 우회전해보세요"
   - 신뢰도: 낮음

### 에러 패턴 분석

**감지 가능한 에러 유형:**
- 연결 에러 → "로봇 연결 상태 확인" 제안
- 타임아웃 에러 → "명령 재시도" 제안
- 파라미터 에러 → "올바른 값 입력" 제안

**자동 제안:**
- 에러 발생 시 즉시 해결 방법 제시
- 반복되는 에러는 우선순위 높게 경고

## 🔧 Python 코드 예제

### Analytics Service 사용

```python
from app.services.analytics_service import get_analytics_service

# 서비스 조회
analytics = await get_analytics_service()

# 사용자 행동 분석
profile = await analytics.analyze_user_behavior(
    user_id="user_001",
    days=7
)

print(f"학습 레벨: {profile.learning_level}")
print(f"선호 명령: {profile.favorite_commands}")

# 스마트 제안 생성
suggestions = await analytics.generate_smart_suggestions(
    user_id="user_001",
    context="idle",
    limit=5
)

for sug in suggestions:
    print(f"{sug.command} (신뢰도: {sug.confidence:.2f}) - {sug.reason}")

# 전체 통계
global_stats = await analytics.get_global_statistics()
print(f"전체 사용자: {global_stats['total_users']}")
print(f"성공률: {global_stats['success_rate']}%")
```

## 📊 활용 시나리오

### 시나리오 1: 초보 사용자 가이드

```python
# 사용자 통계 확인
stats = await analytics.get_user_statistics("new_user")

if stats["learning_level"] == "beginner":
    # 초보자에게 기본 명령 제안
    suggestions = await analytics.generate_smart_suggestions(
        user_id="new_user",
        context="tutorial"
    )
    # → "앞으로 가줘", "정지해줘" 등 기본 명령 제안
```

### 시나리오 2: 에러 발생 시 자동 제안

```python
# 에러 패턴 분석
error_patterns = await analytics.analyze_error_patterns(
    user_id="user_001",
    days=7
)

if error_patterns:
    # 가장 빈번한 에러의 해결 방법 표시
    top_error = error_patterns[0]
    print(f"제안: {top_error['suggestions']}")
```

### 시나리오 3: 시간대별 맞춤 제안

```python
from datetime import datetime

current_hour = datetime.now().hour

# 현재 시간대에 맞는 제안
suggestions = await analytics.generate_smart_suggestions(
    user_id="user_001",
    context=f"time_{current_hour}"
)
# → 해당 시간대에 자주 사용하는 명령 우선 제안
```

## 🚀 향후 개선 계획

### 계획 중인 기능
- [ ] **머신러닝 모델** - TensorFlow/scikit-learn 기반 예측
- [ ] **A/B 테스팅** - 제안 알고리즘 성능 비교
- [ ] **실시간 대시보드** - 통계 시각화
- [ ] **이상 감지** - 비정상 사용 패턴 자동 감지
- [ ] **예측 모델** - 다음 명령 예측 정확도 향상

## 📝 관련 문서

- [테스트 문서](../tests/README.md) - 테스트 시스템 가이드
- [에러 처리 가이드](ERROR_HANDLING.md) - 에러 처리 시스템
- [대화 시스템 가이드](CHAT_INTERACTION_ENHANCED.md) - 강화된 대화 시스템
- [API 문서](/docs) - FastAPI 자동 생성 문서

## 🎉 결론

Deks 1.0의 4순위 개발 작업인 **Analytics API**가 성공적으로 완료되었습니다:

- ✅ **사용자 행동 추적** - 빈도, 시간대, 패턴 분석
- ✅ **스마트 제안 시스템** - 4가지 알고리즘 기반 추천
- ✅ **사용자 프로필 분석** - 학습 레벨, 통계, 선호도
- ✅ **에러 패턴 분석** - 자동 해결 방법 제안
- ✅ **피드백 시스템** - 사용자 만족도 추적
- ✅ **7개 API 엔드포인트** 구현
- ✅ **21개 테스트** 100% 통과

이제 데이터 기반으로 사용자 경험을 개선할 수 있는 시스템이 완성되었습니다!

---

*Analytics API 시스템 구축 완료 - 2025년 10월 7일*

