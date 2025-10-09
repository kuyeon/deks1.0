"""
ESP32 시뮬레이터 - Socket Bridge 연결 테스트용
"""

import socket
import json
import time
import threading

class ESP32Simulator:
    def __init__(self, host="localhost", port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.running = False
    
    def connect(self):
        """Socket Bridge에 연결"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"ESP32 시뮬레이터가 Socket Bridge에 연결됨: {self.host}:{self.port}")
            
            # 핸드셰이크 수행
            self.send_handshake()
            
            # 메시지 수신 루프 시작
            self.running = True
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            # 센서 데이터 전송 루프
            sensor_thread = threading.Thread(target=self.send_sensor_data)
            sensor_thread.daemon = True
            sensor_thread.start()
            
            return True
            
        except Exception as e:
            print(f"연결 실패: {e}")
            return False
    
    def send_handshake(self):
        """초기 핸드셰이크 메시지 전송"""
        handshake = {
            "type": "handshake",
            "firmware_version": "1.0.0",
            "robot_id": "deks_001",
            "capabilities": ["move", "turn", "sensors", "led"]
        }
        self.send_message(handshake)
    
    def send_message(self, message):
        """메시지 전송"""
        try:
            message_json = json.dumps(message, ensure_ascii=False) + "\n"
            self.socket.send(message_json.encode())
            print(f"메시지 전송: {message['type']}")
        except Exception as e:
            print(f"메시지 전송 실패: {e}")
    
    def receive_messages(self):
        """서버로부터 메시지 수신"""
        while self.running and self.connected:
            try:
                data = self.socket.recv(1024)
                if data:
                    message = json.loads(data.decode().strip())
                    print(f"메시지 수신: {message}")
                    self.handle_message(message)
                else:
                    print("연결이 끊어졌습니다")
                    break
            except Exception as e:
                print(f"메시지 수신 오류: {e}")
                break
    
    def handle_message(self, message):
        """수신된 메시지 처리"""
        message_type = message.get("type")
        
        if message_type == "ping":
            # 핑에 대한 퐁 응답
            pong = {
                "type": "pong",
                "timestamp": message.get("timestamp")
            }
            self.send_message(pong)
        
        elif message_type == "command":
            # 명령 실행 시뮬레이션
            command = message.get("command", {})
            print(f"명령 실행: {command}")
            
            # 명령 실행 결과 전송
            result = {
                "type": "command_result",
                "command_id": message.get("command_id"),
                "success": True,
                "data": {
                    "executed_command": command.get("type"),
                    "execution_time": 1.0
                },
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            self.send_message(result)
    
    def send_sensor_data(self):
        """주기적으로 센서 데이터 전송"""
        while self.running and self.connected:
            try:
                sensor_data = {
                    "type": "sensor_data",
                    "data": {
                        "front_distance": 25.5 + (time.time() % 10 - 5),  # 변하는 값
                        "drop_detection": False,
                        "battery_level": 85,
                        "battery_voltage": 3.7,
                        "temperature": 25.0
                    },
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
                }
                self.send_message(sensor_data)
                time.sleep(5)  # 5초마다 전송
                
            except Exception as e:
                print(f"센서 데이터 전송 오류: {e}")
                break
    
    def disconnect(self):
        """연결 종료"""
        self.running = False
        self.connected = False
        if self.socket:
            self.socket.close()
        print("ESP32 시뮬레이터 연결 종료")

if __name__ == "__main__":
    print("ESP32 시뮬레이터 시작...")
    simulator = ESP32Simulator()
    
    if simulator.connect():
        try:
            print("ESP32 시뮬레이터 실행 중... (Ctrl+C로 종료)")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nESP32 시뮬레이터 종료 중...")
            simulator.disconnect()
    else:
        print("ESP32 시뮬레이터 연결 실패")
