"""
Deks 1.0 ESP32 펌웨어 설정 파일
하드웨어별 설정 및 네트워크 정보 관리
"""

# 네트워크 설정
WIFI_CONFIG = {
    "ssid": "your_wifi_ssid",        # 실제 Wi-Fi SSID로 변경
    "password": "your_wifi_password", # 실제 Wi-Fi 비밀번호로 변경
    "timeout": 10                    # 연결 타임아웃 (초)
}

# 서버 설정
SERVER_CONFIG = {
    "host": "192.168.1.100",         # 서버 IP 주소 (실제 환경에 맞게 수정)
    "port": 8888,                    # 서버 포트
    "timeout": 5,                    # 소켓 타임아웃 (초)
    "heartbeat_interval": 1.0,       # 하트비트 전송 간격 (초)
    "heartbeat_timeout": 5.0         # 하트비트 타임아웃 (초)
}

# GPIO 핀 설정
GPIO_CONFIG = {
    # 모터 제어 (L298N)
    "motor_left_pwm": 2,
    "motor_left_dir": 3,
    "motor_right_pwm": 4,
    "motor_right_dir": 5,
    
    # 엔코더
    "encoder_left_a": 6,
    "encoder_left_b": 7,
    "encoder_right_a": 8,
    "encoder_right_b": 9,
    
    # 센서
    "sensor_drop": 10,       # 낙하 방지 센서
    "sensor_obstacle": 11,   # 장애물 감지 센서
    
    # LED 매트릭스 (I2C)
    "led_sda": 35,
    "led_scl": 36,
    
    # 버저
    "buzzer": 12,
    
    # 배터리 모니터링
    "battery": 13,
    
    # 상태 LED
    "status_led": 14
}

# 모터 설정
MOTOR_CONFIG = {
    "pwm_frequency": 1000,           # PWM 주파수 (Hz)
    "max_speed": 100,                # 최대 속도 (-100 ~ 100)
    "min_speed": 10,                 # 최소 동작 속도
    "acceleration": 5,               # 가속도 (속도 변화량)
    "encoder_resolution": 20         # 엔코더 해상도 (펄스/회전)
}

# 센서 설정
SENSOR_CONFIG = {
    "drop_threshold": 800,           # 낙하 감지 임계값
    "obstacle_threshold": 600,       # 장애물 감지 임계값
    "update_interval": 0.1,          # 센서 업데이트 간격 (초)
    "battery_voltage_divider": 2.0   # 배터리 전압 분압 비율
}

# LED 매트릭스 설정
LED_CONFIG = {
    "i2c_address": 0x70,             # I2C 주소
    "i2c_frequency": 400000,         # I2C 주파수 (Hz)
    "brightness": 8,                 # 밝기 (0-15)
    "animation_speed": 100           # 애니메이션 속도 (ms)
}

# 버저 설정
BUZZER_CONFIG = {
    "default_frequency": 1000,       # 기본 주파수 (Hz)
    "default_duty": 512,             # 기본 듀티 사이클 (0-1023)
    "volume_levels": [0, 256, 512, 768, 1023]  # 볼륨 레벨
}

# 안전 설정
SAFETY_CONFIG = {
    "emergency_stop_enabled": True,  # 비상 정지 활성화
    "drop_protection": True,         # 낙하 방지 활성화
    "obstacle_avoidance": True,      # 장애물 회피 활성화
    "battery_low_threshold": 3.0,    # 배터리 부족 경고 임계값 (V)
    "battery_critical_threshold": 2.8 # 배터리 위험 임계값 (V)
}

# 로깅 설정
LOG_CONFIG = {
    "enabled": True,                 # 로깅 활성화
    "level": "INFO",                 # 로그 레벨 (DEBUG, INFO, WARNING, ERROR)
    "max_log_size": 10000,           # 최대 로그 크기 (바이트)
    "log_rotation": True             # 로그 로테이션 활성화
}

# 표정 패턴 정의
EXPRESSION_PATTERNS = {
    "happy": [
        0x3C, 0x42, 0x81, 0x81, 0x81, 0x81, 0x42, 0x3C,
        0x00, 0x00, 0x24, 0x00, 0x00, 0x24, 0x00, 0x00
    ],
    "sad": [
        0x3C, 0x42, 0x81, 0x81, 0x81, 0x81, 0x42, 0x3C,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ],
    "neutral": [
        0x3C, 0x42, 0x81, 0x81, 0x81, 0x81, 0x42, 0x3C,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ],
    "thinking": [
        0x3C, 0x42, 0x81, 0x81, 0x81, 0x81, 0x42, 0x3C,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ],
    "error": [
        0x3C, 0x42, 0x81, 0x81, 0x81, 0x81, 0x42, 0x3C,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ],
    "surprised": [
        0x3C, 0x42, 0x81, 0x81, 0x81, 0x81, 0x42, 0x3C,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ],
    "angry": [
        0x3C, 0x42, 0x81, 0x81, 0x81, 0x81, 0x42, 0x3C,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ],
    "sleepy": [
        0x3C, 0x42, 0x81, 0x81, 0x81, 0x81, 0x42, 0x3C,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
}

# 소리 패턴 정의
SOUND_PATTERNS = {
    "start": {
        "frequencies": [1000, 1500, 2000],
        "durations": [200, 200, 200]
    },
    "success": {
        "frequencies": [2000, 1500, 2000],
        "durations": [300, 300, 300]
    },
    "error": {
        "frequencies": [500, 500, 500],
        "durations": [200, 200, 200]
    },
    "warning": {
        "frequencies": [1000, 500, 1000],
        "durations": [250, 250, 250]
    },
    "thinking": {
        "frequencies": [800, 1200, 800],
        "durations": [150, 150, 150]
    },
    "notification": {
        "frequencies": [1500, 1000],
        "durations": [100, 100]
    },
    "complete": {
        "frequencies": [2000, 1800, 1600, 1400, 1200],
        "durations": [100, 100, 100, 100, 200]
    }
}

# 명령 타입 정의
COMMAND_TYPES = {
    "MOVE": "move",
    "STOP": "stop",
    "EXPRESSION": "expression",
    "SOUND": "sound",
    "EMERGENCY_STOP": "emergency_stop",
    "RESET": "reset",
    "STATUS": "status",
    "CONFIG": "config"
}

# 응답 타입 정의
RESPONSE_TYPES = {
    "STATUS": "status",
    "ERROR": "error",
    "SUCCESS": "success",
    "SENSOR_DATA": "sensor_data",
    "HEARTBEAT": "heartbeat"
}
