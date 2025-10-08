"""
Deks 1.0 ESP32 부트스트랩 파일
시스템 시작 시 실행되는 초기화 코드
"""

import machine
import time
import network
from machine import Pin

def system_init():
    """시스템 초기화"""
    print("Deks 1.0 ESP32 시스템 초기화 시작")
    
    # 시스템 정보 출력
    print(f"CPU 주파수: {machine.freq()} Hz")
    print(f"메모리 여유: {gc.mem_free()} bytes")
    print(f"메모리 할당: {gc.mem_alloc()} bytes")
    
    # GPIO 초기화
    _init_gpio()
    
    # 네트워크 초기화
    _init_network()
    
    print("시스템 초기화 완료")

def _init_gpio():
    """GPIO 초기화"""
    print("GPIO 초기화")
    
    # 모든 핀을 안전한 상태로 초기화
    # 모터 핀들 (출력, LOW)
    motor_pins = [2, 3, 4, 5]
    for pin_num in motor_pins:
        pin = Pin(pin_num, Pin.OUT)
        pin.off()
    
    # 센서 핀들 (입력, 풀업)
    sensor_pins = [6, 7, 8, 9, 10, 11]
    for pin_num in sensor_pins:
        pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
    
    # 상태 LED (출력, OFF)
    status_led = Pin(14, Pin.OUT)
    status_led.off()
    
    print("GPIO 초기화 완료")

def _init_network():
    """네트워크 초기화"""
    print("네트워크 초기화")
    
    # Wi-Fi 비활성화 (main.py에서 활성화)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    
    print("네트워크 초기화 완료")

def check_hardware():
    """하드웨어 상태 점검"""
    print("하드웨어 상태 점검 시작")
    
    # 전원 상태 확인
    try:
        # 배터리 전압 측정 (GPIO 13)
        battery_adc = machine.ADC(machine.Pin(13))
        battery_adc.atten(machine.ADC.ATTN_11DB)
        battery_raw = battery_adc.read()
        battery_voltage = (battery_raw / 4095) * 3.3 * 2  # 2배 분압 가정
        
        print(f"배터리 전압: {battery_voltage:.2f}V")
        
        if battery_voltage < 2.8:
            print("경고: 배터리 전압이 낮습니다!")
            return False
        elif battery_voltage < 3.0:
            print("주의: 배터리 전압이 부족합니다.")
        
    except Exception as e:
        print(f"배터리 상태 확인 실패: {e}")
        return False
    
    # 센서 상태 확인
    try:
        # 센서 핀 상태 확인
        sensor_drop = machine.ADC(machine.Pin(10))
        sensor_obstacle = machine.ADC(machine.Pin(11))
        
        drop_value = sensor_drop.read()
        obstacle_value = sensor_obstacle.read()
        
        print(f"낙하 센서 값: {drop_value}")
        print(f"장애물 센서 값: {obstacle_value}")
        
    except Exception as e:
        print(f"센서 상태 확인 실패: {e}")
        return False
    
    print("하드웨어 상태 점검 완료")
    return True

def led_test():
    """LED 테스트 (GPIO 직접 제어)"""
    print("LED 테스트 시작")
    
    try:
        # LED 매트릭스 행 핀 초기화
        led_pins = [35, 36, 37, 38, 39, 40, 41, 42]
        row_pins = []
        
        for pin_num in led_pins:
            pin = machine.Pin(pin_num, machine.Pin.OUT)
            pin.off()
            row_pins.append(pin)
        
        print("LED 매트릭스 GPIO 핀 초기화 완료")
        
        # 간단한 테스트 패턴 표시
        print("테스트 패턴 표시 중...")
        for i in range(3):  # 3번 반복
            for row in range(8):
                row_pins[row].on()
                time.sleep_ms(50)
                row_pins[row].off()
                time.sleep_ms(50)
        
        # 모든 핀 끄기
        for pin in row_pins:
            pin.off()
        
        print("LED 테스트 완료")
            
    except Exception as e:
        print(f"LED 테스트 실패: {e}")

def buzzer_test():
    """버저 테스트"""
    print("버저 테스트 시작")
    
    try:
        buzzer = machine.PWM(machine.Pin(12))
        buzzer.freq(1000)
        buzzer.duty(512)
        time.sleep(0.5)
        buzzer.duty(0)
        print("버저 테스트 완료")
        
    except Exception as e:
        print(f"버저 테스트 실패: {e}")

def motor_test():
    """모터 테스트 (안전 모드)"""
    print("모터 테스트 시작 (안전 모드)")
    
    try:
        # PWM 핀 초기화
        motor_left_pwm = machine.PWM(machine.Pin(2))
        motor_right_pwm = machine.PWM(machine.Pin(4))
        motor_left_pwm.freq(1000)
        motor_right_pwm.freq(1000)
        
        # 방향 핀 초기화
        motor_left_dir = machine.Pin(3, machine.Pin.OUT)
        motor_right_dir = machine.Pin(5, machine.Pin.OUT)
        
        # 매우 낮은 속도로 짧은 테스트
        print("모터 테스트 실행 중...")
        motor_left_pwm.duty(50)   # 매우 낮은 속도
        motor_right_pwm.duty(50)
        time.sleep(0.1)           # 매우 짧은 시간
        
        # 모터 정지
        motor_left_pwm.duty(0)
        motor_right_pwm.duty(0)
        
        print("모터 테스트 완료")
        
    except Exception as e:
        print(f"모터 테스트 실패: {e}")

def run_startup_tests():
    """시작 시 테스트 실행"""
    print("시작 시 테스트 실행")
    
    # 하드웨어 상태 점검
    if not check_hardware():
        print("하드웨어 점검 실패 - 일부 기능이 제한될 수 있습니다")
    
    # LED 테스트
    led_test()
    
    # 버저 테스트
    buzzer_test()
    
    # 모터 테스트 (선택적)
    # motor_test()  # 안전을 위해 주석 처리
    
    print("시작 시 테스트 완료")

def main():
    """부트스트랩 메인 함수"""
    print("=" * 50)
    print("Deks 1.0 ESP32 부트스트랩")
    print("=" * 50)
    
    # 시스템 초기화
    system_init()
    
    # 시작 시 테스트 실행
    run_startup_tests()
    
    print("부트스트랩 완료 - main.py 실행 준비")
    print("=" * 50)

# 부트스트랩 실행
if __name__ == "__main__":
    main()
