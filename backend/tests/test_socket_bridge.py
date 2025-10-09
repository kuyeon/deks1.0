"""
Socket Bridge 모듈 단위 테스트
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from app.services.socket_bridge import SocketBridgeServer


class TestSocketBridgeServer:
    """Socket Bridge 서버 테스트 클래스"""
    
    @pytest.mark.asyncio
    async def test_socket_bridge_initialization(self):
        """Socket Bridge 서버 초기화 테스트"""
        server = SocketBridgeServer(host="127.0.0.1", port=8888)
        
        assert server.host == "127.0.0.1"
        assert server.port == 8888
        assert server.is_running is False
        assert server.server is None
        assert server.protocol_version == "1.0"
        assert server.heartbeat_interval == 30
        assert server.command_timeout == 10
        
        # 하위 모듈들이 초기화되었는지 확인
        assert server.connection_manager is not None
        assert server.robot_controller is not None
        assert server.sensor_manager is not None
    
    @pytest.mark.asyncio
    async def test_start_server_success(self):
        """서버 시작 성공 테스트"""
        server = SocketBridgeServer(host="127.0.0.1", port=8888)
        
        # 모의 서버 생성
        mock_server = AsyncMock()
        mock_server.sockets = [Mock()]
        mock_server.sockets[0].getsockname.return_value = ('127.0.0.1', 8888)
        mock_server.__aenter__ = AsyncMock(return_value=mock_server)
        mock_server.__aexit__ = AsyncMock(return_value=None)
        mock_server.serve_forever = AsyncMock()
        
        with patch('asyncio.start_server', return_value=mock_server):
            with patch.object(server.robot_controller, 'initialize', new_callable=AsyncMock):
                with patch.object(server.sensor_manager, 'initialize', new_callable=AsyncMock):
                    with patch.object(server.connection_manager, 'initialize', new_callable=AsyncMock):
                        try:
                            # 서버 시작 시도 (타임아웃으로 빠르게 종료)
                            task = asyncio.create_task(server.start_server())
                            await asyncio.sleep(0.1)
                            task.cancel()
                            
                            # 서버가 시작되었는지 확인
                            assert server.is_running is True
                            
                        except asyncio.CancelledError:
                            pass
    
    @pytest.mark.asyncio
    async def test_stop_server(self):
        """서버 중지 테스트"""
        server = SocketBridgeServer()
        server.is_running = True
        
        # 모의 서버 설정
        mock_server = AsyncMock()
        mock_server.close = Mock()
        mock_server.wait_closed = AsyncMock()
        server.server = mock_server
        
        with patch.object(server.robot_controller, 'cleanup', new_callable=AsyncMock):
            with patch.object(server.sensor_manager, 'cleanup', new_callable=AsyncMock):
                with patch.object(server.connection_manager, 'cleanup', new_callable=AsyncMock):
                    await server.stop_server()
        
        assert server.is_running is False
        mock_server.close.assert_called_once()
        mock_server.wait_closed.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_client_connection(self):
        """클라이언트 연결 처리 테스트"""
        server = SocketBridgeServer()
        
        # 모의 reader, writer 생성
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_writer.get_extra_info.return_value = ('192.168.1.100', 12345)
        mock_writer.close = Mock()
        mock_writer.wait_closed = AsyncMock()
        
        # 연결 관리자 모킹
        with patch.object(server.connection_manager, 'register_client', new_callable=AsyncMock):
            with patch.object(server.connection_manager, 'unregister_client', new_callable=AsyncMock):
                with patch.object(server, '_perform_handshake', new_callable=AsyncMock):
                    with patch.object(server, '_message_loop', new_callable=AsyncMock):
                        try:
                            await server._handle_client_connection(mock_reader, mock_writer)
                        except Exception:
                            pass
        
        # 연결 등록 및 해제가 호출되었는지 확인
        server.connection_manager.register_client.assert_called_once()
        server.connection_manager.unregister_client.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_perform_handshake_success(self):
        """핸드셰이크 성공 테스트"""
        server = SocketBridgeServer()
        
        # 모의 reader, writer 생성
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        
        # 핸드셰이크 메시지
        handshake_message = {
            "type": "handshake",
            "firmware_version": "1.0.0",
            "robot_id": "deks_001",
            "capabilities": ["movement", "sensors"]
        }
        
        mock_reader.readline = AsyncMock(
            return_value=(json.dumps(handshake_message) + "\n").encode()
        )
        
        with patch.object(server.connection_manager, 'update_client_info', new_callable=AsyncMock):
            with patch.object(server, '_send_message', new_callable=AsyncMock):
                await server._perform_handshake(mock_reader, mock_writer, "test_client")
        
        # 핸드셰이크 응답이 전송되었는지 확인
        server._send_message.assert_called_once()
        call_args = server._send_message.call_args[0]
        response = call_args[1]
        
        assert response["type"] == "handshake_ack"
        assert response["status"] == "success"
        assert response["protocol_version"] == "1.0"
    
    @pytest.mark.asyncio
    async def test_perform_handshake_invalid_message(self):
        """잘못된 핸드셰이크 메시지 테스트"""
        server = SocketBridgeServer()
        
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        
        # 잘못된 메시지
        invalid_message = {"type": "invalid"}
        mock_reader.readline = AsyncMock(
            return_value=(json.dumps(invalid_message) + "\n").encode()
        )
        
        with pytest.raises(Exception, match="잘못된 핸드셰이크 메시지"):
            await server._perform_handshake(mock_reader, mock_writer, "test_client")
    
    @pytest.mark.asyncio
    async def test_perform_handshake_timeout(self):
        """핸드셰이크 타임아웃 테스트"""
        server = SocketBridgeServer()
        
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        
        # 타임아웃 발생시키기
        mock_reader.readline = AsyncMock(side_effect=asyncio.TimeoutError())
        
        with pytest.raises(asyncio.TimeoutError):
            await server._perform_handshake(mock_reader, mock_writer, "test_client")
    
    @pytest.mark.asyncio
    async def test_process_message_sensor_data(self):
        """센서 데이터 메시지 처리 테스트"""
        server = SocketBridgeServer()
        
        message_data = {
            "type": "sensor_data",
            "data": {
                "front_distance": 25.5,
                "drop_detection": False,
                "battery_level": 85
            }
        }
        
        with patch.object(server.sensor_manager, 'process_sensor_data', new_callable=AsyncMock):
            await server._process_message(message_data, "test_client")
        
        server.sensor_manager.process_sensor_data.assert_called_once_with(message_data["data"])
    
    @pytest.mark.asyncio
    async def test_process_message_command_result(self):
        """명령 결과 메시지 처리 테스트"""
        server = SocketBridgeServer()
        
        message_data = {
            "type": "command_result",
            "data": {
                "command_id": "cmd_123",
                "success": True,
                "result": "완료"
            }
        }
        
        with patch.object(server.robot_controller, 'handle_command_result', new_callable=AsyncMock):
            await server._process_message(message_data, "test_client")
        
        server.robot_controller.handle_command_result.assert_called_once_with(message_data["data"])
    
    @pytest.mark.asyncio
    async def test_process_message_robot_status(self):
        """로봇 상태 메시지 처리 테스트"""
        server = SocketBridgeServer()
        
        message_data = {
            "type": "robot_status",
            "data": {
                "state": "idle",
                "battery": 90,
                "position": {"x": 0, "y": 0}
            }
        }
        
        with patch.object(server.robot_controller, 'update_robot_status', new_callable=AsyncMock):
            await server._process_message(message_data, "test_client")
        
        server.robot_controller.update_robot_status.assert_called_once_with(message_data["data"])
    
    @pytest.mark.asyncio
    async def test_process_message_error(self):
        """에러 메시지 처리 테스트"""
        server = SocketBridgeServer()
        
        message_data = {
            "type": "error",
            "data": {
                "error_type": "motor_error",
                "message": "모터 오류 발생"
            }
        }
        
        with patch.object(server, '_handle_error_message', new_callable=AsyncMock):
            await server._process_message(message_data, "test_client")
        
        server._handle_error_message.assert_called_once_with(message_data["data"], "test_client")
    
    @pytest.mark.asyncio
    async def test_process_message_pong(self):
        """핑 응답 메시지 처리 테스트"""
        server = SocketBridgeServer()
        
        message_data = {"type": "pong"}
        
        with patch.object(server.connection_manager, 'update_last_pong', new_callable=AsyncMock):
            await server._process_message(message_data, "test_client")
        
        server.connection_manager.update_last_pong.assert_called_once_with("test_client")
    
    @pytest.mark.asyncio
    async def test_process_message_unknown_type(self):
        """알 수 없는 메시지 타입 처리 테스트"""
        server = SocketBridgeServer()
        
        message_data = {"type": "unknown_type", "data": {}}
        
        # 로거 모킹
        with patch('app.services.socket_bridge.logger') as mock_logger:
            await server._process_message(message_data, "test_client")
        
        mock_logger.warning.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_heartbeat_loop(self):
        """하트비트 루프 테스트"""
        server = SocketBridgeServer()
        server.is_running = True
        
        mock_writer = AsyncMock()
        
        with patch.object(server, '_send_message', new_callable=AsyncMock):
            with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                # 루프가 한 번 실행되도록 설정
                mock_sleep.side_effect = [None, Exception("stop")]
                
                try:
                    await server._heartbeat_loop(mock_writer, "test_client")
                except Exception:
                    pass
        
        # 핑 메시지가 전송되었는지 확인
        server._send_message.assert_called_once()
        call_args = server._send_message.call_args[0]
        ping_message = call_args[1]
        
        assert ping_message["type"] == "ping"
        assert "timestamp" in ping_message
    
    @pytest.mark.asyncio
    async def test_send_message_success(self):
        """메시지 전송 성공 테스트"""
        server = SocketBridgeServer()
        
        mock_writer = AsyncMock()
        message = {"type": "test", "data": "hello"}
        
        await server._send_message(mock_writer, message)
        
        # 메시지가 전송되었는지 확인
        mock_writer.write.assert_called_once()
        mock_writer.drain.assert_called_once()
        
        # 전송된 메시지 내용 확인
        written_data = mock_writer.write.call_args[0][0]
        message_json = json.loads(written_data.decode().strip())
        assert message_json["type"] == "test"
        assert message_json["data"] == "hello"
    
    @pytest.mark.asyncio
    async def test_send_message_failure(self):
        """메시지 전송 실패 테스트"""
        server = SocketBridgeServer()
        
        mock_writer = AsyncMock()
        mock_writer.write.side_effect = Exception("전송 실패")
        
        message = {"type": "test"}
        
        with pytest.raises(Exception, match="전송 실패"):
            await server._send_message(mock_writer, message)
    
    @pytest.mark.asyncio
    async def test_send_command_with_client_id(self):
        """특정 클라이언트에 명령 전송 테스트"""
        server = SocketBridgeServer()
        
        mock_writer = AsyncMock()
        
        with patch.object(server.connection_manager, 'get_client_writer', return_value=mock_writer):
            with patch.object(server, '_send_message', new_callable=AsyncMock):
                command = {"type": "move", "direction": "forward"}
                result = await server.send_command(command, "test_client")
        
        assert result is True
        server._send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_command_no_client(self):
        """연결된 클라이언트가 없을 때 명령 전송 테스트"""
        server = SocketBridgeServer()
        
        with patch.object(server.connection_manager, 'get_first_client', return_value=None):
            command = {"type": "move"}
            result = await server.send_command(command)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_handle_error_message(self):
        """에러 메시지 처리 테스트"""
        server = SocketBridgeServer()
        
        error_data = {
            "error_type": "sensor_error",
            "message": "센서 오류 발생"
        }
        
        with patch('app.services.socket_bridge.logger') as mock_logger:
            await server._handle_error_message(error_data, "test_client")
        
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "ESP32 에러" in error_call
        assert "sensor_error" in error_call
        assert "센서 오류 발생" in error_call
    
    @pytest.mark.asyncio
    async def test_get_connection_status(self):
        """연결 상태 조회 테스트"""
        server = SocketBridgeServer()
        server.is_running = True
        
        with patch.object(server.connection_manager, 'get_connected_clients', 
                         return_value=["client1", "client2"]):
            status = await server.get_connection_status()
        
        assert status["is_running"] is True
        assert status["host"] == "0.0.0.0"
        assert status["port"] == 8888
        assert status["protocol_version"] == "1.0"
        assert len(status["connected_clients"]) == 2
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self):
        """헬스 체크 - 정상 상태 테스트"""
        server = SocketBridgeServer()
        server.is_running = True
        
        with patch.object(server.connection_manager, 'get_connected_clients', 
                         return_value=["client1"]):
            health = await server.health_check()
        
        assert health["status"] == "healthy"
        assert health["module"] == "socket_bridge"
        assert health["connected_esp32_count"] == 1
        assert health["server_running"] is True
    
    @pytest.mark.asyncio
    async def test_health_check_stopped(self):
        """헬스 체크 - 중지 상태 테스트"""
        server = SocketBridgeServer()
        server.is_running = False
        
        health = await server.health_check()
        
        assert health["status"] == "stopped"
        assert health["server_running"] is False
    
    @pytest.mark.asyncio
    async def test_health_check_error(self):
        """헬스 체크 - 에러 상태 테스트"""
        server = SocketBridgeServer()
        
        with patch.object(server.connection_manager, 'get_connected_clients', 
                         side_effect=Exception("연결 오류")):
            health = await server.health_check()
        
        assert health["status"] == "error"
        assert health["module"] == "socket_bridge"
        assert "연결 오류" in health["error"]

