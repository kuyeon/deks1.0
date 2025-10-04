"""
로봇 제어 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
from loguru import logger
import time
from datetime import datetime

from app.core.config import get_settings
from app.database.database_manager import db_manager
from app.services.socket_bridge import get_socket_bridge

router = APIRouter()
settings = get_settings()


# 요청/응답 모델
class MoveForwardRequest(BaseModel):
    """전진 명령 요청 모델"""
    speed: int = 50
    distance: int = 100
    user_id: str = "default_user"


class TurnRequest(BaseModel):
    """회전 명령 요청 모델"""
    direction: str  # "left" 또는 "right"
    angle: int = 90
    speed: int = 30
    user_id: str = "default_user"


class StopRequest(BaseModel):
    """정지 명령 요청 모델"""
    user_id: str = "default_user"


class SpinRequest(BaseModel):
    """빙글빙글 명령 요청 모델"""
    rotations: int = 1
    user_id: str = "default_user"


class RobotStatus(BaseModel):
    """로봇 상태 모델"""
    position: dict
    orientation: Optional[float] = None
    battery: int
    is_moving: bool
    safety_mode: str
    sensors: dict
    led_expression: Optional[str] = None
    buzzer_active: bool = False
    timestamp: str


class CommandResponse(BaseModel):
    """명령 응답 모델"""
    success: bool
    command_id: str
    message: str
    timestamp: str
    robot_status: Optional[RobotStatus] = None


@router.post("/move/forward", response_model=CommandResponse)
async def move_forward(request: MoveForwardRequest):
    """로봇을 앞으로 이동시킵니다."""
    try:
        logger.info(f"전진 명령 수신: 속도={request.speed}, 거리={request.distance}")
        
        # Socket Bridge를 통해 ESP32에 명령 전송
        socket_bridge = await get_socket_bridge()
        robot_controller = socket_bridge.robot_controller
        
        command_id = f"cmd_{int(datetime.now().timestamp())}"
        
        # 로봇 제어기에게 전진 명령 전달
        success = await robot_controller.move_forward(request.speed, request.distance)
        
        if not success:
            raise HTTPException(status_code=500, detail="로봇 제어기에 명령 전달 실패")
        
        # 명령 실행 로그 저장
        log_data = {
            'command_id': command_id,
            'command_type': 'move_forward',
            'parameters': {
                'speed': request.speed,
                'distance': request.distance
            },
            'user_id': request.user_id,
            'robot_id': 'deks_001',
            'success': True,
            'execution_time': 0.0,  # 실제 구현 시 측정
            'error_message': None
        }
        db_manager.save_command_execution_log(log_data)
        
        return CommandResponse(
            success=True,
            command_id=command_id,
            message="전진 명령을 실행합니다",
            timestamp=datetime.now().isoformat(),
            robot_status=RobotStatus(
                position={"x": 0, "y": 0},
                battery=85,
                is_moving=True,
                safety_mode="normal",
                sensors={
                    "front_distance": 25.5,
                    "drop_detected": False
                },
                timestamp=datetime.now().isoformat()
            )
        )
        
    except Exception as e:
        logger.error(f"전진 명령 실행 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"전진 명령 실행 실패: {str(e)}")


@router.post("/move/turn", response_model=CommandResponse)
async def turn(request: TurnRequest):
    """로봇을 회전시킵니다."""
    try:
        if request.direction not in ["left", "right"]:
            raise HTTPException(status_code=400, detail="방향은 'left' 또는 'right'여야 합니다")
        
        logger.info(f"회전 명령 수신: 방향={request.direction}, 각도={request.angle}")
        
        # Socket Bridge를 통해 ESP32에 명령 전송
        socket_bridge = await get_socket_bridge()
        robot_controller = socket_bridge.robot_controller
        
        command_id = f"cmd_{int(datetime.now().timestamp())}"
        
        # 방향에 따른 회전 명령 실행
        if request.direction == "left":
            success = await robot_controller.turn_left(request.angle)
        else:
            success = await robot_controller.turn_right(request.angle)
        
        if not success:
            raise HTTPException(status_code=500, detail="로봇 제어기에 명령 전달 실패")
        
        return CommandResponse(
            success=True,
            command_id=command_id,
            message=f"{request.direction}으로 {request.angle}도 회전합니다",
            timestamp=datetime.now().isoformat(),
            robot_status=RobotStatus(
                position={"x": 0, "y": 0},
                orientation=request.angle if request.direction == "right" else -request.angle,
                battery=84,
                is_moving=False,
                safety_mode="normal",
                sensors={
                    "front_distance": 25.5,
                    "drop_detected": False
                },
                timestamp=datetime.now().isoformat()
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"회전 명령 실행 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"회전 명령 실행 실패: {str(e)}")


@router.post("/stop", response_model=CommandResponse)
async def stop(request: StopRequest):
    """로봇을 정지시킵니다."""
    try:
        logger.info("정지 명령 수신")
        
        # Socket Bridge를 통해 ESP32에 명령 전송
        socket_bridge = await get_socket_bridge()
        robot_controller = socket_bridge.robot_controller
        
        command_id = f"cmd_{int(datetime.now().timestamp())}"
        
        # 정지 명령 실행
        success = await robot_controller.stop()
        
        if not success:
            raise HTTPException(status_code=500, detail="로봇 제어기에 명령 전달 실패")
        
        return CommandResponse(
            success=True,
            command_id=command_id,
            message="로봇을 정지합니다",
            timestamp=datetime.now().isoformat(),
            robot_status=RobotStatus(
                position={"x": 0, "y": 0},
                battery=84,
                is_moving=False,
                safety_mode="normal",
                sensors={
                    "front_distance": 25.5,
                    "drop_detected": False
                },
                timestamp=datetime.now().isoformat()
            )
        )
        
    except Exception as e:
        logger.error(f"정지 명령 실행 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"정지 명령 실행 실패: {str(e)}")


@router.post("/spin", response_model=CommandResponse)
async def spin(request: SpinRequest):
    """로봇을 빙글빙글 회전시킵니다."""
    try:
        logger.info(f"빙글빙글 명령 수신: 회전수={request.rotations}")
        
        # Socket Bridge를 통해 ESP32에 명령 전송
        socket_bridge = await get_socket_bridge()
        robot_controller = socket_bridge.robot_controller
        
        command_id = f"cmd_{int(datetime.now().timestamp())}"
        
        # 빙글빙글 명령 실행
        success = await robot_controller.spin(request.rotations)
        
        if not success:
            raise HTTPException(status_code=500, detail="로봇 제어기에 명령 전달 실패")
        
        return CommandResponse(
            success=True,
            command_id=command_id,
            message=f"{request.rotations}번 빙글빙글 회전합니다",
            timestamp=datetime.now().isoformat(),
            robot_status=RobotStatus(
                position={"x": 0, "y": 0},
                battery=84,
                is_moving=False,
                safety_mode="normal",
                sensors={
                    "front_distance": 25.5,
                    "drop_detected": False
                },
                timestamp=datetime.now().isoformat()
            )
        )
        
    except Exception as e:
        logger.error(f"빙글빙글 명령 실행 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"빙글빙글 명령 실행 실패: {str(e)}")


@router.get("/status", response_model=RobotStatus)
async def get_robot_status():
    """로봇의 현재 상태를 조회합니다."""
    try:
        logger.info("로봇 상태 조회 요청")
        
        # Socket Bridge를 통해 로봇 상태 조회
        socket_bridge = await get_socket_bridge()
        robot_controller = socket_bridge.robot_controller
        sensor_manager = socket_bridge.sensor_manager
        
        # 로봇 제어기 상태 조회
        robot_status = await robot_controller.get_robot_status()
        
        # 최신 센서 데이터 조회
        sensor_data = await sensor_manager.get_latest_sensor_data()
        
        # 기본값 설정
        position = {"x": 0, "y": 0}
        orientation = 0
        battery = 85
        is_moving = robot_status.get("current_state") == "moving"
        safety_mode = "normal"
        sensors = {
            "front_distance": sensor_data.get("front_distance", 0) if sensor_data else 0,
            "drop_detected": sensor_data.get("drop_detection", False) if sensor_data else False
        }
        
        return RobotStatus(
            position=position,
            orientation=orientation,
            battery=battery,
            is_moving=is_moving,
            safety_mode=safety_mode,
            sensors=sensors,
            led_expression="normal",
            buzzer_active=False,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"로봇 상태 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"로봇 상태 조회 실패: {str(e)}")


@router.get("/robots/status")
async def get_connected_robots():
    """연결된 로봇들의 상태를 조회합니다."""
    try:
        logger.info("연결된 로봇 상태 조회 요청")
        
        # Socket Bridge에서 연결된 로봇 정보 조회
        socket_bridge = await get_socket_bridge()
        connection_manager = socket_bridge.connection_manager
        
        connected_clients = await connection_manager.get_connected_clients()
        connection_stats = await connection_manager.get_connection_statistics()
        
        # 연결된 로봇 정보 변환
        connected_robots = []
        for client in connected_clients:
            client_id = client["client_id"]
            ip_address = client_id.split(":")[0] if ":" in client_id else client_id
            
            robot_info = {
                "robot_id": "deks_001",  # 기본 로봇 ID
                "ip_address": ip_address,
                "port": 8888,  # Socket Bridge 포트
                "status": "connected",
                "last_seen": client["last_activity"],
                "battery_level": 85,  # 기본값
                "connection_quality": "good",
                "connected_duration": client["connected_duration"],
                "message_count": client["message_count"],
                "error_count": client["error_count"]
            }
            connected_robots.append(robot_info)
        
        return {
            "success": True,
            "connected_robots": connected_robots,
            "total_connected": len(connected_robots),
            "socket_bridge_status": "active",
            "connection_statistics": connection_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"연결된 로봇 상태 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"로봇 상태 조회 실패: {str(e)}")


@router.get("/robots/{robot_id}/status")
async def get_robot_detailed_status(robot_id: str):
    """특정 로봇의 상세 상태를 조회합니다."""
    try:
        logger.info(f"로봇 {robot_id} 상세 상태 조회 요청")
        
        # TODO: Socket Bridge에서 특정 로봇의 상세 정보 조회
        
        return {
            "success": True,
            "robot": {
                "robot_id": robot_id,
                "ip_address": "192.168.1.100",
                "port": settings.robot_tcp_port,
                "status": "connected",
                "connection_time": "2024-01-01T11:30:00Z",
                "last_seen": "2024-01-01T12:00:00Z",
                "commands_sent": 15,
                "commands_completed": 14,
                "commands_failed": 1,
                "battery_level": 85,
                "connection_quality": "excellent",
                "socket_bridge_metrics": {
                    "avg_response_time": 8.5,
                    "packet_loss": 0.0,
                    "last_ping": "2024-01-01T12:00:00Z"
                }
            },
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"로봇 {robot_id} 상세 상태 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"로봇 상세 상태 조회 실패: {str(e)}")
