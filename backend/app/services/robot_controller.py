"""
로봇 제어 모듈
ESP32 로봇의 이동, 정지, 회전 등의 명령을 관리
"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
from loguru import logger

from .connection_manager import ConnectionManager
from app.core.exceptions import (
    RobotNotConnectedException,
    RobotCommandFailedException,
    InvalidParameterException
)


class RobotState(Enum):
    """로봇 상태 열거형"""
    IDLE = "idle"
    MOVING = "moving"
    TURNING = "turning"
    STOPPING = "stopping"
    ERROR = "error"


class MovementType(Enum):
    """이동 타입 열거형"""
    FORWARD = "forward"
    BACKWARD = "backward"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    SPIN = "spin"
    STOP = "stop"


class RobotController:
    """로봇 제어 클래스"""
    
    def __init__(self):
        """로봇 제어기 초기화"""
        self.connection_manager: Optional[ConnectionManager] = None
        self.current_state = RobotState.IDLE
        self.last_command = None
        self.command_history = []
        self.max_command_history = 100
        
        # 안전 설정
        self.max_speed = 100
        self.min_speed = 0
        self.max_distance = 200
        self.min_distance = 0
        
        # 명령 대기열
        self.command_queue = asyncio.Queue()
        self.is_processing_commands = False
        
        logger.info("로봇 제어기 초기화됨")
    
    async def initialize(self):
        """로봇 제어기 초기화 (비동기)"""
        # 명령 처리 루프 시작
        self.is_processing_commands = True
        asyncio.create_task(self._command_processing_loop())
        
        logger.info("로봇 제어기 초기화 완료")
    
    async def cleanup(self):
        """로봇 제어기 정리"""
        self.is_processing_commands = False
        
        # 대기 중인 명령들 정리
        while not self.command_queue.empty():
            try:
                self.command_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        logger.info("로봇 제어기 정리 완료")
    
    def set_connection_manager(self, connection_manager: ConnectionManager):
        """연결 관리자 설정"""
        self.connection_manager = connection_manager
    
    async def _command_processing_loop(self):
        """명령 처리 루프"""
        while self.is_processing_commands:
            try:
                # 명령 대기열에서 명령 가져오기
                command = await asyncio.wait_for(
                    self.command_queue.get(),
                    timeout=1.0
                )
                
                # 명령 실행
                await self._execute_command(command)
                
            except asyncio.TimeoutError:
                # 타임아웃은 정상 (대기 중인 명령이 없음)
                continue
            except Exception as e:
                logger.error(f"명령 처리 루프 오류: {e}")
    
    async def _execute_command(self, command: Dict[str, Any]):
        """명령 실행"""
        try:
            command_type = command.get("type")
            client_id = command.get("client_id")
            
            logger.info(f"명령 실행 시작 - {command_type}")
            
            # 명령 전송
            success = await self._send_command_to_robot(command, client_id)
            
            if success:
                # 명령 히스토리에 추가
                self._add_to_command_history(command)
                logger.info(f"명령 실행 완료 - {command_type}")
            else:
                logger.error(f"명령 실행 실패 - {command_type}")
                
        except Exception as e:
            logger.error(f"명령 실행 중 오류: {e}")
    
    async def _send_command_to_robot(self, command: Dict[str, Any], client_id: Optional[str] = None) -> bool:
        """로봇에 명령 전송"""
        try:
            if not self.connection_manager:
                raise RobotCommandFailedException(
                    command=command.get('type', 'unknown'),
                    reason="연결 관리자가 설정되지 않음"
                )
            
            # 첫 번째 연결된 클라이언트 찾기
            if not client_id:
                client_id = await self.connection_manager.get_first_client()
                if not client_id:
                    raise RobotNotConnectedException()
            
            # 명령 전송
            writer = await self.connection_manager.get_client_writer(client_id)
            if not writer:
                raise RobotNotConnectedException(robot_id=client_id)
            
            # 명령 메시지 생성
            command_message = {
                "type": "command",
                "command": command,
                "timestamp": datetime.now().isoformat(),
                "command_id": f"cmd_{int(datetime.now().timestamp())}"
            }
            
            # 메시지 전송
            message_json = f"{json.dumps(command_message, ensure_ascii=False)}\n"
            writer.write(message_json.encode())
            await writer.drain()
            
            # 메시지 카운트 증가
            await self.connection_manager.increment_message_count(client_id)
            
            logger.debug(f"명령 전송 완료 - {client_id}: {command.get('type')}")
            return True
            
        except (RobotNotConnectedException, RobotCommandFailedException):
            # Deks 예외는 그대로 전파
            raise
        except Exception as e:
            logger.error(f"명령 전송 실패: {e}")
            raise RobotCommandFailedException(
                command=command.get('type', 'unknown'),
                reason=str(e),
                original_exception=e
            )
    
    def _add_to_command_history(self, command: Dict[str, Any]):
        """명령 히스토리에 추가"""
        try:
            command_record = {
                "command": command,
                "timestamp": datetime.now().isoformat(),
                "state": self.current_state.value
            }
            
            self.command_history.append(command_record)
            
            # 히스토리 크기 제한
            if len(self.command_history) > self.max_command_history:
                self.command_history.pop(0)
                
        except Exception as e:
            logger.error(f"명령 히스토리 추가 실패: {e}")
    
    async def move_forward(self, speed: int, distance: int) -> bool:
        """전진 명령"""
        try:
            # 입력 검증 (예외 발생 가능)
            speed = self._validate_speed(speed)
            distance = self._validate_distance(distance)
            
            command = {
                "type": MovementType.FORWARD.value,
                "speed": speed,
                "distance": distance,
                "timestamp": datetime.now().isoformat()
            }
            
            # 명령 대기열에 추가
            await self.command_queue.put(command)
            self.current_state = RobotState.MOVING
            
            logger.info(f"전진 명령 추가됨 - 속도: {speed}, 거리: {distance}")
            return True
            
        except InvalidParameterException:
            # 파라미터 검증 예외는 그대로 전파
            raise
        except Exception as e:
            logger.error(f"전진 명령 실패: {e}")
            raise RobotCommandFailedException(
                command="move_forward",
                reason=str(e),
                original_exception=e
            )
    
    async def move_backward(self, speed: int, distance: int) -> bool:
        """후진 명령"""
        try:
            speed = self._validate_speed(speed)
            distance = self._validate_distance(distance)
            
            command = {
                "type": MovementType.BACKWARD.value,
                "speed": speed,
                "distance": distance,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.command_queue.put(command)
            self.current_state = RobotState.MOVING
            
            logger.info(f"후진 명령 추가됨 - 속도: {speed}, 거리: {distance}")
            return True
            
        except InvalidParameterException:
            raise
        except Exception as e:
            logger.error(f"후진 명령 실패: {e}")
            raise RobotCommandFailedException(
                command="move_backward",
                reason=str(e),
                original_exception=e
            )
    
    async def turn_left(self, angle: int = 90) -> bool:
        """좌회전 명령"""
        try:
            command = {
                "type": MovementType.TURN_LEFT.value,
                "angle": angle,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.command_queue.put(command)
            self.current_state = RobotState.TURNING
            
            logger.info(f"좌회전 명령 추가됨 - 각도: {angle}")
            return True
            
        except Exception as e:
            logger.error(f"좌회전 명령 실패: {e}")
            raise RobotCommandFailedException(
                command="turn_left",
                reason=str(e),
                original_exception=e
            )
    
    async def turn_right(self, angle: int = 90) -> bool:
        """우회전 명령"""
        try:
            command = {
                "type": MovementType.TURN_RIGHT.value,
                "angle": angle,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.command_queue.put(command)
            self.current_state = RobotState.TURNING
            
            logger.info(f"우회전 명령 추가됨 - 각도: {angle}")
            return True
            
        except Exception as e:
            logger.error(f"우회전 명령 실패: {e}")
            raise RobotCommandFailedException(
                command="turn_right",
                reason=str(e),
                original_exception=e
            )
    
    async def spin(self, rotations: int = 1) -> bool:
        """빙글빙글 명령"""
        try:
            command = {
                "type": MovementType.SPIN.value,
                "rotations": rotations,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.command_queue.put(command)
            self.current_state = RobotState.TURNING
            
            logger.info(f"빙글빙글 명령 추가됨 - 회전수: {rotations}")
            return True
            
        except Exception as e:
            logger.error(f"빙글빙글 명령 실패: {e}")
            raise RobotCommandFailedException(
                command="spin",
                reason=str(e),
                original_exception=e
            )
    
    async def stop(self) -> bool:
        """정지 명령"""
        try:
            command = {
                "type": MovementType.STOP.value,
                "timestamp": datetime.now().isoformat()
            }
            
            # 정지 명령은 우선순위가 높으므로 즉시 실행
            await self.command_queue.put(command)
            self.current_state = RobotState.STOPPING
            
            logger.info("정지 명령 추가됨")
            return True
            
        except Exception as e:
            logger.error(f"정지 명령 실패: {e}")
            return False
    
    async def emergency_stop(self) -> bool:
        """비상 정지 명령"""
        try:
            # 대기열의 모든 명령 제거
            while not self.command_queue.empty():
                try:
                    self.command_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            
            command = {
                "type": "emergency_stop",
                "timestamp": datetime.now().isoformat()
            }
            
            # 비상 정지는 즉시 전송
            success = await self._send_command_to_robot(command)
            
            if success:
                self.current_state = RobotState.STOPPING
                logger.warning("비상 정지 실행됨")
            
            return success
            
        except Exception as e:
            logger.error(f"비상 정지 실패: {e}")
            return False
    
    def _validate_speed(self, speed: int) -> int:
        """속도 값 검증"""
        if speed < self.min_speed:
            raise InvalidParameterException(
                parameter_name="speed",
                reason=f"속도는 {self.min_speed}보다 크거나 같아야 합니다 (입력값: {speed})"
            )
        elif speed > self.max_speed:
            raise InvalidParameterException(
                parameter_name="speed",
                reason=f"속도는 {self.max_speed}보다 작거나 같아야 합니다 (입력값: {speed})"
            )
        return speed
    
    def _validate_distance(self, distance: int) -> int:
        """거리 값 검증"""
        if distance < self.min_distance:
            raise InvalidParameterException(
                parameter_name="distance",
                reason=f"거리는 {self.min_distance}보다 크거나 같아야 합니다 (입력값: {distance})"
            )
        elif distance > self.max_distance:
            raise InvalidParameterException(
                parameter_name="distance",
                reason=f"거리는 {self.max_distance}보다 작거나 같아야 합니다 (입력값: {distance})"
            )
        return distance
    
    async def handle_command_result(self, result_data: Dict[str, Any]):
        """ESP32로부터 받은 명령 실행 결과 처리"""
        try:
            command_id = result_data.get("command_id", "unknown")
            success = result_data.get("success", False)
            error_message = result_data.get("error", "")
            
            if not command_id or command_id == "unknown":
                logger.warning(f"command_id가 없는 결과 수신: {result_data}")
                return
            
            if success:
                self.current_state = RobotState.IDLE
                logger.info(f"명령 실행 성공 - {command_id}")
            else:
                self.current_state = RobotState.ERROR
                logger.error(f"명령 실행 실패 - {command_id}: {error_message}")
            
            # 결과를 히스토리에 추가
            result_record = {
                "command_id": command_id,
                "success": success,
                "error": error_message,
                "timestamp": datetime.now().isoformat()
            }
            
            # 최근 명령에 결과 추가
            if self.command_history:
                self.command_history[-1]["result"] = result_record
            
        except Exception as e:
            logger.error(f"명령 결과 처리 중 오류: {e}")
    
    async def update_robot_status(self, status_data: Dict[str, Any]):
        """로봇 상태 업데이트"""
        try:
            new_state = status_data.get("state", self.current_state.value)
            
            # 상태 변경 로깅
            if new_state != self.current_state.value:
                logger.info(f"로봇 상태 변경: {self.current_state.value} -> {new_state}")
                self.current_state = RobotState(new_state)
            
            # 추가 상태 정보 저장
            self.last_status_update = datetime.now()
            self.robot_status_data = status_data
            
        except Exception as e:
            logger.error(f"로봇 상태 업데이트 중 오류: {e}")
    
    async def get_robot_status(self) -> Dict[str, Any]:
        """현재 로봇 상태 조회"""
        try:
            return {
                "current_state": self.current_state.value,
                "last_command": self.last_command,
                "command_queue_size": self.command_queue.qsize(),
                "is_processing_commands": self.is_processing_commands,
                "last_status_update": getattr(self, 'last_status_update', None),
                "robot_status_data": getattr(self, 'robot_status_data', {}),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"로봇 상태 조회 중 오류: {e}")
            return {}
    
    async def get_command_history(self, limit: int = 10) -> list:
        """명령 히스토리 조회"""
        try:
            return self.command_history[-limit:] if limit > 0 else self.command_history
            
        except Exception as e:
            logger.error(f"명령 히스토리 조회 중 오류: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """로봇 제어기 헬스 체크"""
        try:
            return {
                "status": "healthy",
                "module": "robot_controller",
                "current_state": self.current_state.value,
                "command_queue_size": self.command_queue.qsize(),
                "is_processing_commands": self.is_processing_commands,
                "command_history_size": len(self.command_history)
            }
            
        except Exception as e:
            logger.error(f"로봇 제어기 헬스 체크 실패: {e}")
            return {
                "status": "error",
                "module": "robot_controller",
                "error": str(e)
            }
