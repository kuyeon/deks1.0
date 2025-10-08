"""
Deks 1.0 통신 프로토콜 최적화 모듈
메시지 포맷, 전송 효율성, 에러 처리 개선
"""

import json
import time
import struct
from typing import Dict, Any, Optional, List

class ProtocolOptimizer:
    """통신 프로토콜 최적화 클래스"""
    
    def __init__(self):
        # 메시지 타입 정의
        self.MESSAGE_TYPES = {
            "STATUS": 0x01,
            "MOVE": 0x02,
            "STOP": 0x03,
            "EXPRESSION": 0x04,
            "SOUND": 0x05,
            "EMERGENCY_STOP": 0x06,
            "RESET": 0x07,
            "CONFIG": 0x08,
            "HEARTBEAT": 0x09,
            "ERROR": 0x0A,
            "SENSOR_DATA": 0x0B
        }
        
        # 역방향 매핑
        self.TYPE_TO_NAME = {v: k for k, v in self.MESSAGE_TYPES.items()}
        
        # 메시지 버퍼
        self.message_buffer = bytearray()
        self.buffer_size = 0
        self.max_buffer_size = 1024
        
        # 통계 정보
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "bytes_sent": 0,
            "bytes_received": 0,
            "errors": 0,
            "last_activity": 0
        }
    
    def create_binary_message(self, msg_type: str, data: Dict[str, Any]) -> bytes:
        """바이너리 메시지 생성 (JSON 대신 바이너리 포맷 사용)"""
        try:
            # 메시지 타입 확인
            if msg_type not in self.MESSAGE_TYPES:
                raise ValueError(f"알 수 없는 메시지 타입: {msg_type}")
            
            type_code = self.MESSAGE_TYPES[msg_type]
            
            # 메시지 헤더 생성 (4바이트)
            # [타입(1바이트)][길이(2바이트)][체크섬(1바이트)]
            timestamp = int(time.time() * 1000) & 0xFFFFFFFF  # 4바이트 타임스탬프
            
            # 데이터를 바이너리로 인코딩
            binary_data = self._encode_data(data)
            data_length = len(binary_data)
            
            # 체크섬 계산
            checksum = self._calculate_checksum(type_code, data_length, binary_data)
            
            # 메시지 조립
            message = struct.pack('>BHHB', type_code, data_length, timestamp & 0xFFFF, checksum)
            message += binary_data
            
            # 통계 업데이트
            self.stats["messages_sent"] += 1
            self.stats["bytes_sent"] += len(message)
            self.stats["last_activity"] = time.time()
            
            return message
            
        except Exception as e:
            self.stats["errors"] += 1
            print(f"바이너리 메시지 생성 실패: {e}")
            return b""
    
    def parse_binary_message(self, data: bytes) -> Optional[Dict[str, Any]]:
        """바이너리 메시지 파싱"""
        try:
            if len(data) < 6:  # 최소 헤더 크기
                return None
            
            # 헤더 파싱
            type_code, data_length, timestamp, checksum = struct.unpack('>BHHB', data[:6])
            
            # 데이터 추출
            if len(data) < 6 + data_length:
                return None
            
            binary_data = data[6:6+data_length]
            
            # 체크섬 검증
            expected_checksum = self._calculate_checksum(type_code, data_length, binary_data)
            if checksum != expected_checksum:
                print(f"체크섬 오류: {checksum} != {expected_checksum}")
                self.stats["errors"] += 1
                return None
            
            # 메시지 타입 확인
            if type_code not in self.TYPE_TO_NAME:
                print(f"알 수 없는 메시지 타입 코드: {type_code}")
                self.stats["errors"] += 1
                return None
            
            msg_type = self.TYPE_TO_NAME[type_code]
            
            # 데이터 디코딩
            decoded_data = self._decode_data(binary_data, msg_type)
            
            # 통계 업데이트
            self.stats["messages_received"] += 1
            self.stats["bytes_received"] += len(data)
            self.stats["last_activity"] = time.time()
            
            return {
                "type": msg_type,
                "timestamp": timestamp,
                "data": decoded_data
            }
            
        except Exception as e:
            self.stats["errors"] += 1
            print(f"바이너리 메시지 파싱 실패: {e}")
            return None
    
    def _encode_data(self, data: Dict[str, Any]) -> bytes:
        """데이터를 바이너리로 인코딩"""
        encoded = bytearray()
        
        for key, value in data.items():
            # 키 길이와 키 데이터
            key_bytes = key.encode('utf-8')
            encoded.extend(struct.pack('>H', len(key_bytes)))
            encoded.extend(key_bytes)
            
            # 값 인코딩
            if isinstance(value, bool):
                encoded.extend(struct.pack('>B', 1 if value else 0))
            elif isinstance(value, int):
                if -128 <= value <= 127:
                    encoded.extend(struct.pack('>b', value))  # 1바이트
                elif -32768 <= value <= 32767:
                    encoded.extend(struct.pack('>h', value))  # 2바이트
                else:
                    encoded.extend(struct.pack('>i', value))  # 4바이트
            elif isinstance(value, float):
                encoded.extend(struct.pack('>f', value))  # 4바이트 float
            elif isinstance(value, str):
                value_bytes = value.encode('utf-8')
                encoded.extend(struct.pack('>H', len(value_bytes)))
                encoded.extend(value_bytes)
            elif isinstance(value, dict):
                # 중첩된 딕셔너리 재귀 처리
                nested_data = self._encode_data(value)
                encoded.extend(struct.pack('>H', len(nested_data)))
                encoded.extend(nested_data)
            elif isinstance(value, list):
                # 리스트 처리
                encoded.extend(struct.pack('>H', len(value)))
                for item in value:
                    if isinstance(item, int):
                        encoded.extend(struct.pack('>h', item))
                    elif isinstance(item, float):
                        encoded.extend(struct.pack('>f', item))
        
        return bytes(encoded)
    
    def _decode_data(self, data: bytes, msg_type: str) -> Dict[str, Any]:
        """바이너리 데이터를 딕셔너리로 디코딩"""
        decoded = {}
        offset = 0
        
        while offset < len(data):
            # 키 길이 읽기
            if offset + 2 > len(data):
                break
            key_length = struct.unpack('>H', data[offset:offset+2])[0]
            offset += 2
            
            # 키 읽기
            if offset + key_length > len(data):
                break
            key = data[offset:offset+key_length].decode('utf-8')
            offset += key_length
            
            # 값 읽기 (타입에 따라)
            if msg_type == "STATUS":
                value = self._decode_status_value(data, offset)
            elif msg_type == "MOVE":
                value = self._decode_move_value(data, offset)
            elif msg_type == "SENSOR_DATA":
                value = self._decode_sensor_value(data, offset)
            else:
                value = self._decode_generic_value(data, offset)
            
            decoded[key] = value
        
        return decoded
    
    def _decode_status_value(self, data: bytes, offset: int) -> Any:
        """상태 메시지 값 디코딩"""
        if offset >= len(data):
            return None
        
        # 상태 메시지는 주로 float 값들
        if offset + 4 <= len(data):
            return struct.unpack('>f', data[offset:offset+4])[0]
        return None
    
    def _decode_move_value(self, data: bytes, offset: int) -> Any:
        """이동 명령 값 디코딩"""
        if offset >= len(data):
            return None
        
        # 이동 명령은 주로 int 값들
        if offset + 2 <= len(data):
            return struct.unpack('>h', data[offset:offset+2])[0]
        return None
    
    def _decode_sensor_value(self, data: bytes, offset: int) -> Any:
        """센서 데이터 값 디코딩"""
        if offset >= len(data):
            return None
        
        # 센서 데이터는 주로 int 값들
        if offset + 2 <= len(data):
            return struct.unpack('>H', data[offset:offset+2])[0]
        return None
    
    def _decode_generic_value(self, data: bytes, offset: int) -> Any:
        """일반 값 디코딩"""
        if offset >= len(data):
            return None
        
        # 기본적으로 int로 시도
        if offset + 2 <= len(data):
            return struct.unpack('>h', data[offset:offset+2])[0]
        return None
    
    def _calculate_checksum(self, type_code: int, data_length: int, data: bytes) -> int:
        """체크섬 계산"""
        checksum = type_code + data_length
        for byte in data:
            checksum += byte
        return checksum & 0xFF
    
    def create_compressed_message(self, msg_type: str, data: Dict[str, Any]) -> bytes:
        """압축된 메시지 생성 (JSON + 압축)"""
        try:
            # JSON 메시지 생성
            json_message = {
                "t": msg_type,
                "d": data,
                "ts": int(time.time() * 1000)
            }
            
            # JSON 문자열로 변환
            json_str = json.dumps(json_message, separators=(',', ':'))
            
            # 간단한 압축 (반복 문자 제거)
            compressed = self._simple_compress(json_str.encode('utf-8'))
            
            # 통계 업데이트
            self.stats["messages_sent"] += 1
            self.stats["bytes_sent"] += len(compressed)
            self.stats["last_activity"] = time.time()
            
            return compressed
            
        except Exception as e:
            self.stats["errors"] += 1
            print(f"압축 메시지 생성 실패: {e}")
            return b""
    
    def _simple_compress(self, data: bytes) -> bytes:
        """간단한 압축 (RLE - Run Length Encoding)"""
        if not data:
            return b""
        
        compressed = bytearray()
        current_byte = data[0]
        count = 1
        
        for i in range(1, len(data)):
            if data[i] == current_byte and count < 255:
                count += 1
            else:
                if count > 3:  # 3번 이상 반복되는 경우만 압축
                    compressed.extend([0xFF, current_byte, count])
                else:
                    compressed.extend([current_byte] * count)
                current_byte = data[i]
                count = 1
        
        # 마지막 바이트 처리
        if count > 3:
            compressed.extend([0xFF, current_byte, count])
        else:
            compressed.extend([current_byte] * count)
        
        return bytes(compressed)
    
    def _simple_decompress(self, data: bytes) -> bytes:
        """간단한 압축 해제"""
        if not data:
            return b""
        
        decompressed = bytearray()
        i = 0
        
        while i < len(data):
            if i + 2 < len(data) and data[i] == 0xFF:
                # 압축된 데이터
                byte_value = data[i + 1]
                count = data[i + 2]
                decompressed.extend([byte_value] * count)
                i += 3
            else:
                # 일반 데이터
                decompressed.append(data[i])
                i += 1
        
        return bytes(decompressed)
    
    def parse_compressed_message(self, data: bytes) -> Optional[Dict[str, Any]]:
        """압축된 메시지 파싱"""
        try:
            # 압축 해제
            decompressed = self._simple_decompress(data)
            
            # JSON 파싱
            json_str = decompressed.decode('utf-8')
            message = json.loads(json_str)
            
            # 통계 업데이트
            self.stats["messages_received"] += 1
            self.stats["bytes_received"] += len(data)
            self.stats["last_activity"] = time.time()
            
            return message
            
        except Exception as e:
            self.stats["errors"] += 1
            print(f"압축 메시지 파싱 실패: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """통신 통계 반환"""
        current_time = time.time()
        uptime = current_time - self.stats["last_activity"] if self.stats["last_activity"] > 0 else 0
        
        return {
            "messages_sent": self.stats["messages_sent"],
            "messages_received": self.stats["messages_received"],
            "bytes_sent": self.stats["bytes_sent"],
            "bytes_received": self.stats["bytes_received"],
            "errors": self.stats["errors"],
            "uptime": uptime,
            "error_rate": self.stats["errors"] / max(1, self.stats["messages_sent"] + self.stats["messages_received"])
        }
    
    def reset_statistics(self):
        """통계 초기화"""
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "bytes_sent": 0,
            "bytes_received": 0,
            "errors": 0,
            "last_activity": time.time()
        }

# 프로토콜 최적화 유틸리티 함수들
def create_optimized_status_message(battery_level: float, motor_speed: int, 
                                  encoder_counts: Dict[str, int], 
                                  sensors: Dict[str, Any]) -> bytes:
    """최적화된 상태 메시지 생성"""
    optimizer = ProtocolOptimizer()
    
    data = {
        "battery": battery_level,
        "motor_speed": motor_speed,
        "encoder_left": encoder_counts.get("left", 0),
        "encoder_right": encoder_counts.get("right", 0),
        "drop_detected": sensors.get("drop_detected", False),
        "obstacle_detected": sensors.get("obstacle_detected", False),
        "drop_distance": sensors.get("drop_distance", 0),
        "obstacle_distance": sensors.get("obstacle_distance", 0)
    }
    
    return optimizer.create_binary_message("STATUS", data)

def create_optimized_move_command(left_speed: int, right_speed: int) -> bytes:
    """최적화된 이동 명령 생성"""
    optimizer = ProtocolOptimizer()
    
    data = {
        "left_speed": left_speed,
        "right_speed": right_speed
    }
    
    return optimizer.create_binary_message("MOVE", data)

def create_optimized_expression_command(expression: str) -> bytes:
    """최적화된 표정 명령 생성"""
    optimizer = ProtocolOptimizer()
    
    data = {
        "expression": expression
    }
    
    return optimizer.create_binary_message("EXPRESSION", data)

def create_optimized_sound_command(sound: str, duration: int = 500) -> bytes:
    """최적화된 소리 명령 생성"""
    optimizer = ProtocolOptimizer()
    
    data = {
        "sound": sound,
        "duration": duration
    }
    
    return optimizer.create_binary_message("SOUND", data)
