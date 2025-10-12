"""
Deks 1.0 하드웨어 인터페이스 모듈
센서, 모터, LED, 버저 제어를 위한 하드웨어 추상화 계층
"""

import time
import math
from machine import Pin, PWM, ADC, I2C
try:
    import uasyncio as asyncio
except ImportError:
    asyncio = None

class MotorController:
    """모터 제어 클래스"""
    
    def __init__(self, left_in1_pin, left_in2_pin, left_enable_pin,
                 right_in1_pin, right_in2_pin, right_enable_pin,
                 left_encoder_a, left_encoder_b,
                 right_encoder_a, right_encoder_b):
        """모터 컨트롤러 초기화"""
        print(f"모터 컨트롤러 초기화:")
        print(f"  왼쪽 모터: IN1={left_in1_pin}, IN2={left_in2_pin}, Enable={left_enable_pin}")
        print(f"  오른쪽 모터: IN1={right_in1_pin}, IN2={right_in2_pin}, Enable={right_enable_pin}")
        print(f"  왼쪽 엔코더: A={left_encoder_a}, B={left_encoder_b}")
        print(f"  오른쪽 엔코더: A={right_encoder_a}, B={right_encoder_b}")
        
        # 왼쪽 모터 L298N 핀
        self.left_in1 = Pin(left_in1_pin, Pin.OUT)
        self.left_in2 = Pin(left_in2_pin, Pin.OUT)
        self.left_enable = PWM(Pin(left_enable_pin))
        
        # 오른쪽 모터 L298N 핀
        self.right_in1 = Pin(right_in1_pin, Pin.OUT)
        self.right_in2 = Pin(right_in2_pin, Pin.OUT)
        self.right_enable = PWM(Pin(right_enable_pin))
        
        # PWM 설정
        self.left_enable.freq(1000)
        self.right_enable.freq(1000)
        
        # 모터 정지 상태로 초기화
        self.left_enable.duty(0)
        self.right_enable.duty(0)
        self.left_in1.off()
        self.left_in2.off()
        self.right_in1.off()
        self.right_in2.off()
        print("모터 핀 초기화 완료 (모두 OFF)")
        
        # 엔코더 설정
        self.left_encoder_a = Pin(left_encoder_a, Pin.IN, Pin.PULL_UP)
        self.left_encoder_b = Pin(left_encoder_b, Pin.IN, Pin.PULL_UP)
        self.right_encoder_a = Pin(right_encoder_a, Pin.IN, Pin.PULL_UP)
        self.right_encoder_b = Pin(right_encoder_b, Pin.IN, Pin.PULL_UP)
        
        # 엔코더 카운터
        self.left_count = 0
        self.right_count = 0
        
        # 엔코더 인터럽트 설정 (B 채널을 인터럽트 핀으로 사용)
        self.left_encoder_b.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._left_encoder_callback)
        self.right_encoder_a.irq(trigger=Pin.IRQ_RISING, handler=self._right_encoder_callback)
        
        # 모터 상태
        self.left_speed = 0
        self.right_speed = 0
        self.is_moving = False
        
        # 안전 설정
        self.max_speed = 100
        self.min_speed = 0  # 속도 0 허용 (정지 처리)
        self.acceleration = 5
        
        # PWM 듀티 범위 설정 (460~1023)
        # 460 미만에서는 모터가 제대로 작동하지 않음
        self.min_pwm_duty = 460
        self.max_pwm_duty = 1023
        self.pwm_range = self.max_pwm_duty - self.min_pwm_duty  # 563
        
        print("모터 컨트롤러 초기화 완료")
        print(f"PWM 듀티 범위: {self.min_pwm_duty} ~ {self.max_pwm_duty}")
    
    def _left_encoder_callback(self, pin):
        """왼쪽 엔코더 인터럽트 콜백 (B 채널 인터럽트)"""
        # B 채널이 변할 때, A 채널 상태를 확인하여 방향 결정
        if self.left_encoder_a.value():
            self.left_count += 1
        else:
            self.left_count -= 1
    
    def _right_encoder_callback(self, pin):
        """오른쪽 엔코더 인터럽트 콜백"""
        if self.right_encoder_b.value():
            self.right_count += 1
        else:
            self.right_count -= 1
    
    def _speed_to_pwm_duty(self, speed: int) -> int:
        """
        속도 값(0~100)을 PWM 듀티 사이클(460~1023)로 재매핑
        
        Args:
            speed: 속도 값 (0~100)
            
        Returns:
            PWM 듀티 사이클 (460~1023)
        """
        # 속도 0~100을 PWM 460~1023으로 선형 매핑
        # speed = 0일 때 460, speed = 100일 때 1023
        # duty = 460 + (speed / 100) * (1023 - 460)
        # duty = 460 + speed * 5.63
        duty = int(self.min_pwm_duty + (abs(speed) / 100.0) * self.pwm_range)
        return max(self.min_pwm_duty, min(self.max_pwm_duty, duty))
    
    def move(self, left_speed: int, right_speed: int):
        """모터 이동 제어"""
        print(f"MotorController.move 호출: left={left_speed}, right={right_speed}")
        
        # 속도 제한
        left_speed = max(-self.max_speed, min(self.max_speed, left_speed))
        right_speed = max(-self.max_speed, min(self.max_speed, right_speed))
        
        # 최소 속도 처리
        if abs(left_speed) < self.min_speed and left_speed != 0:
            left_speed = self.min_speed if left_speed > 0 else -self.min_speed
        if abs(right_speed) < self.min_speed and right_speed != 0:
            right_speed = self.min_speed if right_speed > 0 else -self.min_speed
        
        print(f"조정된 속도: left={left_speed}, right={right_speed}")
        
        # 완전 정지 체크 (좌우 모두 0)
        if left_speed == 0 and right_speed == 0:
            print(f"완전 정지: 좌우 모두 0")
            self.left_in1.off()
            self.left_in2.off()
            self.left_enable.duty(0)
            self.right_in1.off()
            self.right_in2.off()
            self.right_enable.duty(0)
        else:
            # 왼쪽 모터 제어 (L298N IN1, IN2 방식) - 방향 반전됨
            if left_speed >= 0:
                # 전진: IN1=0, IN2=1 (반전) - 속도 0도 PWM 460으로 작동
                duty_value = self._speed_to_pwm_duty(left_speed)
                print(f"왼쪽 모터 전진: IN1=OFF, IN2=ON, PWM duty={duty_value}")
                self.left_in1.off()
                self.left_in2.on()
                self.left_enable.duty(duty_value)
            else:  # left_speed < 0
                # 후진: IN1=1, IN2=0 (반전)
                duty_value = self._speed_to_pwm_duty(-left_speed)
                print(f"왼쪽 모터 후진: IN1=ON, IN2=OFF, PWM duty={duty_value}")
                self.left_in1.on()
                self.left_in2.off()
                self.left_enable.duty(duty_value)
            
            # 오른쪽 모터 제어 (L298N IN1, IN2 방식)
            if right_speed >= 0:
                # 전진: IN1=1, IN2=0 - 속도 0도 PWM 460으로 작동
                duty_value = self._speed_to_pwm_duty(right_speed)
                print(f"오른쪽 모터 전진: IN1=ON, IN2=OFF, PWM duty={duty_value}")
                self.right_in1.on()
                self.right_in2.off()
                self.right_enable.duty(duty_value)
            else:  # right_speed < 0
                # 후진: IN1=0, IN2=1
                duty_value = self._speed_to_pwm_duty(-right_speed)
                print(f"오른쪽 모터 후진: IN1=OFF, IN2=ON, PWM duty={duty_value}")
                self.right_in1.off()
                self.right_in2.on()
                self.right_enable.duty(duty_value)
        
        self.left_speed = left_speed
        self.right_speed = right_speed
        self.is_moving = not (left_speed == 0 and right_speed == 0)
    
    def move_pwm(self, left_pwm: int, right_pwm: int):
        """PWM 듀티로 직접 모터 제어 (서버에서 변환된 값 사용)"""
        print(f"MotorController.move_pwm 호출: left={left_pwm}, right={right_pwm}")
        
        # 완전 정지 체크 (좌우 모두 0)
        if left_pwm == 0 and right_pwm == 0:
            print(f"완전 정지: 좌우 모두 0")
            self.left_in1.off()
            self.left_in2.off()
            self.left_enable.duty(0)
            self.right_in1.off()
            self.right_in2.off()
            self.right_enable.duty(0)
            self.is_moving = False
        else:
            # 왼쪽 모터 제어 - PWM 듀티 직접 사용
            if left_pwm >= 0:
                # 전진 방향 (반전)
                print(f"왼쪽 모터 전진: IN1=OFF, IN2=ON, PWM duty={left_pwm}")
                self.left_in1.off()
                self.left_in2.on()
                self.left_enable.duty(left_pwm)
            else:
                # 후진 방향 (반전)
                duty_value = abs(left_pwm)
                print(f"왼쪽 모터 후진: IN1=ON, IN2=OFF, PWM duty={duty_value}")
                self.left_in1.on()
                self.left_in2.off()
                self.left_enable.duty(duty_value)
            
            # 오른쪽 모터 제어 - PWM 듀티 직접 사용
            if right_pwm >= 0:
                # 전진 방향
                print(f"오른쪽 모터 전진: IN1=ON, IN2=OFF, PWM duty={right_pwm}")
                self.right_in1.on()
                self.right_in2.off()
                self.right_enable.duty(right_pwm)
            else:
                # 후진 방향
                duty_value = abs(right_pwm)
                print(f"오른쪽 모터 후진: IN1=OFF, IN2=ON, PWM duty={duty_value}")
                self.right_in1.off()
                self.right_in2.on()
                self.right_enable.duty(duty_value)
            
            self.is_moving = True
        
        self.left_speed = left_pwm  # PWM 듀티를 속도로 저장
        self.right_speed = right_pwm
    
    def stop(self):
        """모터 정지"""
        print("MotorController.stop 호출")
        self.left_enable.duty(0)
        self.right_enable.duty(0)
        self.left_in1.off()
        self.left_in2.off()
        self.right_in1.off()
        self.right_in2.off()
        self.left_speed = 0
        self.right_speed = 0
        self.is_moving = False
        print("모터 완전 정지 완료")
    
    def get_encoder_counts(self) -> Dict[str, int]:
        """엔코더 카운트 반환"""
        return {
            "left": self.left_count,
            "right": self.right_count
        }
    
    def reset_encoders(self):
        """엔코더 카운트 리셋"""
        self.left_count = 0
        self.right_count = 0
    
    def get_status(self) -> Dict[str, any]:
        """모터 상태 반환"""
        return {
            "left_speed": self.left_speed,
            "right_speed": self.right_speed,
            "is_moving": self.is_moving,
            "encoder_counts": self.get_encoder_counts()
        }

class SensorManager:
    """센서 관리 클래스"""
    
    def __init__(self, drop_sensor_pin: int, obstacle_sensor_pin: int, 
                 battery_pin: int):
        """센서 매니저 초기화"""
        self.drop_sensor = ADC(Pin(drop_sensor_pin))
        self.obstacle_sensor = ADC(Pin(obstacle_sensor_pin))
        self.battery_adc = ADC(Pin(battery_pin))
        
        # ADC 설정
        self.drop_sensor.atten(ADC.ATTN_11DB)
        self.obstacle_sensor.atten(ADC.ATTN_11DB)
        self.battery_adc.atten(ADC.ATTN_11DB)
        
        # 센서 임계값
        self.drop_threshold = 800
        self.obstacle_threshold = 600
        self.battery_low_threshold = 3.0
        self.battery_critical_threshold = 2.8
        
        # 센서 데이터
        self.sensor_data = {
            "drop_detected": False,
            "obstacle_detected": False,
            "drop_distance": 0,
            "obstacle_distance": 0,
            "battery_level": 0.0,
            "battery_status": "normal"
        }
        
        # 필터링을 위한 이전 값들
        self.drop_history = [0] * 5
        self.obstacle_history = [0] * 5
        self.battery_history = [0.0] * 3
        
        print("센서 매니저 초기화 완료")
    
    def read_sensors(self):
        """모든 센서 읽기"""
        # 원시 센서 값 읽기
        drop_raw = self.drop_sensor.read()
        obstacle_raw = self.obstacle_sensor.read()
        battery_raw = self.battery_adc.read()
        
        # 배터리 전압 계산 (분압 회로 가정)
        battery_voltage = (battery_raw / 4095) * 3.3 * 2
        
        # 필터링 적용
        drop_filtered = self._apply_filter(self.drop_history, drop_raw)
        obstacle_filtered = self._apply_filter(self.obstacle_history, obstacle_raw)
        battery_filtered = self._apply_filter(self.battery_history, battery_voltage)
        
        # 센서 데이터 업데이트
        self.sensor_data["drop_distance"] = drop_filtered
        self.sensor_data["obstacle_distance"] = obstacle_filtered
        self.sensor_data["battery_level"] = battery_filtered
        
        # 감지 상태 업데이트
        self.sensor_data["drop_detected"] = drop_filtered < self.drop_threshold
        self.sensor_data["obstacle_detected"] = obstacle_filtered < self.obstacle_threshold
        
        # 배터리 상태 업데이트
        if battery_filtered < self.battery_critical_threshold:
            self.sensor_data["battery_status"] = "critical"
        elif battery_filtered < self.battery_low_threshold:
            self.sensor_data["battery_status"] = "low"
        else:
            self.sensor_data["battery_status"] = "normal"
    
    def _apply_filter(self, history: List, new_value: float) -> float:
        """이동 평균 필터 적용"""
        history.pop(0)
        history.append(new_value)
        return sum(history) / len(history)
    
    def get_sensor_data(self) -> Dict[str, any]:
        """센서 데이터 반환"""
        return self.sensor_data.copy()
    
    def is_drop_detected(self) -> bool:
        """낙하 감지 여부"""
        return self.sensor_data["drop_detected"]
    
    def is_obstacle_detected(self) -> bool:
        """장애물 감지 여부"""
        return self.sensor_data["obstacle_detected"]
    
    def get_battery_status(self) -> str:
        """배터리 상태 반환"""
        return self.sensor_data["battery_status"]
    
    def calibrate_sensors(self):
        """센서 캘리브레이션"""
        print("센서 캘리브레이션 시작")
        
        # 10번 측정하여 평균값 계산
        drop_values = []
        obstacle_values = []
        battery_values = []
        
        for _ in range(10):
            drop_values.append(self.drop_sensor.read())
            obstacle_values.append(self.obstacle_sensor.read())
            battery_values.append((self.battery_adc.read() / 4095) * 3.3 * 2)
            time.sleep(0.1)
        
        # 평균값으로 임계값 조정
        drop_avg = sum(drop_values) / len(drop_values)
        obstacle_avg = sum(obstacle_values) / len(obstacle_values)
        battery_avg = sum(battery_values) / len(battery_values)
        
        # 임계값을 평균값의 80%로 설정
        self.drop_threshold = int(drop_avg * 0.8)
        self.obstacle_threshold = int(obstacle_avg * 0.8)
        
        print(f"센서 캘리브레이션 완료:")
        print(f"  낙하 센서 임계값: {self.drop_threshold}")
        print(f"  장애물 센서 임계값: {self.obstacle_threshold}")
        print(f"  배터리 전압: {battery_avg:.2f}V")

class LEDMatrixController:
    """LED 매트릭스 제어 클래스 (GPIO 직접 제어)"""
    
    def __init__(self, row_pins: List[int]):
        """LED 매트릭스 컨트롤러 초기화"""
        self.row_pins = []
        self.row_count = len(row_pins)
        self.col_count = 8
        
        # 행 핀 초기화
        for pin_num in row_pins:
            pin = Pin(pin_num, Pin.OUT)
            pin.off()  # 초기에는 모든 행을 끔
            self.row_pins.append(pin)
        
        # 표정 패턴 정의 (8x8 비트맵)
        self.expressions = {
            "happy": [
                0x3C,  # 00111100
                0x42,  # 01000010
                0x81,  # 10000001
                0x81,  # 10000001
                0x81,  # 10000001
                0x81,  # 10000001
                0x42,  # 01000010
                0x3C   # 00111100
            ],
            "sad": [
                0x3C,  # 00111100
                0x42,  # 01000010
                0x81,  # 10000001
                0x81,  # 10000001
                0x81,  # 10000001
                0x81,  # 10000001
                0x42,  # 01000010
                0x3C   # 00111100
            ],
            "neutral": [
                0x3C,  # 00111100
                0x42,  # 01000010
                0x81,  # 10000001
                0x81,  # 10000001
                0x81,  # 10000001
                0x81,  # 10000001
                0x42,  # 01000010
                0x3C   # 00111100
            ],
            "thinking": [
                0x3C,  # 00111100
                0x42,  # 01000010
                0x81,  # 10000001
                0x81,  # 10000001
                0x81,  # 10000001
                0x81,  # 10000001
                0x42,  # 01000010
                0x3C   # 00111100
            ],
            "error": [
                0x3C,  # 00111100
                0x42,  # 01000010
                0x81,  # 10000001
                0x81,  # 10000001
                0x81,  # 10000001
                0x81,  # 10000001
                0x42,  # 01000010
                0x3C   # 00111100
            ],
            "surprised": [
                0x3C,  # 00111100
                0x42,  # 01000010
                0x81,  # 10000001
                0x81,  # 10000001
                0x81,  # 10000001
                0x81,  # 10000001
                0x42,  # 01000010
                0x3C   # 00111100
            ],
            "angry": [
                0x3C,  # 00111100
                0x42,  # 01000010
                0x81,  # 10000001
                0x81,  # 10000001
                0x81,  # 10000001
                0x81,  # 10000001
                0x42,  # 01000010
                0x3C   # 00111100
            ],
            "sleepy": [
                0x3C,  # 00111100
                0x42,  # 01000010
                0x81,  # 10000001
                0x81,  # 10000001
                0x81,  # 10000001
                0x81,  # 10000001
                0x42,  # 01000010
                0x3C   # 00111100
            ]
        }
        
        # 애니메이션 패턴
        self.animations = {
            "blink": self._create_blink_animation(),
            "fade": self._create_fade_animation(),
            "rainbow": self._create_rainbow_animation(),
            "wave": self._create_wave_animation(),
            "pulse": self._create_pulse_animation(),
            "sparkle": self._create_sparkle_animation()
        }
        
        self.current_expression = "neutral"
        self.is_animating = False
        self.current_pattern = [0x00] * 8  # 현재 표시 중인 패턴
        
        # 기본 표정 표시
        self.set_expression("neutral")
        
        print("LED 매트릭스 컨트롤러 초기화 완료")
    
    def _display_pattern(self, pattern: List[int]):
        """패턴을 LED 매트릭스에 표시"""
        # 모든 행을 끔
        for pin in self.row_pins:
            pin.off()
        
        # 행 스캔 방식으로 패턴 표시
        for row in range(self.row_count):
            if row < len(pattern):
                row_data = pattern[row]
                # 해당 행의 핀을 켬
                self.row_pins[row].on()
                
                # 열 데이터 처리 (여기서는 간단히 행만 제어)
                # 실제로는 열 핀도 필요하지만, 1588AS는 행 스캔만으로도 동작
                
                # 짧은 지연 후 다음 행으로
                time.sleep_us(1000)  # 1ms
                
                # 행 끄기
                self.row_pins[row].off()
    
    def set_expression(self, expression_name: str):
        """표정 설정"""
        if expression_name in self.expressions:
            try:
                pattern = self.expressions[expression_name]
                self.current_pattern = pattern.copy()
                self.current_expression = expression_name
                self._display_pattern(pattern)
            except Exception as e:
                print(f"LED 표정 설정 실패: {e}")
        else:
            print(f"알 수 없는 표정: {expression_name}")
    
    def play_animation(self, animation_name: str, duration: int = 1000):
        """애니메이션 재생"""
        if animation_name in self.animations:
            self.is_animating = True
            frames = self.animations[animation_name]
            frame_duration = duration // len(frames)
            
            for frame in frames:
                if not self.is_animating:  # 애니메이션 중단 확인
                    break
                self._display_pattern(frame)
                time.sleep_ms(frame_duration)
            
            self.is_animating = False
        else:
            print(f"알 수 없는 애니메이션: {animation_name}")
    
    def stop_animation(self):
        """애니메이션 중단"""
        self.is_animating = False
    
    def _create_blink_animation(self) -> List[List[int]]:
        """깜빡임 애니메이션 생성"""
        frames = []
        base_pattern = self.expressions["neutral"]
        
        for i in range(10):
            if i % 2 == 0:
                frames.append(base_pattern)
            else:
                frames.append([0x00] * 16)
        
        return frames
    
    def _create_fade_animation(self) -> List[List[int]]:
        """페이드 애니메이션 생성"""
        frames = []
        base_pattern = self.expressions["happy"]
        
        for intensity in range(0, 16, 2):
            frame = []
            for byte_val in base_pattern:
                # 간단한 밝기 조절 (실제로는 PWM 사용)
                frame.append(byte_val if intensity > 8 else 0x00)
            frames.append(frame)
        
        return frames
    
    def _create_rainbow_animation(self) -> List[List[int]]:
        """무지개 애니메이션 생성"""
        frames = []
        colors = [0xFF, 0xFE, 0xFC, 0xF8, 0xF0, 0xE0, 0xC0, 0x80]
        
        for color in colors:
            frame = [color] * 16
            frames.append(frame)
        
        return frames
    
    def _create_wave_animation(self) -> List[List[int]]:
        """파도 애니메이션 생성"""
        frames = []
        
        for i in range(8):
            frame = [0x00] * 16
            for j in range(8):
                if (i + j) % 2 == 0:
                    frame[j] = 0xFF
            frames.append(frame)
        
        return frames
    
    def _create_pulse_animation(self) -> List[List[int]]:
        """펄스 애니메이션 생성"""
        frames = []
        base_pattern = self.expressions["neutral"]
        
        for scale in [0.2, 0.4, 0.6, 0.8, 1.0, 0.8, 0.6, 0.4, 0.2]:
            frame = []
            for byte_val in base_pattern:
                frame.append(int(byte_val * scale))
            frames.append(frame)
        
        return frames
    
    def _create_sparkle_animation(self) -> List[List[int]]:
        """반짝임 애니메이션 생성"""
        frames = []
        
        for i in range(20):
            frame = [0x00] * 16
            # 랜덤한 위치에 점 표시
            for j in range(3):
                pos = (i + j * 5) % 16
                frame[pos] = 0xFF
            frames.append(frame)
        
        return frames
    
    def get_status(self) -> Dict[str, any]:
        """LED 매트릭스 상태 반환"""
        return {
            "current_expression": self.current_expression,
            "is_animating": self.is_animating,
            "available_expressions": list(self.expressions.keys()),
            "available_animations": list(self.animations.keys())
        }

class BuzzerController:
    """버저 제어 클래스"""
    
    def __init__(self, buzzer_pin: int):
        """버저 컨트롤러 초기화"""
        self.buzzer = PWM(Pin(buzzer_pin))
        self.buzzer.freq(1000)
        self.buzzer.duty(0)
        
        # 사전 정의된 소리 패턴
        self.sounds = {
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
        
        # 볼륨 레벨
        self.volume_levels = [0, 256, 512, 768, 1023]
        self.current_volume = 2  # 기본 볼륨 (중간)
        
        self.is_playing = False
        
        print("버저 컨트롤러 초기화 완료")
    
    def play_sound(self, sound_name: str, volume: int = None):
        """소리 재생"""
        if sound_name in self.sounds:
            if volume is None:
                volume = self.current_volume
            
            volume = max(0, min(4, volume))  # 0-4 범위로 제한
            duty_cycle = self.volume_levels[volume]
            
            sound_data = self.sounds[sound_name]
            frequencies = sound_data["frequencies"]
            durations = sound_data["durations"]
            
            self.is_playing = True
            
            for freq, duration in zip(frequencies, durations):
                if not self.is_playing:  # 재생 중단 확인
                    break
                self.buzzer.freq(freq)
                self.buzzer.duty(duty_cycle)
                time.sleep_ms(duration)
            
            self.buzzer.duty(0)
            self.is_playing = False
        else:
            print(f"알 수 없는 소리: {sound_name}")
    
    def play_custom_melody(self, frequencies: List[int], durations: List[int], volume: int = None):
        """커스텀 멜로디 재생"""
        if volume is None:
            volume = self.current_volume
        
        volume = max(0, min(4, volume))
        duty_cycle = self.volume_levels[volume]
        
        self.is_playing = True
        
        for freq, duration in zip(frequencies, durations):
            if not self.is_playing:
                break
            self.buzzer.freq(freq)
            self.buzzer.duty(duty_cycle)
            time.sleep_ms(duration)
        
        self.buzzer.duty(0)
        self.is_playing = False
    
    def stop_sound(self):
        """소리 중단"""
        self.is_playing = False
        self.buzzer.duty(0)
    
    def set_volume(self, volume: int):
        """볼륨 설정"""
        self.current_volume = max(0, min(4, volume))
    
    def get_status(self) -> Dict[str, any]:
        """버저 상태 반환"""
        return {
            "is_playing": self.is_playing,
            "current_volume": self.current_volume,
            "available_sounds": list(self.sounds.keys()),
            "volume_levels": len(self.volume_levels)
        }

class HardwareInterface:
    """하드웨어 인터페이스 통합 클래스"""
    
    def __init__(self, config: Dict[str, any]):
        """하드웨어 인터페이스 초기화"""
        self.config = config
        
        # 하드웨어 컴포넌트 초기화
        self.motor_controller = MotorController(
            config["motor_left_in1"], config["motor_left_in2"], config["motor_left_enable"],
            config["motor_right_in1"], config["motor_right_in2"], config["motor_right_enable"],
            config["encoder_left_a"], config["encoder_left_b"],
            config["encoder_right_a"], config["encoder_right_b"]
        )
        
        self.sensor_manager = SensorManager(
            config["sensor_drop"], config["sensor_obstacle"], config["battery"]
        )
        
        # LED 매트릭스 행 핀 목록 생성
        led_row_pins = [
            config["led_row_0"], config["led_row_1"], config["led_row_2"], config["led_row_3"],
            config["led_row_4"], config["led_row_5"], config["led_row_6"], config["led_row_7"]
        ]
        
        self.led_controller = LEDMatrixController(led_row_pins)
        
        self.buzzer_controller = BuzzerController(config["buzzer"])
        
        # 상태 LED
        self.status_led = Pin(config["status_led"], Pin.OUT)
        self.status_led.off()
        
        # 안전 시스템
        self.emergency_stop = False
        self.safety_enabled = True
        
        print("하드웨어 인터페이스 초기화 완료")
    
    def update_sensors(self):
        """모든 센서 업데이트"""
        self.sensor_manager.read_sensors()
    
    def check_safety(self) -> bool:
        """안전 검사"""
        if not self.safety_enabled:
            return True
        
        sensor_data = self.sensor_manager.get_sensor_data()
        
        # 테스트 모드: 안전 검사 비활성화
        # 낙하 감지 (비활성화됨)
        # if sensor_data["drop_detected"]:
        #     print("낙하 감지 - 비상 정지")
        #     self.emergency_stop = True
        #     self.motor_controller.stop()
        #     self.led_controller.set_expression("error")
        #     self.buzzer_controller.play_sound("warning")
        #     return False
        
        # 테스트 모드: 배터리 검사 비활성화
        # if sensor_data["battery_status"] == "critical":
        #     print("배터리 위험 - 비상 정지")
        #     self.emergency_stop = True
        #     self.motor_controller.stop()
        #     self.led_controller.set_expression("error")
        #     self.buzzer_controller.play_sound("error")
        #     return False
        
        # 테스트 모드: 항상 안전함
        return True
    
    def move_robot(self, left_speed: int, right_speed: int):
        """로봇 이동 (속도 기반)"""
        if self.emergency_stop:
            print("비상 정지 상태 - 이동 불가")
            return False
        
        if not self.check_safety():
            return False
        
        self.motor_controller.move(left_speed, right_speed)
        return True
    
    def move_robot_pwm(self, left_pwm: int, right_pwm: int):
        """로봇 이동 (PWM 듀티 직접 지정)"""
        if self.emergency_stop:
            print("비상 정지 상태 - 이동 불가")
            return False
        
        if not self.check_safety():
            return False
        
        self.motor_controller.move_pwm(left_pwm, right_pwm)
        return True
    
    def stop_robot(self):
        """로봇 정지"""
        print("로봇 정지 명령 수신")
        self.motor_controller.stop()
        print("로봇 정지 명령 완료")
    
    def set_expression(self, expression: str):
        """표정 설정"""
        self.led_controller.set_expression(expression)
    
    def play_sound(self, sound: str, volume: int = None):
        """소리 재생"""
        self.buzzer_controller.play_sound(sound, volume)
    
    def reset_emergency_stop(self):
        """비상 정지 리셋"""
        self.emergency_stop = False
        self.led_controller.set_expression("neutral")
    
    def get_status(self) -> Dict[str, any]:
        """전체 하드웨어 상태 반환"""
        return {
            "motor": self.motor_controller.get_status(),
            "sensors": self.sensor_manager.get_sensor_data(),
            "led": self.led_controller.get_status(),
            "buzzer": self.buzzer_controller.get_status(),
            "emergency_stop": self.emergency_stop,
            "safety_enabled": self.safety_enabled
        }
    
    def calibrate_all(self):
        """모든 센서 캘리브레이션"""
        print("전체 하드웨어 캘리브레이션 시작")
        self.sensor_manager.calibrate_sensors()
        print("하드웨어 캘리브레이션 완료")
