"""
Deks 1.0 하드웨어 테스트 시나리오
실제 하드웨어에서 실행할 수 있는 종합 테스트 시나리오
"""

import time
import uasyncio as asyncio
from hardware_interface import HardwareInterface
from config import GPIO_CONFIG

class HardwareTestScenarios:
    """하드웨어 테스트 시나리오 클래스"""
    
    def __init__(self):
        """테스트 시나리오 초기화"""
        self.hardware = HardwareInterface(GPIO_CONFIG)
        self.test_results = {}
        self.current_test = None
        
        print("하드웨어 테스트 시나리오 초기화 완료")
    
    async def run_all_tests(self):
        """모든 테스트 시나리오 실행"""
        print("=" * 60)
        print("Deks 1.0 하드웨어 종합 테스트 시작")
        print("=" * 60)
        
        # 테스트 시나리오 목록
        test_scenarios = [
            ("기본 하드웨어 점검", self.test_basic_hardware),
            ("센서 시스템 테스트", self.test_sensor_system),
            ("모터 시스템 테스트", self.test_motor_system),
            ("LED 표정 시스템 테스트", self.test_led_expression_system),
            ("버저 소리 시스템 테스트", self.test_buzzer_sound_system),
            ("안전 시스템 테스트", self.test_safety_system),
            ("통합 동작 테스트", self.test_integrated_operation),
            ("스트레스 테스트", self.test_stress_test),
            ("장시간 동작 테스트", self.test_long_duration_operation)
        ]
        
        # 각 테스트 실행
        for test_name, test_func in test_scenarios:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = await test_func()
                self.test_results[test_name] = {
                    "status": "PASS" if result else "FAIL",
                    "details": "테스트 완료" if result else "테스트 실패"
                }
                print(f"✅ {test_name}: {'통과' if result else '실패'}")
            except Exception as e:
                self.test_results[test_name] = {
                    "status": "ERROR",
                    "details": str(e)
                }
                print(f"❌ {test_name}: 오류 - {e}")
            
            # 테스트 간 대기
            await asyncio.sleep(1)
        
        # 결과 요약
        self.print_test_summary()
        
        print("=" * 60)
        print("하드웨어 종합 테스트 완료")
        print("=" * 60)
    
    async def test_basic_hardware(self) -> bool:
        """기본 하드웨어 점검"""
        print("기본 하드웨어 점검 시작")
        
        try:
            # 하드웨어 상태 확인
            status = self.hardware.get_status()
            
            # 각 컴포넌트 상태 확인
            motor_status = status["motor"]
            sensor_status = status["sensors"]
            led_status = status["led"]
            buzzer_status = status["buzzer"]
            
            print(f"모터 상태: {motor_status['is_moving']}")
            print(f"센서 데이터: {sensor_status}")
            print(f"LED 표정: {led_status['current_expression']}")
            print(f"버저 상태: {buzzer_status['is_playing']}")
            
            # 기본 기능 동작 확인
            self.hardware.set_expression("neutral")
            await asyncio.sleep(0.5)
            
            return True
            
        except Exception as e:
            print(f"기본 하드웨어 점검 실패: {e}")
            return False
    
    async def test_sensor_system(self) -> bool:
        """센서 시스템 테스트"""
        print("센서 시스템 테스트 시작")
        
        try:
            # 센서 데이터 읽기
            self.hardware.update_sensors()
            sensor_data = self.hardware.sensor_manager.get_sensor_data()
            
            print(f"낙하 센서: {sensor_data['drop_distance']} (감지: {sensor_data['drop_detected']})")
            print(f"장애물 센서: {sensor_data['obstacle_distance']} (감지: {sensor_data['obstacle_detected']})")
            print(f"배터리 전압: {sensor_data['battery_level']:.2f}V (상태: {sensor_data['battery_status']})")
            
            # 센서 값 범위 확인
            if (0 <= sensor_data['drop_distance'] <= 4095 and 
                0 <= sensor_data['obstacle_distance'] <= 4095 and
                sensor_data['battery_level'] > 0):
                print("센서 값이 정상 범위 내에 있습니다")
                return True
            else:
                print("센서 값이 비정상 범위입니다")
                return False
                
        except Exception as e:
            print(f"센서 시스템 테스트 실패: {e}")
            return False
    
    async def test_motor_system(self) -> bool:
        """모터 시스템 테스트 (안전 모드)"""
        print("모터 시스템 테스트 시작 (안전 모드)")
        
        try:
            # 매우 낮은 속도로 짧은 테스트
            print("전진 테스트 (낮은 속도)")
            self.hardware.move_robot(20, 20)
            await asyncio.sleep(0.5)
            
            print("정지")
            self.hardware.stop_robot()
            await asyncio.sleep(0.5)
            
            print("후진 테스트 (낮은 속도)")
            self.hardware.move_robot(-20, -20)
            await asyncio.sleep(0.5)
            
            print("정지")
            self.hardware.stop_robot()
            await asyncio.sleep(0.5)
            
            # 엔코더 카운트 확인
            encoder_counts = self.hardware.motor_controller.get_encoder_counts()
            print(f"엔코더 카운트 - 왼쪽: {encoder_counts['left']}, 오른쪽: {encoder_counts['right']}")
            
            # 엔코더가 변화했는지 확인
            if encoder_counts['left'] != 0 or encoder_counts['right'] != 0:
                print("엔코더가 정상적으로 동작합니다")
                return True
            else:
                print("엔코더 동작이 감지되지 않았습니다")
                return False
                
        except Exception as e:
            print(f"모터 시스템 테스트 실패: {e}")
            return False
    
    async def test_led_expression_system(self) -> bool:
        """LED 표정 시스템 테스트"""
        print("LED 표정 시스템 테스트 시작")
        
        try:
            # 다양한 표정 테스트
            expressions = ["happy", "sad", "neutral", "thinking", "error", "surprised", "angry", "sleepy"]
            
            for expression in expressions:
                print(f"표정 테스트: {expression}")
                self.hardware.set_expression(expression)
                await asyncio.sleep(0.5)
            
            # 애니메이션 테스트
            print("애니메이션 테스트: blink")
            self.hardware.led_controller.play_animation("blink", 1000)
            await asyncio.sleep(1)
            
            print("애니메이션 테스트: pulse")
            self.hardware.led_controller.play_animation("pulse", 1000)
            await asyncio.sleep(1)
            
            # 기본 표정으로 복귀
            self.hardware.set_expression("neutral")
            
            print("LED 표정 시스템 테스트 완료")
            return True
            
        except Exception as e:
            print(f"LED 표정 시스템 테스트 실패: {e}")
            return False
    
    async def test_buzzer_sound_system(self) -> bool:
        """버저 소리 시스템 테스트"""
        print("버저 소리 시스템 테스트 시작")
        
        try:
            # 다양한 소리 테스트
            sounds = ["start", "success", "error", "warning", "thinking", "notification", "complete"]
            
            for sound in sounds:
                print(f"소리 테스트: {sound}")
                self.hardware.play_sound(sound)
                await asyncio.sleep(0.5)
            
            # 볼륨 테스트
            print("볼륨 테스트")
            for volume in range(5):
                print(f"볼륨 레벨: {volume}")
                self.hardware.buzzer_controller.play_sound("notification", volume)
                await asyncio.sleep(0.3)
            
            # 커스텀 멜로디 테스트
            print("커스텀 멜로디 테스트")
            custom_frequencies = [1000, 1200, 1400, 1600, 1800, 2000]
            custom_durations = [200, 200, 200, 200, 200, 400]
            self.hardware.buzzer_controller.play_custom_melody(custom_frequencies, custom_durations)
            
            print("버저 소리 시스템 테스트 완료")
            return True
            
        except Exception as e:
            print(f"버저 소리 시스템 테스트 실패: {e}")
            return False
    
    async def test_safety_system(self) -> bool:
        """안전 시스템 테스트"""
        print("안전 시스템 테스트 시작")
        
        try:
            # 비상 정지 테스트
            print("비상 정지 테스트")
            self.hardware.emergency_stop = True
            result = self.hardware.move_robot(50, 50)
            if not result:
                print("비상 정지가 정상적으로 동작합니다")
            else:
                print("비상 정지가 동작하지 않습니다")
                return False
            
            # 비상 정지 리셋
            self.hardware.reset_emergency_stop()
            await asyncio.sleep(0.5)
            
            # 안전 시스템 활성화/비활성화 테스트
            print("안전 시스템 비활성화 테스트")
            self.hardware.safety_enabled = False
            result = self.hardware.move_robot(30, 30)
            if result:
                print("안전 시스템 비활성화가 정상적으로 동작합니다")
            else:
                print("안전 시스템 비활성화가 동작하지 않습니다")
                return False
            
            # 안전 시스템 재활성화
            self.hardware.safety_enabled = True
            self.hardware.stop_robot()
            
            print("안전 시스템 테스트 완료")
            return True
            
        except Exception as e:
            print(f"안전 시스템 테스트 실패: {e}")
            return False
    
    async def test_integrated_operation(self) -> bool:
        """통합 동작 테스트"""
        print("통합 동작 테스트 시작")
        
        try:
            # 시나리오 1: 명령 수신 시나리오
            print("시나리오 1: 명령 수신")
            self.hardware.set_expression("thinking")
            self.hardware.play_sound("notification")
            await asyncio.sleep(0.5)
            
            # 시나리오 2: 이동 명령 실행
            print("시나리오 2: 이동 명령 실행")
            self.hardware.set_expression("neutral")
            self.hardware.move_robot(30, 30)
            await asyncio.sleep(1)
            
            # 시나리오 3: 작업 완료
            print("시나리오 3: 작업 완료")
            self.hardware.stop_robot()
            self.hardware.set_expression("happy")
            self.hardware.play_sound("success")
            await asyncio.sleep(1)
            
            # 시나리오 4: 에러 상황
            print("시나리오 4: 에러 상황")
            self.hardware.set_expression("error")
            self.hardware.play_sound("error")
            await asyncio.sleep(1)
            
            # 기본 상태로 복귀
            self.hardware.set_expression("neutral")
            
            print("통합 동작 테스트 완료")
            return True
            
        except Exception as e:
            print(f"통합 동작 테스트 실패: {e}")
            return False
    
    async def test_stress_test(self) -> bool:
        """스트레스 테스트"""
        print("스트레스 테스트 시작")
        
        try:
            # 빠른 연속 명령 테스트
            print("빠른 연속 명령 테스트")
            for i in range(10):
                # 빠른 표정 변경
                expressions = ["happy", "sad", "neutral", "thinking"]
                self.hardware.set_expression(expressions[i % len(expressions)])
                
                # 빠른 소리 재생
                sounds = ["notification", "start", "success"]
                self.hardware.play_sound(sounds[i % len(sounds)])
                
                # 빠른 모터 제어 (낮은 속도)
                speeds = [20, -20, 0]
                self.hardware.move_robot(speeds[i % len(speeds)], speeds[i % len(speeds)])
                
                await asyncio.sleep(0.1)
            
            # 정리
            self.hardware.stop_robot()
            self.hardware.set_expression("neutral")
            
            print("스트레스 테스트 완료")
            return True
            
        except Exception as e:
            print(f"스트레스 테스트 실패: {e}")
            return False
    
    async def test_long_duration_operation(self) -> bool:
        """장시간 동작 테스트"""
        print("장시간 동작 테스트 시작 (30초)")
        
        try:
            start_time = time.time()
            test_duration = 30  # 30초 테스트
            
            while time.time() - start_time < test_duration:
                # 센서 데이터 주기적 업데이트
                self.hardware.update_sensors()
                
                # 주기적 상태 표시
                elapsed = int(time.time() - start_time)
                if elapsed % 5 == 0:
                    print(f"테스트 진행 중: {elapsed}초")
                    self.hardware.set_expression("thinking")
                    self.hardware.play_sound("notification")
                
                # 주기적 모터 테스트 (매우 낮은 속도)
                if elapsed % 10 == 0:
                    self.hardware.move_robot(15, 15)
                    await asyncio.sleep(0.5)
                    self.hardware.stop_robot()
                
                await asyncio.sleep(1)
            
            # 테스트 완료
            self.hardware.set_expression("happy")
            self.hardware.play_sound("complete")
            
            print("장시간 동작 테스트 완료")
            return True
            
        except Exception as e:
            print(f"장시간 동작 테스트 실패: {e}")
            return False
    
    def print_test_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("테스트 결과 요약")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["status"] == "PASS")
        failed_tests = sum(1 for result in self.test_results.values() if result["status"] == "FAIL")
        error_tests = sum(1 for result in self.test_results.values() if result["status"] == "ERROR")
        
        print(f"총 테스트: {total_tests}")
        print(f"통과: {passed_tests}")
        print(f"실패: {failed_tests}")
        print(f"오류: {error_tests}")
        print(f"성공률: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n상세 결과:")
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_icon} {test_name}: {result['status']} - {result['details']}")
    
    def save_test_results(self):
        """테스트 결과를 파일로 저장"""
        try:
            import json
            with open("hardware_test_results.json", "w") as f:
                json.dump(self.test_results, f, indent=2)
            print("테스트 결과가 hardware_test_results.json에 저장되었습니다")
        except Exception as e:
            print(f"테스트 결과 저장 실패: {e}")

# 테스트 실행 함수
async def main():
    """메인 테스트 실행 함수"""
    tester = HardwareTestScenarios()
    await tester.run_all_tests()
    tester.save_test_results()

# 개별 테스트 실행 함수들
async def run_basic_tests():
    """기본 테스트만 실행"""
    tester = HardwareTestScenarios()
    
    basic_tests = [
        ("기본 하드웨어 점검", tester.test_basic_hardware),
        ("센서 시스템 테스트", tester.test_sensor_system),
        ("LED 표정 시스템 테스트", tester.test_led_expression_system),
        ("버저 소리 시스템 테스트", tester.test_buzzer_sound_system)
    ]
    
    for test_name, test_func in basic_tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = await test_func()
            print(f"✅ {test_name}: {'통과' if result else '실패'}")
        except Exception as e:
            print(f"❌ {test_name}: 오류 - {e}")

async def run_safety_tests():
    """안전 테스트만 실행"""
    tester = HardwareTestScenarios()
    
    safety_tests = [
        ("안전 시스템 테스트", tester.test_safety_system),
        ("통합 동작 테스트", tester.test_integrated_operation)
    ]
    
    for test_name, test_func in safety_tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = await test_func()
            print(f"✅ {test_name}: {'통과' if result else '실패'}")
        except Exception as e:
            print(f"❌ {test_name}: 오류 - {e}")

# 테스트 실행
if __name__ == "__main__":
    asyncio.run(main())
