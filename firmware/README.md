# Deks 1.0 ESP32 펌웨어

ESP32 S3 기반 Deks 로봇의 마이크로파이썬 펌웨어입니다.

## 📋 기능

### 핵심 기능
- **TCP 클라이언트 통신**: 서버와 실시간 통신
- **모터 제어**: FIT0405 DC 모터 + L298N 드라이버
- **센서 데이터 수집**: 적외선 센서, 엔코더
- **LED 표정 제어**: 1588AS LED 매트릭스
- **버저 소리 제어**: PWM 기반 멜로디 재생
- **배터리 모니터링**: 전압 측정 및 경고
- **안전 시스템**: 낙하 방지, 장애물 회피

### 통신 프로토콜
- **JSON 기반 메시지**: 명령 및 상태 데이터
- **하트비트 시스템**: 연결 상태 모니터링
- **에러 처리**: 자동 재연결 및 복구

## 🔧 하드웨어 구성

### GPIO 핀 배치
```
모터 제어:
  GPIO 2, 3  → 왼쪽 모터 (PWM, 방향)
  GPIO 4, 5  → 오른쪽 모터 (PWM, 방향)

엔코더:
  GPIO 6, 7  → 왼쪽 엔코더 (A, B 채널)
  GPIO 8, 9  → 오른쪽 엔코더 (A, B 채널)

센서:
  GPIO 10    → 낙하 방지 센서 (ADC)
  GPIO 11    → 장애물 감지 센서 (ADC)
  GPIO 13    → 배터리 모니터링 (ADC)

표현 시스템:
  GPIO 35, 36 → LED 매트릭스 (I2C)
  GPIO 12     → 버저 (PWM)

상태 표시:
  GPIO 14     → 상태 LED
```

### 하드웨어 사양
- **메인 컨트롤러**: ESP32 S3 DevKitC-1
- **모터**: FIT0405 DC 기어드 모터 (6V, 200RPM, 엔코더 내장)
- **모터 드라이버**: L298N 듀얼 H-브리지
- **센서**: 적외선 거리센서 (5-30cm)
- **LED 매트릭스**: 1588AS 8x8 LED 매트릭스
- **버저**: 5V 패시브 버저
- **전원**: 3.7V 리튬 폴리머 배터리 (2000mAh)

## 📁 파일 구조

```
firmware/
├── main.py           # 메인 펌웨어 프로그램
├── config.py         # 설정 파일
├── boot.py           # 부트스트랩 파일
├── test_firmware.py  # 테스트 스크립트
└── README.md         # 이 파일
```

## 🚀 설치 및 실행

### 1. 마이크로파이썬 설치
```bash
# ESP32 S3용 마이크로파이썬 펌웨어 다운로드
# https://micropython.org/download/esp32s3/
```

### 2. 펌웨어 업로드
```bash
# esptool을 사용하여 마이크로파이썬 펌웨어 업로드
esptool.py --chip esp32s3 --port COM3 --baud 460800 write_flash -z 0x0 esp32s3-20231005-v1.21.0.bin
```

### 3. 파일 업로드
```bash
# ampy 또는 rshell을 사용하여 파일 업로드
ampy --port COM3 put main.py
ampy --port COM3 put config.py
ampy --port COM3 put boot.py
```

### 4. 설정 수정
`config.py` 파일에서 다음 설정을 수정하세요:
```python
WIFI_CONFIG = {
    "ssid": "your_wifi_ssid",        # 실제 Wi-Fi SSID
    "password": "your_wifi_password", # 실제 Wi-Fi 비밀번호
}

SERVER_CONFIG = {
    "host": "192.168.1.100",         # 서버 IP 주소
    "port": 8888,                    # 서버 포트
}
```

## 🧪 테스트

### 펌웨어 테스트 실행
```python
# ESP32에서 직접 실행
import test_firmware
test_firmware.main()
```

### 개별 테스트
```python
# 특정 기능만 테스트
tester = test_firmware.FirmwareTester()
tester.test_sensors()
tester.test_led_matrix()
```

## 📡 통신 프로토콜

### 서버로 전송하는 메시지
```json
{
    "type": "status",
    "timestamp": 1699123456.789,
    "battery_level": 3.7,
    "motor_speed": 50,
    "encoder_counts": {
        "left": 1200,
        "right": 1180
    },
    "sensors": {
        "drop_detected": false,
        "obstacle_detected": true,
        "drop_distance": 950,
        "obstacle_distance": 450
    },
    "emergency_stop": false,
    "connected": true
}
```

### 서버에서 수신하는 명령
```json
{
    "type": "move",
    "left_speed": 50,
    "right_speed": 50
}
```

```json
{
    "type": "expression",
    "expression": "happy"
}
```

```json
{
    "type": "sound",
    "sound": "success",
    "duration": 500
}
```

## ⚙️ 설정 옵션

### 모터 설정
```python
MOTOR_CONFIG = {
    "pwm_frequency": 1000,    # PWM 주파수 (Hz)
    "max_speed": 100,         # 최대 속도 (-100 ~ 100)
    "min_speed": 10,          # 최소 동작 속도
    "acceleration": 5,        # 가속도
}
```

### 센서 설정
```python
SENSOR_CONFIG = {
    "drop_threshold": 800,           # 낙하 감지 임계값
    "obstacle_threshold": 600,       # 장애물 감지 임계값
    "update_interval": 0.1,          # 센서 업데이트 간격 (초)
    "battery_voltage_divider": 2.0   # 배터리 전압 분압 비율
}
```

### 안전 설정
```python
SAFETY_CONFIG = {
    "emergency_stop_enabled": True,  # 비상 정지 활성화
    "drop_protection": True,         # 낙하 방지 활성화
    "obstacle_avoidance": True,      # 장애물 회피 활성화
    "battery_low_threshold": 3.0,    # 배터리 부족 경고 (V)
    "battery_critical_threshold": 2.8 # 배터리 위험 (V)
}
```

## 🛡️ 안전 기능

### 자동 안전 시스템
- **낙하 방지**: 낙하 센서 감지 시 즉시 정지
- **장애물 회피**: 장애물 감지 시 정지 및 경고
- **배터리 모니터링**: 전압 부족 시 경고 및 안전 모드
- **비상 정지**: 서버 명령 또는 하드웨어 오류 시 즉시 정지

### 에러 처리
- **연결 끊김 감지**: 하트비트 타임아웃 시 재연결 시도
- **센서 오류 처리**: 센서 값 이상 시 안전 모드 전환
- **모터 오류 처리**: 모터 제어 오류 시 정지

## 🔍 디버깅

### 로그 출력
펌웨어는 시리얼 포트를 통해 상세한 로그를 출력합니다:
```
Deks 로봇 초기화 시작
모터 시스템 초기화
센서 시스템 초기화
Wi-Fi 연결 시도: your_wifi_ssid
Wi-Fi 연결 성공: ('192.168.1.100', '255.255.255.0', '192.168.1.1', '8.8.8.8')
서버 연결 시도: 192.168.1.100:8888
서버 연결 성공
```

### 테스트 결과 확인
```python
# 테스트 결과 파일 확인
import json
with open("test_results.json", "r") as f:
    results = json.load(f)
    print(json.dumps(results, indent=2))
```

## 📞 지원

### 문제 해결
1. **Wi-Fi 연결 실패**: SSID/비밀번호 확인
2. **서버 연결 실패**: IP 주소/포트 확인
3. **센서 오류**: 하드웨어 연결 상태 확인
4. **모터 동작 안함**: 전원 공급 및 드라이버 연결 확인

### 로그 확인
시리얼 모니터를 통해 실시간 로그를 확인할 수 있습니다:
- **보드레이트**: 115200 bps
- **포트**: COM3 (Windows) 또는 /dev/ttyUSB0 (Linux)

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**Deks 1.0 ESP32 펌웨어** - 안전하고 효율적인 로봇 제어를 위한 마이크로파이썬 기반 펌웨어
