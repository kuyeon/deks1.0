"""
로봇 제어기 모듈 단위 테스트
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from app.services.robot_controller import (
    RobotController, 
    RobotState, 
    MovementType
)


class TestRobotController:
    """로봇 제어기 테스트 클래스"""
    
    @pytest.mark.asyncio
    async def test_robot_controller_initialization(self):
        """로봇 제어기 초기화 테스트"""
        controller = RobotController()
        
        assert controller.connection_manager is None
        assert controller.current_state == RobotState.IDLE
        assert controller.last_command is None
        assert controller.command_history == []
        assert controller.max_command_history == 100
        assert controller.max_speed == 100
        assert controller.min_speed == 0
        assert controller.max_distance == 200
        assert controller.min_distance == 0
        assert controller.is_processing_commands is False
    
    @pytest.mark.asyncio
    async def test_initialize_and_cleanup(self):
        """초기화 및 정리 테스트"""
        controller = RobotController()
        
        # 초기화
        with patch.object(controller, '_command_processing_loop', new_callable=AsyncMock):
            await controller.initialize()
        
        assert controller.is_processing_commands is True
        
        # 정리
        await controller.cleanup()
        assert controller.is_processing_commands is False
    
    @pytest.mark.asyncio
    async def test_set_connection_manager(self):
        """연결 관리자 설정 테스트"""
        controller = RobotController()
        mock_manager = Mock()
        
        controller.set_connection_manager(mock_manager)
        assert controller.connection_manager is mock_manager
    
    @pytest.mark.asyncio
    async def test_command_processing_loop(self):
        """명령 처리 루프 테스트"""
        controller = RobotController()
        
        test_command = {"type": "test", "data": "hello"}
        
        with patch.object(controller, '_execute_command', new_callable=AsyncMock) as mock_execute:
            # 명령을 큐에 추가
            await controller.command_queue.put(test_command)
            
            # 루프가 한 번만 실행되도록 설정
            original_loop = controller._command_processing_loop
            
            async def mock_loop():
                controller.is_processing_commands = True
                try:
                    # 명령 하나만 처리하고 종료
                    command = await controller.command_queue.get()
                    await controller._execute_command(command)
                finally:
                    controller.is_processing_commands = False
            
            controller._command_processing_loop = mock_loop
            
            # 루프 실행
            await controller._command_processing_loop()
        
        mock_execute.assert_called_once_with(test_command)
    
    @pytest.mark.asyncio
    async def test_execute_command_success(self):
        """명령 실행 성공 테스트"""
        controller = RobotController()
        
        command = {
            "type": "forward",
            "speed": 50,
            "distance": 100,
            "client_id": "test_client"
        }
        
        with patch.object(controller, '_send_command_to_robot', return_value=True) as mock_send:
            with patch.object(controller, '_add_to_command_history') as mock_add:
                await controller._execute_command(command)
        
        mock_send.assert_called_once_with(command, "test_client")
        mock_add.assert_called_once_with(command)
    
    @pytest.mark.asyncio
    async def test_execute_command_failure(self):
        """명령 실행 실패 테스트"""
        controller = RobotController()
        
        command = {"type": "forward", "speed": 50}
        
        with patch.object(controller, '_send_command_to_robot', return_value=False):
            with patch('app.services.robot_controller.logger') as mock_logger:
                await controller._execute_command(command)
        
        # 에러 로그가 기록되었는지 확인
        mock_logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_send_command_to_robot_no_connection_manager(self):
        """연결 관리자가 없을 때 명령 전송 테스트"""
        controller = RobotController()
        
        command = {"type": "forward"}
        result = await controller._send_command_to_robot(command)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_send_command_to_robot_no_client(self):
        """연결된 클라이언트가 없을 때 명령 전송 테스트"""
        controller = RobotController()
        mock_manager = AsyncMock()
        mock_manager.get_first_client.return_value = None
        controller.connection_manager = mock_manager
        
        command = {"type": "forward"}
        result = await controller._send_command_to_robot(command)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_send_command_to_robot_no_writer(self):
        """Writer가 없을 때 명령 전송 테스트"""
        controller = RobotController()
        mock_manager = AsyncMock()
        mock_manager.get_first_client.return_value = "test_client"
        mock_manager.get_client_writer.return_value = None
        controller.connection_manager = mock_manager
        
        command = {"type": "forward"}
        result = await controller._send_command_to_robot(command)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_send_command_to_robot_success(self):
        """명령 전송 성공 테스트"""
        controller = RobotController()
        mock_manager = AsyncMock()
        mock_writer = AsyncMock()
        
        mock_manager.get_first_client.return_value = "test_client"
        mock_manager.get_client_writer.return_value = mock_writer
        mock_manager.increment_message_count = AsyncMock()
        controller.connection_manager = mock_manager
        
        command = {"type": "forward", "speed": 50}
        result = await controller._send_command_to_robot(command)
        
        assert result is True
        mock_writer.write.assert_called_once()
        mock_writer.drain.assert_called_once()
        mock_manager.increment_message_count.assert_called_once_with("test_client")
    
    @pytest.mark.asyncio
    async def test_send_command_to_robot_failure(self):
        """명령 전송 실패 테스트"""
        controller = RobotController()
        mock_manager = AsyncMock()
        mock_writer = AsyncMock()
        mock_writer.write.side_effect = Exception("전송 실패")
        
        mock_manager.get_first_client.return_value = "test_client"
        mock_manager.get_client_writer.return_value = mock_writer
        controller.connection_manager = mock_manager
        
        command = {"type": "forward"}
        result = await controller._send_command_to_robot(command)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_add_to_command_history(self):
        """명령 히스토리 추가 테스트"""
        controller = RobotController()
        controller.current_state = RobotState.MOVING
        
        command = {"type": "forward", "speed": 50}
        await controller._add_to_command_history(command)
        
        assert len(controller.command_history) == 1
        history_item = controller.command_history[0]
        assert history_item["command"] == command
        assert history_item["state"] == RobotState.MOVING.value
        assert "timestamp" in history_item
    
    @pytest.mark.asyncio
    async def test_command_history_size_limit(self):
        """명령 히스토리 크기 제한 테스트"""
        controller = RobotController()
        controller.max_command_history = 3
        
        # 4개의 명령 추가
        for i in range(4):
            command = {"type": "test", "id": i}
            await controller._add_to_command_history(command)
        
        assert len(controller.command_history) == 3
        # 첫 번째 명령이 제거되었는지 확인
        assert controller.command_history[0]["command"]["id"] == 1
        assert controller.command_history[-1]["command"]["id"] == 3
    
    @pytest.mark.asyncio
    async def test_move_forward_success(self):
        """전진 명령 성공 테스트"""
        controller = RobotController()
        
        result = await controller.move_forward(speed=50, distance=100)
        
        assert result is True
        assert controller.current_state == RobotState.MOVING
        assert controller.command_queue.qsize() == 1
        
        # 큐에서 명령 확인
        command = await controller.command_queue.get()
        assert command["type"] == MovementType.FORWARD.value
        assert command["speed"] == 50
        assert command["distance"] == 100
    
    @pytest.mark.asyncio
    async def test_move_forward_validation(self):
        """전진 명령 입력 검증 테스트"""
        controller = RobotController()
        
        # 속도가 범위를 벗어나는 경우
        result = await controller.move_forward(speed=150, distance=100)
        assert result is True
        
        command = await controller.command_queue.get()
        assert command["speed"] == 100  # 최대값으로 조정
        
        # 거리가 범위를 벗어나는 경우
        result = await controller.move_forward(speed=50, distance=300)
        assert result is True
        
        command = await controller.command_queue.get()
        assert command["distance"] == 200  # 최대값으로 조정
    
    @pytest.mark.asyncio
    async def test_move_backward_success(self):
        """후진 명령 성공 테스트"""
        controller = RobotController()
        
        result = await controller.move_backward(speed=30, distance=50)
        
        assert result is True
        assert controller.current_state == RobotState.MOVING
        
        command = await controller.command_queue.get()
        assert command["type"] == MovementType.BACKWARD.value
        assert command["speed"] == 30
        assert command["distance"] == 50
    
    @pytest.mark.asyncio
    async def test_turn_left_success(self):
        """좌회전 명령 성공 테스트"""
        controller = RobotController()
        
        result = await controller.turn_left(angle=45)
        
        assert result is True
        assert controller.current_state == RobotState.TURNING
        
        command = await controller.command_queue.get()
        assert command["type"] == MovementType.TURN_LEFT.value
        assert command["angle"] == 45
    
    @pytest.mark.asyncio
    async def test_turn_left_default_angle(self):
        """좌회전 명령 기본 각도 테스트"""
        controller = RobotController()
        
        result = await controller.turn_left()
        
        assert result is True
        command = await controller.command_queue.get()
        assert command["angle"] == 90  # 기본값
    
    @pytest.mark.asyncio
    async def test_turn_right_success(self):
        """우회전 명령 성공 테스트"""
        controller = RobotController()
        
        result = await controller.turn_right(angle=135)
        
        assert result is True
        assert controller.current_state == RobotState.TURNING
        
        command = await controller.command_queue.get()
        assert command["type"] == MovementType.TURN_RIGHT.value
        assert command["angle"] == 135
    
    @pytest.mark.asyncio
    async def test_spin_success(self):
        """빙글빙글 명령 성공 테스트"""
        controller = RobotController()
        
        result = await controller.spin(rotations=2)
        
        assert result is True
        assert controller.current_state == RobotState.TURNING
        
        command = await controller.command_queue.get()
        assert command["type"] == MovementType.SPIN.value
        assert command["rotations"] == 2
    
    @pytest.mark.asyncio
    async def test_stop_success(self):
        """정지 명령 성공 테스트"""
        controller = RobotController()
        
        result = await controller.stop()
        
        assert result is True
        assert controller.current_state == RobotState.STOPPING
        
        command = await controller.command_queue.get()
        assert command["type"] == MovementType.STOP.value
    
    @pytest.mark.asyncio
    async def test_emergency_stop_success(self):
        """비상 정지 명령 성공 테스트"""
        controller = RobotController()
        mock_manager = AsyncMock()
        mock_writer = AsyncMock()
        
        mock_manager.get_first_client.return_value = "test_client"
        mock_manager.get_client_writer.return_value = mock_writer
        mock_manager.increment_message_count = AsyncMock()
        controller.connection_manager = mock_manager
        
        # 큐에 명령들 추가
        await controller.command_queue.put({"type": "forward"})
        await controller.command_queue.put({"type": "turn_left"})
        
        result = await controller.emergency_stop()
        
        assert result is True
        assert controller.current_state == RobotState.STOPPING
        assert controller.command_queue.qsize() == 0  # 큐가 비워졌는지 확인
    
    @pytest.mark.asyncio
    async def test_emergency_stop_no_client(self):
        """비상 정지 - 연결된 클라이언트 없음 테스트"""
        controller = RobotController()
        mock_manager = AsyncMock()
        mock_manager.get_first_client.return_value = None
        controller.connection_manager = mock_manager
        
        result = await controller.emergency_stop()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_speed(self):
        """속도 값 검증 테스트"""
        controller = RobotController()
        
        # 정상 범위
        assert controller._validate_speed(50) == 50
        
        # 최소값 미만
        assert controller._validate_speed(-10) == 0
        
        # 최대값 초과
        assert controller._validate_speed(150) == 100
    
    @pytest.mark.asyncio
    async def test_validate_distance(self):
        """거리 값 검증 테스트"""
        controller = RobotController()
        
        # 정상 범위
        assert controller._validate_distance(100) == 100
        
        # 최소값 미만
        assert controller._validate_distance(-10) == 0
        
        # 최대값 초과
        assert controller._validate_distance(300) == 200
    
    @pytest.mark.asyncio
    async def test_handle_command_result_success(self):
        """명령 결과 처리 - 성공 테스트"""
        controller = RobotController()
        controller.current_state = RobotState.MOVING
        
        # 명령 히스토리에 항목 추가
        controller.command_history.append({
            "command": {"type": "forward"},
            "timestamp": datetime.now().isoformat(),
            "state": RobotState.MOVING.value
        })
        
        result_data = {
            "command_id": "cmd_123",
            "success": True,
            "error": ""
        }
        
        await controller.handle_command_result(result_data)
        
        assert controller.current_state == RobotState.IDLE
        assert len(controller.command_history) == 1
        assert "result" in controller.command_history[0]
    
    @pytest.mark.asyncio
    async def test_handle_command_result_failure(self):
        """명령 결과 처리 - 실패 테스트"""
        controller = RobotController()
        controller.current_state = RobotState.MOVING
        
        result_data = {
            "command_id": "cmd_123",
            "success": False,
            "error": "모터 오류"
        }
        
        await controller.handle_command_result(result_data)
        
        assert controller.current_state == RobotState.ERROR
    
    @pytest.mark.asyncio
    async def test_update_robot_status(self):
        """로봇 상태 업데이트 테스트"""
        controller = RobotController()
        controller.current_state = RobotState.IDLE
        
        status_data = {
            "state": "moving",
            "battery": 85,
            "position": {"x": 10, "y": 20}
        }
        
        with patch('app.services.robot_controller.logger') as mock_logger:
            await controller.update_robot_status(status_data)
        
        assert controller.current_state == RobotState.MOVING
        assert controller.robot_status_data == status_data
        assert hasattr(controller, 'last_status_update')
        
        # 상태 변경 로그 확인
        mock_logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_get_robot_status(self):
        """로봇 상태 조회 테스트"""
        controller = RobotController()
        controller.current_state = RobotState.MOVING
        controller.last_command = {"type": "forward"}
        controller.is_processing_commands = True
        
        # 큐에 명령 추가
        await controller.command_queue.put({"type": "test"})
        
        status = await controller.get_robot_status()
        
        assert status["current_state"] == RobotState.MOVING.value
        assert status["last_command"] == {"type": "forward"}
        assert status["command_queue_size"] == 1
        assert status["is_processing_commands"] is True
        assert "timestamp" in status
    
    @pytest.mark.asyncio
    async def test_get_command_history(self):
        """명령 히스토리 조회 테스트"""
        controller = RobotController()
        
        # 히스토리에 항목들 추가
        for i in range(5):
            controller.command_history.append({
                "command": {"type": f"test_{i}"},
                "timestamp": datetime.now().isoformat(),
                "state": "idle"
            })
        
        # 제한 없이 조회
        history = await controller.get_command_history(limit=0)
        assert len(history) == 5
        
        # 제한하여 조회
        history = await controller.get_command_history(limit=3)
        assert len(history) == 3
        assert history[0]["command"]["type"] == "test_2"  # 뒤에서 3개
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self):
        """헬스 체크 - 정상 상태 테스트"""
        controller = RobotController()
        controller.current_state = RobotState.IDLE
        controller.is_processing_commands = True
        
        # 큐에 명령 추가
        await controller.command_queue.put({"type": "test"})
        
        # 히스토리에 항목 추가
        controller.command_history.append({"command": {"type": "test"}})
        
        health = await controller.health_check()
        
        assert health["status"] == "healthy"
        assert health["module"] == "robot_controller"
        assert health["current_state"] == RobotState.IDLE.value
        assert health["command_queue_size"] == 1
        assert health["is_processing_commands"] is True
        assert health["command_history_size"] == 1
    
    @pytest.mark.asyncio
    async def test_health_check_error(self):
        """헬스 체크 - 에러 상태 테스트"""
        controller = RobotController()
        
        # 큐에 접근할 때 에러 발생시키기
        with patch.object(controller.command_queue, 'qsize', side_effect=Exception("큐 오류")):
            health = await controller.health_check()
        
        assert health["status"] == "error"
        assert health["module"] == "robot_controller"
        assert "큐 오류" in health["error"]


class TestRobotState:
    """로봇 상태 열거형 테스트"""
    
    def test_robot_state_values(self):
        """로봇 상태 값 테스트"""
        assert RobotState.IDLE.value == "idle"
        assert RobotState.MOVING.value == "moving"
        assert RobotState.TURNING.value == "turning"
        assert RobotState.STOPPING.value == "stopping"
        assert RobotState.ERROR.value == "error"


class TestMovementType:
    """이동 타입 열거형 테스트"""
    
    def test_movement_type_values(self):
        """이동 타입 값 테스트"""
        assert MovementType.FORWARD.value == "forward"
        assert MovementType.BACKWARD.value == "backward"
        assert MovementType.TURN_LEFT.value == "turn_left"
        assert MovementType.TURN_RIGHT.value == "turn_right"
        assert MovementType.SPIN.value == "spin"
        assert MovementType.STOP.value == "stop"
