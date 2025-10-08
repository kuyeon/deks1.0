"""
Socket Bridge 메인 서버
ESP32와의 TCP 통신을 담당하는 핵심 서버
"""

import asyncio
import json
import socket
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger

from .robot_controller import RobotController
from .sensor_manager import SensorManager
from .connection_manager import ConnectionManager


class SocketBridgeServer:
    """ESP32와의 TCP 통신을 담당하는 메인 서버 클래스"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8888):
        """
        Socket Bridge 서버 초기화
        
        Args:
            host: 서버 바인딩 주소 (기본값: 0.0.0.0)
            port: 서버 포트 (기본값: 8888)
        """
        self.host = host
        self.port = port
        self.server: Optional[asyncio.Server] = None
        self.is_running = False
        
        # 하위 모듈들 초기화
        self.connection_manager = ConnectionManager()
        self.robot_controller = RobotController()
        self.sensor_manager = SensorManager()
        
        # 연결 관리자를 로봇 제어기에 설정
        self.robot_controller.set_connection_manager(self.connection_manager)
        
        # 통신 프로토콜 설정
        self.protocol_version = "1.0"
        self.heartbeat_interval = 30  # 30초마다 핑
        self.command_timeout = 10     # 명령 타임아웃 10초
        
        logger.info(f"Socket Bridge 서버 초기화됨 - {host}:{port}")
    
    async def start_server(self):
        """Socket Bridge 서버 시작"""
        try:
            # TCP 서버 생성
            self.server = await asyncio.start_server(
                self._handle_client_connection,
                self.host,
                self.port
            )
            
            self.is_running = True
            logger.info(f"Socket Bridge 서버 시작됨 - {self.host}:{self.port}")
            
            # 서버 정보 출력
            addr = self.server.sockets[0].getsockname()
            logger.info(f"ESP32 연결 대기 중... {addr[0]}:{addr[1]}")
            
            # 하위 모듈들 시작
            await self.robot_controller.initialize()
            await self.sensor_manager.initialize()
            await self.connection_manager.initialize()
            
            # 서버 실행
            async with self.server:
                await self.server.serve_forever()
                
        except Exception as e:
            logger.error(f"Socket Bridge 서버 시작 실패: {e}")
            await self.stop_server()
            raise
    
    async def stop_server(self):
        """Socket Bridge 서버 중지"""
        try:
            self.is_running = False
            
            if self.server:
                self.server.close()
                await self.server.wait_closed()
                logger.info("Socket Bridge 서버 중지됨")
            
            # 하위 모듈들 정리
            await self.robot_controller.cleanup()
            await self.sensor_manager.cleanup()
            await self.connection_manager.cleanup()
            
        except Exception as e:
            logger.error(f"Socket Bridge 서버 중지 중 오류: {e}")
    
    async def _handle_client_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """ESP32 클라이언트 연결 처리"""
        client_addr = writer.get_extra_info('peername')
        client_id = f"{client_addr[0]}:{client_addr[1]}"
        
        logger.info(f"ESP32 연결됨 - {client_id}")
        
        try:
            # 연결 등록
            await self.connection_manager.register_client(client_id, writer)
            
            # 핸드셰이크 수행
            await self._perform_handshake(reader, writer, client_id)
            
            # 메시지 루프 시작
            await self._message_loop(reader, writer, client_id)
            
        except asyncio.CancelledError:
            logger.info(f"ESP32 연결 취소됨 - {client_id}")
        except Exception as e:
            logger.error(f"ESP32 연결 처리 중 오류 - {client_id}: {e}")
        finally:
            # 연결 정리
            await self.connection_manager.unregister_client(client_id)
            writer.close()
            await writer.wait_closed()
            logger.info(f"ESP32 연결 종료됨 - {client_id}")
    
    async def _perform_handshake(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, client_id: str):
        """ESP32와의 초기 핸드셰이크 수행"""
        try:
            # ESP32로부터 초기 메시지 수신
            initial_message = await asyncio.wait_for(
                reader.readline(), 
                timeout=self.command_timeout
            )
            
            if not initial_message:
                raise Exception("초기 메시지 수신 실패")
            
            # JSON 파싱
            message_data = json.loads(initial_message.decode().strip())
            
            if message_data.get("type") != "handshake":
                raise Exception("잘못된 핸드셰이크 메시지")
            
            # ESP32 정보 추출
            esp32_info = {
                "client_id": client_id,
                "firmware_version": message_data.get("firmware_version", "unknown"),
                "robot_id": message_data.get("robot_id", "deks_001"),
                "capabilities": message_data.get("capabilities", []),
                "connected_at": datetime.now().isoformat()
            }
            
            # 연결 정보 저장
            await self.connection_manager.update_client_info(client_id, esp32_info)
            
            # 핸드셰이크 응답 전송
            response = {
                "type": "handshake_ack",
                "status": "success",
                "protocol_version": self.protocol_version,
                "server_time": datetime.now().isoformat(),
                "heartbeat_interval": self.heartbeat_interval
            }
            
            await self._send_message(writer, response)
            logger.info(f"핸드셰이크 완료 - {client_id}")
            
        except asyncio.TimeoutError:
            logger.error(f"핸드셰이크 타임아웃 - {client_id}")
            raise
        except Exception as e:
            logger.error(f"핸드셰이크 실패 - {client_id}: {e}")
            raise
    
    async def _message_loop(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, client_id: str):
        """ESP32와의 메시지 루프"""
        heartbeat_task = None
        
        try:
            # 하트비트 태스크 시작
            heartbeat_task = asyncio.create_task(
                self._heartbeat_loop(writer, client_id)
            )
            
            while self.is_running:
                try:
                    # 메시지 수신 대기
                    message = await asyncio.wait_for(
                        reader.readline(),
                        timeout=self.heartbeat_interval + 5  # 하트비트보다 약간 길게
                    )
                    
                    if not message:
                        logger.warning(f"ESP32 연결 끊어짐 - {client_id}")
                        break
                    
                    # JSON 파싱
                    message_data = json.loads(message.decode().strip())
                    logger.debug(f"ESP32 메시지 수신 - {client_id}: {message_data}")
                    
                    # 메시지 타입에 따른 처리
                    await self._process_message(message_data, client_id)
                    
                except asyncio.TimeoutError:
                    # 하트비트 타임아웃 - 연결 상태 확인
                    if not await self.connection_manager.is_client_alive(client_id):
                        logger.warning(f"ESP32 하트비트 타임아웃 - {client_id}")
                        break
                    
        except Exception as e:
            logger.error(f"메시지 루프 오류 - {client_id}: {e}")
        finally:
            # 하트비트 태스크 정리
            if heartbeat_task:
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass
    
    async def _process_message(self, message_data: Dict[str, Any], client_id: str):
        """ESP32로부터 받은 메시지 처리"""
        message_type = message_data.get("type")
        
        try:
            if message_type == "sensor_data":
                # 센서 데이터 처리
                await self.sensor_manager.process_sensor_data(message_data.get("data", {}))
                
            elif message_type == "command_result":
                # 명령 실행 결과 처리
                # ESP32가 전체 메시지를 보내므로 data 필드가 아닌 전체 메시지 전달
                await self.robot_controller.handle_command_result(message_data)
                
            elif message_type == "robot_status":
                # 로봇 상태 업데이트
                await self.robot_controller.update_robot_status(message_data.get("data", {}))
                
            elif message_type == "error":
                # 에러 메시지 처리
                await self._handle_error_message(message_data.get("data", {}), client_id)
                
            elif message_type == "pong":
                # 핑 응답 처리
                await self.connection_manager.update_last_pong(client_id)
                
            elif message_type == "status":
                # ESP32 상태 메시지 처리
                logger.debug(f"ESP32 상태 수신 - {client_id}")
                # 센서 데이터 업데이트
                if "sensors" in message_data:
                    await self.sensor_manager.process_sensor_data(message_data["sensors"])
                # 로봇 상태 업데이트
                await self.robot_controller.update_robot_status({
                    "battery_level": message_data.get("battery_level", 0),
                    "motor_speed": message_data.get("motor_speed", 0),
                    "encoder_counts": message_data.get("encoder_counts", [0, 0]),
                    "emergency_stop": message_data.get("emergency_stop", False),
                    "connected": message_data.get("connected", True),
                    "timestamp": message_data.get("timestamp", 0)
                })
                
            else:
                logger.warning(f"알 수 없는 메시지 타입 - {client_id}: {message_type}")
                
        except Exception as e:
            logger.error(f"메시지 처리 중 오류 - {client_id}: {e}")
    
    async def _heartbeat_loop(self, writer: asyncio.StreamWriter, client_id: str):
        """하트비트 루프"""
        while self.is_running:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                if not self.is_running:
                    break
                
                # 핑 메시지 전송
                ping_message = {
                    "type": "ping",
                    "timestamp": datetime.now().isoformat()
                }
                
                await self._send_message(writer, ping_message)
                logger.debug(f"핑 전송 - {client_id}")
                
            except Exception as e:
                logger.error(f"하트비트 루프 오류 - {client_id}: {e}")
                break
    
    async def _send_message(self, writer: asyncio.StreamWriter, message: Dict[str, Any]):
        """ESP32에 메시지 전송"""
        try:
            message_json = json.dumps(message, ensure_ascii=False)
            message_bytes = (message_json + "\n").encode()
            
            writer.write(message_bytes)
            await writer.drain()
            
            logger.debug(f"메시지 전송: {message}")
            
        except Exception as e:
            logger.error(f"메시지 전송 실패: {e}")
            raise
    
    async def send_command(self, command: Dict[str, Any], client_id: Optional[str] = None) -> bool:
        """ESP32에 명령 전송"""
        try:
            if client_id is None:
                # 첫 번째 연결된 클라이언트에게 전송
                client_id = await self.connection_manager.get_first_client()
                if not client_id:
                    logger.error("연결된 ESP32가 없습니다")
                    return False
            
            writer = await self.connection_manager.get_client_writer(client_id)
            if not writer:
                logger.error(f"클라이언트 writer를 찾을 수 없습니다 - {client_id}")
                return False
            
            await self._send_message(writer, command)
            logger.info(f"명령 전송 완료 - {client_id}: {command.get('type', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"명령 전송 실패: {e}")
            return False
    
    async def _handle_error_message(self, error_data: Dict[str, Any], client_id: str):
        """ESP32로부터 받은 에러 메시지 처리"""
        error_type = error_data.get("error_type", "unknown")
        error_message = error_data.get("message", "알 수 없는 오류")
        
        logger.error(f"ESP32 에러 - {client_id}: {error_type} - {error_message}")
        
        # 에러 데이터베이스에 저장 (향후 구현)
        # await self.database.save_error_log({
        #     "client_id": client_id,
        #     "error_type": error_type,
        #     "error_message": error_message,
        #     "timestamp": datetime.now().isoformat()
        # })
    
    async def get_connection_status(self) -> Dict[str, Any]:
        """현재 연결 상태 조회"""
        return {
            "is_running": self.is_running,
            "host": self.host,
            "port": self.port,
            "protocol_version": self.protocol_version,
            "connected_clients": await self.connection_manager.get_connected_clients(),
            "server_info": {
                "started_at": "2024-01-01T00:00:00Z",  # TODO: 실제 시작 시간 저장
                "uptime": "0 seconds"  # TODO: 실제 업타임 계산
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Socket Bridge 헬스 체크"""
        try:
            client_count = len(await self.connection_manager.get_connected_clients())
            
            return {
                "status": "healthy" if self.is_running else "stopped",
                "module": "socket_bridge",
                "connected_esp32_count": client_count,
                "server_running": self.is_running,
                "protocol_version": self.protocol_version
            }
        except Exception as e:
            logger.error(f"헬스 체크 실패: {e}")
            return {
                "status": "error",
                "module": "socket_bridge",
                "error": str(e)
            }


# 전역 Socket Bridge 인스턴스
socket_bridge_server: Optional[SocketBridgeServer] = None


async def get_socket_bridge() -> SocketBridgeServer:
    """전역 Socket Bridge 인스턴스 반환"""
    global socket_bridge_server
    if socket_bridge_server is None:
        socket_bridge_server = SocketBridgeServer()
    return socket_bridge_server


async def start_socket_bridge():
    """Socket Bridge 서버 시작 (FastAPI에서 호출)"""
    global socket_bridge_server
    if socket_bridge_server is None:
        socket_bridge_server = SocketBridgeServer()
    
    # 백그라운드에서 서버 시작
    asyncio.create_task(socket_bridge_server.start_server())


async def stop_socket_bridge():
    """Socket Bridge 서버 중지 (FastAPI에서 호출)"""
    global socket_bridge_server
    if socket_bridge_server:
        await socket_bridge_server.stop_server()
        socket_bridge_server = None
