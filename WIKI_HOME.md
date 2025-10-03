# Deks 1.0 위키독스

<div align="center">


██████╗ ███████╗██╗  ██╗███████╗
██╔══██╗██╔════╝██║ ██╔╝██╔════╝
██║  ██║█████╗  █████╔╝ ███████╗
██║  ██║██╔══╝  ██╔═██╗ ╚════██║
██████╔╝███████╗██║  ██╗███████║
╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝


**1.0** 🤖

</div>
<div align="center">
**책상 위의 작은 친구가 되어주는 스마트 로봇**

[![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg)](http://unlicense.org/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![ESP32](https://img.shields.io/badge/ESP32-S3-green.svg)](https://www.espressif.com/en/products/socs/esp32-s3)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-009688.svg)](https://fastapi.tiangolo.com/)

</div>

---

## 🎯 프로젝트 개요

**Deks 1.0**은 책상 위에서 안전하게 돌아다니며 자연어로 대화할 수 있는 스마트 로봇입니다. ESP32 S3를 기반으로 하며, 웹 브라우저를 통해 직관적인 제어가 가능합니다.

### ✨ 주요 특징

- 🤖 **자연어 제어**: "앞으로 가줘", "오른쪽으로 돌아" 등 자연스러운 명령
- 🛡️ **안전 우선**: 낙하 방지 센서로 책상에서 떨어지지 않도록 보호
- 🎭 **감정 표현**: LED 매트릭스와 버저로 다양한 표정과 소리 표현
- 🌐 **웹 인터페이스**: 브라우저에서 실시간으로 로봇과 대화
- 📊 **학습 기능**: 사용자 패턴을 학습하여 개인화된 서비스 제공

---

## 📚 문서 가이드

### 🚀 시작하기

| 문서 | 설명 | 대상 |
|------|------|------|
| [📖 프로젝트 소개](README.md) | Deks 1.0의 전체적인 개요와 특징 | 모든 사용자 |
| [🛠️ 하드웨어 가이드](HARDWARE.md) | 부품 목록 및 구매 정보 | 하드웨어 제작자 |
| [⚙️ 하드웨어 인터페이스](HARDWARE_INTERFACE.md) | GPIO 핀 구성 및 연결 방법 | 하드웨어 개발자 |

### 🏗️ 개발자 가이드

| 문서 | 설명 | 대상 |
|------|------|------|
| [🏛️ 시스템 아키텍처](ARCHITECTURE.md) | 전체 시스템 구조 및 컴포넌트 설계 | 시스템 설계자 |
| [📡 통신 프로토콜](PROTOCOLS.md) | ESP32와 서버 간 통신 규격 | 백엔드 개발자 |
| [🔧 기술 스택](TECH_STACK.md) | 사용된 기술과 라이브러리 목록 | 개발자 |
| [🤖 로봇 행동 정의](BEHAVIOR.md) | 로봇의 동작 패턴 및 행동 규칙 | 펌웨어 개발자 |

### 🔌 API 문서

| 문서 | 설명 | 대상 |
|------|------|------|
| [📋 백엔드 API 명세서](BACKEND_API.md) | REST API 및 WebSocket API 상세 명세 | API 개발자 |

---

## 🎮 빠른 시작

### 1️⃣ 하드웨어 준비
```bash
# 필요한 부품 구매 (예상 비용: $80-135)
- ESP32 S3 개발보드
- FIT0405 DC 모터 2개
- L298N 모터 드라이버
- 1588AS LED 매트릭스
- 적외선 센서 2개
- 기타 부품들...
```

### 2️⃣ 소프트웨어 설치
```bash
# Python 환경 설정
pip install fastapi uvicorn websockets sqlite3

# ESP32 펌웨어 업로드
# (마이크로파이썬 펌웨어 설치)
```

### 3️⃣ 실행하기
```bash
# FastAPI 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000

# 웹 브라우저에서 접속
http://localhost:8000
```

---

## 🎯 사용 예시

### 기본 명령어
```
사용자: "앞으로 가줘"
Deks: "앞으로 이동합니다!" (전진 시작)

사용자: "오른쪽으로 돌아"
Deks: "오른쪽으로 회전합니다!" (제자리 회전)

사용자: "정지해줘"
Deks: "정지합니다!" (즉시 정지)
```

### 안전 기능
```
낙하 감지 시: "위험 감지! 정지합니다!" (즉시 정지)
장애물 감지 시: 자동 회피 동작
```

---

## 🛡️ 안전 기능

### 낙하 방지 시스템
- **적외선 센서**: 책상 가장자리 감지
- **즉시 정지**: 낙하 위험 시 자동 정지
- **안전 회피**: 180도 회전 후 안전한 방향으로 이동

### 장애물 회피
- **전방 센서**: 장애물 감지
- **자동 회피**: 안전한 거리 유지
- **스마트 경로**: 최적 경로로 이동

---

## 🎭 감정 표현

### LED 표정
- 😊 **행복**: 웃는 표정
- 😢 **슬픔**: 슬픈 표정  
- 😲 **놀람**: 놀란 표정
- ❤️ **사랑**: 하트 표정

### 음향 효과
- 🎵 **멜로디**: 기쁜 소리
- ⚠️ **경보**: 위험 알림
- ✅ **성공**: 작업 완료음
- ❌ **에러**: 오류 알림

---

## 🔧 기술 스택

### 하드웨어
- **ESP32 S3**: 메인 컨트롤러
- **마이크로파이썬**: 펌웨어 언어
- **FIT0405**: DC 모터 (엔코더 내장)
- **L298N**: 모터 드라이버

### 소프트웨어
- **FastAPI**: 백엔드 서버
- **WebSocket**: 실시간 통신
- **SQLite**: 사용자 데이터 저장
- **HTML/CSS/JavaScript**: 웹 인터페이스

### 설계 도구
- **Onshape**: 3D CAD 설계
- **KiCAD**: PCB 설계

---

## 🤝 기여하기

Deks 1.0은 오픈소스 프로젝트입니다! 여러분의 기여를 환영합니다.

### 기여 방법
1. **Fork** 이 저장소
2. **Feature 브랜치** 생성 (`git checkout -b feature/amazing-feature`)
3. **변경사항 커밋** (`git commit -m 'Add amazing feature'`)
4. **브랜치 푸시** (`git push origin feature/amazing-feature`)
5. **Pull Request** 생성

### 기여 영역
- 🐛 **버그 수정**: 문제점 발견 및 수정
- ✨ **새 기능**: 새로운 기능 추가
- 📚 **문서화**: 문서 개선 및 번역
- 🎨 **UI/UX**: 사용자 인터페이스 개선
- 🧪 **테스트**: 테스트 코드 작성

---

## 📞 지원 및 문의

### 문제 해결
- 📖 **FAQ**: 자주 묻는 질문
- 🐛 **이슈 트래커**: [GitHub Issues](https://github.com/kuyeon/deks1.0/issues)
- 💬 **토론**: [GitHub Discussions](https://github.com/kuyeon/deks1.0/discussions)

### 커뮤니티
- 🌐 **웹사이트**: [프로젝트 홈페이지](https://github.com/kuyeon/deks1.0)
- 📧 **이메일**: [프로젝트 메인테이너](mailto:kuyeon99@gmail.com)
- 💬 **디스코드**: [커뮤니티 서버](https://discord.gg/your-server)(준비중)

---

## 📄 라이선스

이 프로젝트는 [Unlicense](LICENSE) 하에 배포됩니다.

```
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>
```

---

## 🎉 감사의 말

Deks 1.0 프로젝트에 기여해주신 모든 분들께 감사드립니다.

### 주요 기여자
- **프로젝트 창시자**: [@kuyeon](https://github.com/kuyeon)
- **하드웨어 설계**: [기여자 이름]
- **소프트웨어 개발**: [기여자 이름]
- **문서화**: [기여자 이름]

### 특별 감사
- **ESP32 커뮤니티**: 마이크로파이썬 지원
- **FastAPI 팀**: 훌륭한 웹 프레임워크
- **오픈소스 커뮤니티**: 다양한 라이브러리와 도구

---

<div align="center">

**Deks 1.0** - 책상 위의 작은 친구가 되어주는 스마트 로봇

[![GitHub stars](https://img.shields.io/github/stars/kuyeon/deks1.0?style=social)](https://github.com/kuyeon/deks1.0/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/kuyeon/deks1.0?style=social)](https://github.com/kuyeon/deks1.0/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/kuyeon/deks1.0?style=social)](https://github.com/kuyeon/deks1.0/watchers)

</div>
