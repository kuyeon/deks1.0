"""
Deks 1.0 ESP32 펌웨어 테스트 스크립트
개발 및 디버깅용 테스트 코드
"""

import time
import json
from machine import Pin, PWM, ADC, I2C
import uasyncio as asyncio

class FirmwareTester:
    """펌웨어 테스트 클래스"""
    
    def __init__(self):
        print("펌웨어 테스트 초기화")
        self.test_results = {}
    
    def test_gpio_pins(self):
        """GPIO 핀 테스트"""
        print("GPIO 핀 테스트 시작")
        
        test_pins = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 35, 36]
        results = {}
        
        for pin_num in test_pins:
            try:
                if pin_num in [2, 3, 4, 5, 12, 14]:  # 출력 핀
                    pin = Pin(pin_num, Pin.OUT)
                    pin.on()
                    time.sleep(0.1)
                    pin.off()
                    results[pin_num] = "OK"
                else:  # 입력 핀
                    pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
                    value = pin.value()
                    results[pin_num] = f"OK (값: {value})"
                    
            except Exception as e:
                results[pin_num] = f"ERROR: {e}"
        
        self.test_results["gpio"] = results
        print("GPIO 핀 테스트 완료")
        return results
    
    def test_motors(self):
        """모터 테스트"""
        print("모터 테스트 시작")
        
        results = {}
        
        try:
            # PWM 핀 테스트
            motor_left_pwm = PWM(Pin(2))
            motor_right_pwm = PWM(Pin(4))
            motor_left_pwm.freq(1000)
            motor_right_pwm.freq(1000)
            
            # 방향 핀 테스트
            motor_left_dir = Pin(3, Pin.OUT)
            motor_right_dir = Pin(5, Pin.OUT)
            
            # 낮은 속도로 테스트
            print("모터 테스트 실행 중...")
            motor_left_pwm.duty(100)
            motor_right_pwm.duty(100)
            time.sleep(0.5)
            
            # 정지
            motor_left_pwm.duty(0)
            motor_right_pwm.duty(0)
            
            results["left_motor"] = "OK"
            results["right_motor"] = "OK"
            
        except Exception as e:
            results["error"] = str(e)
        
        self.test_results["motors"] = results
        print("모터 테스트 완료")
        return results
    
    def test_encoders(self):
        """엔코더 테스트"""
        print("엔코더 테스트 시작")
        
        results = {}
        
        try:
            # 엔코더 핀 초기화
            encoder_left_a = Pin(6, Pin.IN, Pin.PULL_UP)
            encoder_left_b = Pin(7, Pin.IN, Pin.PULL_UP)
            encoder_right_a = Pin(8, Pin.IN, Pin.PULL_UP)
            encoder_right_b = Pin(9, Pin.IN, Pin.PULL_UP)
            
            # 엔코더 값 읽기
            left_a = encoder_left_a.value()
            left_b = encoder_left_b.value()
            right_a = encoder_right_a.value()
            right_b = encoder_right_b.value()
            
            results["left_encoder"] = f"A:{left_a}, B:{left_b}"
            results["right_encoder"] = f"A:{right_a}, B:{right_b}"
            
        except Exception as e:
            results["error"] = str(e)
        
        self.test_results["encoders"] = results
        print("엔코더 테스트 완료")
        return results
    
    def test_sensors(self):
        """센서 테스트"""
        print("센서 테스트 시작")
        
        results = {}
        
        try:
            # ADC 센서 초기화
            sensor_drop = ADC(Pin(10))
            sensor_obstacle = ADC(Pin(11))
            battery_adc = ADC(Pin(13))
            
            # ADC 설정
            sensor_drop.atten(ADC.ATTN_11DB)
            sensor_obstacle.atten(ADC.ATTN_11DB)
            battery_adc.atten(ADC.ATTN_11DB)
            
            # 센서 값 읽기
            drop_value = sensor_drop.read()
            obstacle_value = sensor_obstacle.read()
            battery_value = battery_adc.read()
            
            # 전압 계산
            battery_voltage = (battery_value / 4095) * 3.3 * 2
            
            results["drop_sensor"] = f"값: {drop_value}"
            results["obstacle_sensor"] = f"값: {obstacle_value}"
            results["battery"] = f"값: {battery_value}, 전압: {battery_voltage:.2f}V"
            
        except Exception as e:
            results["error"] = str(e)
        
        self.test_results["sensors"] = results
        print("센서 테스트 완료")
        return results
    
    def test_led_matrix(self):
        """LED 매트릭스 테스트"""
        print("LED 매트릭스 테스트 시작")
        
        results = {}
        
        try:
            # I2C 초기화
            i2c = I2C(0, sda=Pin(35), scl=Pin(36), freq=400000)
            
            # I2C 장치 스캔
            devices = i2c.scan()
            results["i2c_devices"] = devices
            
            if 0x70 in devices:
                # 테스트 패턴 전송
                test_pattern = [0xFF, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0xFF]
                i2c.writeto(0x70, bytes(test_pattern))
                time.sleep(1)
                
                # 패턴 지우기
                clear_pattern = [0x00] * 8
                i2c.writeto(0x70, bytes(clear_pattern))
                
                results["led_matrix"] = "OK"
            else:
                results["led_matrix"] = "ERROR: LED 매트릭스를 찾을 수 없음"
                
        except Exception as e:
            results["error"] = str(e)
        
        self.test_results["led_matrix"] = results
        print("LED 매트릭스 테스트 완료")
        return results
    
    def test_buzzer(self):
        """버저 테스트"""
        print("버저 테스트 시작")
        
        results = {}
        
        try:
            buzzer = PWM(Pin(12))
            buzzer.freq(1000)
            
            # 테스트 소리 재생
            buzzer.duty(512)
            time.sleep(0.3)
            buzzer.duty(0)
            
            results["buzzer"] = "OK"
            
        except Exception as e:
            results["error"] = str(e)
        
        self.test_results["buzzer"] = results
        print("버저 테스트 완료")
        return results
    
    def test_wifi(self):
        """Wi-Fi 테스트"""
        print("Wi-Fi 테스트 시작")
        
        results = {}
        
        try:
            import network
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            
            # Wi-Fi 네트워크 스캔
            networks = wlan.scan()
            results["available_networks"] = len(networks)
            results["networks"] = [net[0].decode() for net in networks[:5]]  # 처음 5개만
            
        except Exception as e:
            results["error"] = str(e)
        
        self.test_results["wifi"] = results
        print("Wi-Fi 테스트 완료")
        return results
    
    def test_memory(self):
        """메모리 테스트"""
        print("메모리 테스트 시작")
        
        results = {}
        
        try:
            import machine
            import gc
            
            # 메모리 정보
            mem_info = machine.mem_info()
            results["mem_info"] = str(mem_info)
            
            # 가비지 컬렉션
            gc.collect()
            results["gc_collect"] = "OK"
            
            # 메모리 사용량
            results["free_memory"] = gc.mem_free()
            results["allocated_memory"] = gc.mem_alloc()
            
        except Exception as e:
            results["error"] = str(e)
        
        self.test_results["memory"] = results
        print("메모리 테스트 완료")
        return results
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("=" * 50)
        print("Deks 1.0 ESP32 펌웨어 테스트 시작")
        print("=" * 50)
        
        # 각 테스트 실행
        self.test_gpio_pins()
        self.test_encoders()
        self.test_sensors()
        self.test_led_matrix()
        self.test_buzzer()
        self.test_wifi()
        self.test_memory()
        # self.test_motors()  # 안전을 위해 주석 처리
        
        # 결과 출력
        self.print_test_results()
        
        print("=" * 50)
        print("모든 테스트 완료")
        print("=" * 50)
    
    def print_test_results(self):
        """테스트 결과 출력"""
        print("\n테스트 결과:")
        print("-" * 30)
        
        for test_name, results in self.test_results.items():
            print(f"\n{test_name.upper()} 테스트:")
            for key, value in results.items():
                print(f"  {key}: {value}")
    
    def save_test_results(self):
        """테스트 결과를 파일로 저장"""
        try:
            with open("test_results.json", "w") as f:
                json.dump(self.test_results, f, indent=2)
            print("테스트 결과가 test_results.json에 저장되었습니다")
        except Exception as e:
            print(f"테스트 결과 저장 실패: {e}")

# 테스트 실행
def main():
    """메인 테스트 함수"""
    tester = FirmwareTester()
    tester.run_all_tests()
    tester.save_test_results()

if __name__ == "__main__":
    main()
