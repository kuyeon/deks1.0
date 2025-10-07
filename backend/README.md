# Deks 1.0 백엔드 서버

Deks 1.0 로봇을 위한 FastAPI 기반 백엔드 서버입니다.

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
cd backend
pip install -r requirements.txt
```

### 2. 서버 실행

```bash
# 개발 모드 (자동 재시작)
python run_server.py

# 또는 직접 실행
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. API 문서 확인

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📁 프로젝트 구조

```
backend/
├── app/
│   ├── api/v1/          # API 엔드포인트
│   │   ├── endpoints/   # 각 기능별 라우터
│   │   └── __init__.py
│   ├── core/            # 핵심 설정
│   │   ├── config.py    # 설정 관리
│   │   └── __init__.py
│   ├── database/        # 데이터베이스
│   │   ├── init_db.py   # DB 초기화
│   │   └── __init__.py
│   ├── models/          # 데이터 모델
│   ├── services/        # 비즈니스 로직
│   ├── utils/           # 유틸리티
│   └── main.py          # 메인 애플리케이션
├── tests/               # 테스트
├── docs/                # 문서
├── requirements.txt     # 의존성
├── pyproject.toml      # 프로젝트 설정
├── run_server.py       # 서버 실행 스크립트
└── README.md
```

## 🔌 API 엔드포인트

### 로봇 제어
- `POST /api/v1/robot/move/forward` - 전진
- `POST /api/v1/robot/move/turn` - 회전
- `POST /api/v1/robot/stop` - 정지
- `GET /api/v1/robot/status` - 상태 조회

### 자연어 처리
- `POST /api/v1/nlp/parse-command` - 명령 파싱
- `GET /api/v1/nlp/commands` - 지원 명령어 목록

### 센서 데이터
- `GET /api/v1/sensors/distance` - 거리 센서
- `GET /api/v1/sensors/position` - 위치 정보
- `GET /api/v1/sensors/battery` - 배터리 상태

### 표현 제어
- `POST /api/v1/expression/led` - LED 표정
- `POST /api/v1/expression/buzzer` - 버저 소리

### 사용자 분석
- `GET /api/v1/analytics/user-patterns` - 사용자 패턴
- `GET /api/v1/analytics/suggestions` - 스마트 제안
- `POST /api/v1/analytics/feedback` - 피드백 제출

### WebSocket
- `WS /api/v1/ws/robot` - 로봇 연결
- `WS /api/v1/ws/client` - 클라이언트 연결

## 🗄️ 데이터베이스

SQLite 데이터베이스를 사용하며, 다음과 같은 테이블이 자동으로 생성됩니다:

- `user_interactions` - 사용자 상호작용 기록
- `command_frequency` - 명령어 사용 빈도
- `error_patterns` - 에러 패턴 분석
- `emotion_responses` - 감정 반응 기록
- `robot_states` - 로봇 상태 기록
- `sensor_data` - 센서 데이터
- `command_execution_logs` - 명령 실행 로그

## ⚙️ 설정

환경 변수를 통해 설정을 변경할 수 있습니다:

```bash
# 서버 설정
HOST=0.0.0.0
PORT=8000
DEBUG=true

# 데이터베이스
DATABASE_URL=sqlite:///./deks.db

# 로봇 통신
ROBOT_TCP_PORT=8888
ROBOT_CONNECTION_TIMEOUT=30

# 로깅
LOG_LEVEL=INFO
LOG_FILE=logs/deks.log
```

## 🧪 테스트

```bash
# 테스트 실행
pytest

# 커버리지 포함 테스트
pytest --cov=app tests/
```

## 📝 개발 가이드

### 새로운 API 엔드포인트 추가

1. `app/api/v1/endpoints/` 디렉토리에 새로운 라우터 파일 생성
2. `app/api/v1/__init__.py`에서 라우터 등록
3. 필요한 경우 `app/models/`에 데이터 모델 추가

### Socket Bridge 통합

Socket Bridge 모듈이 `app/services/socket_bridge.py`에 구현되어 있습니다:
- ESP32와의 TCP 통신 (포트 8888)
- 실시간 센서 데이터 수신
- 로봇 명령 전송
- 연결 상태 모니터링
- 자동 재연결 메커니즘

## 🔧 개발 도구

- **FastAPI**: 웹 프레임워크
- **Uvicorn**: ASGI 서버
- **Pydantic**: 데이터 검증
- **SQLite**: 데이터베이스
- **Loguru**: 로깅
- **WebSocket**: 실시간 통신

## 📞 지원

문제가 발생하거나 질문이 있으시면 GitHub Issues를 통해 문의해 주세요.

---

**Deks 1.0 백엔드** - 안전하고 효율적인 로봇 제어를 위한 완전한 API 서버
