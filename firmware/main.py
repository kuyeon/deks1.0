"""
Deks 1.0 ESP32 펌웨어 - 메인 제어 프로그램
마이크로파이썬 기반 ESP32 S3 펌웨어

기능:
- TCP 클라이언트로 서버와 통신
- 모터 제어 (FIT0405 + L298N)
- 센서 데이터 수집 (적외선 센서, 엔코더)
- LED 매트릭스 표정 제어
- 버저 소리 제어
- 배터리 모니터링
- 최적화된 통신 프로토콜
- 하드웨어 인터페이스 추상화
"""

import network
import socket
import json
import time
import machine
from machine import Pin, PWM, ADC, I2C
import uasyncio as asyncio
from micropython import const

# 로컬 모듈 임포트
from config import *
from hardware_interface import HardwareInterface
from protocol import ProtocolOptimizer, create_optimized_status_message

# 설정에서 상수 가져오기
SERVER_HOST = SERVER_CONFIG["host"]
SERVER_PORT = SERVER_CONFIG["port"]
WIFI_SSID = WIFI_CONFIG["ssid"]
WIFI_PASSWORD = WIFI_CONFIG["password"]

class DeksRobot:
    """Deks 로봇 메인 제어 클래스"""
    
    def __init__(self):
        print("Deks 로봇 초기화 시작")
        
        # 네트워크 설정
        self.wlan = network.WLAN(network.STA_IF)
        self.socket = None
        self.wifi_connected = False
        self.connected = False
        
        # 하드웨어 인터페이스 초기화
        self.hardware = HardwareInterface(GPIO_CONFIG)
        
        # 비상 정지 해제 (초기화 시)
        self.hardware.emergency_stop = False
        
        # 통신 프로토콜 최적화
        self.protocol = ProtocolOptimizer()
        
        # 상태 변수
        self.last_heartbeat = time.time()
        self.message_count = 0
        
        print("Deks 로봇 초기화 완료")
    
    
    def connect_wifi(self):
        """Wi-Fi 연결"""
        print(f"Wi-Fi 연결 시도: {WIFI_SSID}")
        
        try:
            # Wi-Fi 재초기화
            self.wlan.active(False)
            time.sleep_ms(100)
            self.wlan.active(True)
            
            # 이전 연결 해제
            if self.wlan.isconnected():
                self.wlan.disconnect()
                time.sleep_ms(100)
            
            # 연결 시도
            self.wlan.connect(WIFI_SSID, WIFI_PASSWORD)
            
            # 연결 대기 (타임아웃: 10초)
            timeout = WIFI_CONFIG["timeout"] * 1000  # ms로 변환
            start_time = time.ticks_ms()
            
            while not self.wlan.isconnected():
                if time.ticks_diff(time.ticks_ms(), start_time) > timeout:
                    print("Wi-Fi 연결 타임아웃")
                    self.wifi_connected = False
                    return False
                time.sleep_ms(100)
            
            # 연결 성공
            ip_info = self.wlan.ifconfig()
            print(f"Wi-Fi 연결 성공!")
            print(f"  IP: {ip_info[0]}")
            print(f"  Gateway: {ip_info[2]}")
            self.wifi_connected = True
            return True
            
        except Exception as e:
            print(f"Wi-Fi 연결 실패: {e}")
            self.wifi_connected = False
            return False
    
    def connect_server(self):
        """서버에 TCP 연결"""
        print(f"서버 연결 시도: {SERVER_HOST}:{SERVER_PORT}")
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(3)  # 3초 타임아웃
            print(f"소켓 생성 완료, 연결 시도 중...")
            self.socket.connect((SERVER_HOST, SERVER_PORT))
            self.socket.settimeout(None)  # 연결 후 타임아웃 해제
            self.connected = True
            print("서버 연결 성공")
            
            # 핸드셰이크 메시지 전송 (JSON 형식)
            handshake = {
                "type": "handshake",
                "device_id": "esp32_deks_001",
                "version": "1.0.0",
                "ip": self.wlan.ifconfig()[0]
            }
            self.send_data(handshake)
            print("핸드셰이크 전송 완료")
            
            # 연결 성공 표시
            self.hardware.set_expression("happy")
            self.hardware.play_sound("start")
            
            return True
            
        except Exception as e:
            print(f"서버 연결 실패: {e}")
            self.connected = False
            return False
    
    def send_data(self, data):
        """서버에 데이터 전송"""
        if not self.connected or not self.socket:
            return False
        
        try:
            message = json.dumps(data) + "\n"
            encoded_message = message.encode()
            
            # 소켓 전송 (논블로킹 설정 후 전송)
            self.socket.setblocking(True)
            self.socket.send(encoded_message)
            return True
        except OSError as e:
            # 타임아웃 에러는 무시하고 계속
            if e.args[0] in (116, 110):  # ETIMEDOUT, ECONNRESET은 재시도
                return False
            else:
                print(f"데이터 전송 실패: {e}")
                self.connected = False
                return False
        except Exception as e:
            print(f"데이터 전송 실패: {e}")
            self.connected = False
            return False
    
    def receive_command(self):
        """서버로부터 명령 수신"""
        if not self.connected or not self.socket:
            return None
        
        try:
            # 논블로킹 수신
            self.socket.settimeout(0.1)
            data = self.socket.recv(1024)
            if data:
                command = json.loads(data.decode().strip())
                return command
        except OSError as e:
            # 타임아웃이나 데이터 없음 (EAGAIN, ETIMEDOUT)
            if e.args[0] not in (11, 110, 115, 116):  # EAGAIN, ETIMEDOUT
                print(f"명령 수신 실패: {e}")
                self.connected = False
        except Exception as e:
            print(f"명령 수신 실패: {e}")
            self.connected = False
        
        return None
    
    def update_sensors(self):
        """센서 데이터 업데이트"""
        self.hardware.update_sensors()
    
    def move_motors(self, left_speed, right_speed):
        """모터 제어"""
        return self.hardware.move_robot(left_speed, right_speed)
    
    def stop_motors(self):
        """모터 정지"""
        self.hardware.stop_robot()
    
    def set_expression(self, expression_name):
        """LED 표정 설정"""
        self.hardware.set_expression(expression_name)
    
    def play_sound(self, sound_name, duration=500):
        """버저 소리 재생"""
        self.hardware.play_sound(sound_name)
    
    def process_command(self, command):
        """서버 명령 처리"""
        cmd_type = command.get("type")
        command_id = command.get("command_id", "unknown")
        success = True
        
        try:
            if cmd_type == "move":
                # 이동 명령
                left_speed = command.get("left_speed", 0)
                right_speed = command.get("right_speed", 0)
                self.move_motors(left_speed, right_speed)
                
            elif cmd_type == "stop":
                # 정지 명령
                self.stop_motors()
                
            elif cmd_type == "expression":
                # 표정 변경
                expression = command.get("expression", "neutral")
                self.set_expression(expression)
                
            elif cmd_type == "sound":
                # 소리 재생
                sound = command.get("sound", "start")
                duration = command.get("duration", 500)
                self.play_sound(sound, duration)
                
            elif cmd_type == "emergency_stop":
                # 비상 정지
                self.hardware.emergency_stop = True
                self.stop_motors()
                self.set_expression("error")
                self.play_sound("error")
                
            elif cmd_type == "reset":
                # 시스템 리셋
                self.hardware.reset_emergency_stop()
                self.set_expression("neutral")
                
        except Exception as e:
            print(f"명령 실행 오류: {e}")
            success = False
        
        # 기본 명령 타입에 대한 응답 (handshake_ack, ping, command는 별도 처리)
        if cmd_type in ["move", "stop", "expression", "sound", "emergency_stop", "reset"]:
            result = {
                "type": "command_result",
                "command_id": command_id,
                "success": success,
                "command_type": cmd_type,
                "timestamp": time.time()
            }
            self.send_data(result)
            
        elif cmd_type == "handshake_ack":
            # 핸드셰이크 응답 수신
            print(f"서버 핸드셰이크 수신: 프로토콜 버전 {command.get('protocol_version')}")
            # 하트비트 간격 업데이트
            if 'heartbeat_interval' in command:
                print(f"하트비트 간격: {command['heartbeat_interval']}초")
        
        elif cmd_type == "ping":
            # 핑 메시지 수신 - pong 응답
            pong = {"type": "pong", "timestamp": time.time()}
            self.send_data(pong)
            
        elif cmd_type == "command":
            # 중첩된 명령 처리
            inner_command = command.get("command", {})
            inner_type = inner_command.get("type")
            command_id = command.get("command_id", "unknown")
            success = False
            
            if inner_type == "forward":
                # 전진 명령
                speed = inner_command.get("speed", 50)
                distance = inner_command.get("distance", 0)
                print(f"전진: 속도 {speed}, 거리 {distance}")
                self.move_motors(speed, speed)
                success = True
                
            elif inner_type == "backward":
                # 후진 명령
                speed = inner_command.get("speed", 50)
                distance = inner_command.get("distance", 0)
                print(f"후진: 속도 {speed}, 거리 {distance}")
                self.move_motors(-speed, -speed)
                success = True
                
            elif inner_type == "turn_left":
                # 좌회전 명령
                angle = inner_command.get("angle", 90)
                print(f"좌회전: {angle}도")
                self.move_motors(-50, 50)
                success = True
                
            elif inner_type == "turn_right":
                # 우회전 명령
                angle = inner_command.get("angle", 90)
                print(f"우회전: {angle}도")
                self.move_motors(50, -50)
                success = True
                
            elif inner_type == "stop":
                # 정지 명령
                print("정지")
                self.stop_motors()
                success = True
                
            elif inner_type == "spin":
                # 빙글빙글 회전 명령
                rotations = inner_command.get("rotations", 1)
                print(f"빙글빙글 회전: {rotations}회")
                self.move_motors(50, -50)  # 제자리 회전
                success = True
                
            else:
                print(f"알 수 없는 내부 명령: {inner_type}")
            
            # 명령 실행 결과 응답
            result = {
                "type": "command_result",
                "command_id": command_id,
                "success": success,
                "timestamp": time.time()
            }
            self.send_data(result)
            
        else:
            print(f"알 수 없는 명령: {cmd_type}")
    
    def send_status(self):
        """상태 정보 전송"""
        # 연결되지 않았으면 전송하지 않음
        if not self.connected or not self.socket:
            return
        
        # 하드웨어 상태 가져오기
        hardware_status = self.hardware.get_status()
        
        status_data = {
            "type": "status",
            "timestamp": time.time(),
            "battery_level": hardware_status["sensors"]["battery_level"],
            "motor_speed": (hardware_status["motor"]["left_speed"] + hardware_status["motor"]["right_speed"]) / 2,
            "encoder_counts": hardware_status["motor"]["encoder_counts"],
            "sensors": hardware_status["sensors"],
            "emergency_stop": hardware_status["emergency_stop"],
            "connected": self.connected,
            "message_count": self.message_count
        }
        
        # JSON 메시지 전송 (바이너리는 백엔드가 아직 미지원)
        if self.send_data(status_data):
            self.message_count += 1
    
    async def main_loop(self):
        """메인 실행 루프"""
        print("메인 루프 시작")
        
        last_status_send = 0
        last_heartbeat = time.time()
        
        while True:
            try:
                # 센서 데이터 업데이트
                self.update_sensors()
                
                # 서버 명령 수신 및 처리
                command = self.receive_command()
                if command:
                    print(f"명령 수신: {command}")
                    self.process_command(command)
                    last_heartbeat = time.time()
                
                # 주기적 상태 전송 (설정된 간격마다)
                current_time = time.time()
                if current_time - last_status_send >= SERVER_CONFIG["heartbeat_interval"]:
                    self.send_status()
                    last_status_send = current_time
                
                # 하트비트 체크 (60초 이상 명령 없으면 연결 끊김으로 간주)
                if current_time - last_heartbeat > 60:
                    print("하트비트 타임아웃 - 연결 끊김")
                    self.connected = False
                    break
                
                # 안전 검사 (테스트 모드에서는 비활성화)
                # if self.connected:
                #     if not self.hardware.check_safety():
                #         print("안전 검사 실패 - 비상 정지")
                #         self.stop_motors()
                #         self.set_expression("error")
                #         # 연결 끊지만 루프는 계속
                
                await asyncio.sleep(0.1)  # 100ms 간격
                
            except Exception as e:
                print(f"메인 루프 오류: {e}")
                await asyncio.sleep(1)

# 메인 실행
async def main():
    """메인 함수"""
    print("Deks 1.0 ESP32 펌웨어 시작")
    
    # 로봇 인스턴스 생성
    robot = DeksRobot()
    
    # Wi-Fi 연결 재시도
    wifi_retry_count = 0
    max_wifi_retries = 5
    while not robot.connect_wifi() and wifi_retry_count < max_wifi_retries:
        wifi_retry_count += 1
        print(f"Wi-Fi 재연결 시도 {wifi_retry_count}/{max_wifi_retries}")
        time.sleep(5)
    
    if not robot.wifi_connected:
        print("Wi-Fi 연결 실패 - 오프라인 모드로 계속")
    else:
        # 서버 연결
        server_retry_count = 0
        max_server_retries = 3
        while not robot.connect_server() and server_retry_count < max_server_retries:
            server_retry_count += 1
            print(f"서버 재연결 시도 {server_retry_count}/{max_server_retries}")
            time.sleep(3)
        
        if not robot.connected:
            print("서버 연결 실패 - 로컬 모드로 계속")
    
    # 메인 루프 실행 (재연결 루프)
    while True:
        try:
            # 연결 확인
            if not robot.wifi_connected:
                print("Wi-Fi 재연결 시도...")
                if robot.connect_wifi():
                    print("Wi-Fi 재연결 성공")
                else:
                    print("Wi-Fi 재연결 실패 - 2초 후 재시도")
                    await asyncio.sleep(2)
                    continue
            
            if not robot.connected:
                print("서버 재연결 시도...")
                if robot.connect_server():
                    print("서버 재연결 성공")
                else:
                    print("서버 재연결 실패 - 1초 후 재시도")
                    await asyncio.sleep(1)
                    continue
            
            # 메인 루프 실행
            await robot.main_loop()
            
        except KeyboardInterrupt:
            print("프로그램 중단")
            break
        except Exception as e:
            print(f"메인 루프 예외: {e}")
            await asyncio.sleep(5)
            # 재연결 시도
            robot.connected = False
    
    # 정리 작업
    robot.stop_motors()
    if robot.socket:
        robot.socket.close()
    print("프로그램 종료")

# 프로그램 실행
if __name__ == "__main__":
    asyncio.run(main())
