"""
센서 데이터 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from loguru import logger
from datetime import datetime

from app.database.database_manager import db_manager
from app.services.socket_bridge import get_socket_bridge

router = APIRouter()


# 응답 모델
class DistanceSensorData(BaseModel):
    """적외선 센서 데이터 모델"""
    front: float  # 전방 적외선 센서 (장애물 감지)
    drop_detection: bool  # 낙하 감지 (적외선 센서)
    unit: str = "cm"
    timestamp: str
    status: str


class PositionData(BaseModel):
    """위치 데이터 모델"""
    x: float
    y: float
    orientation: float
    unit: str = "cm"
    timestamp: str
    accuracy: str


class BatteryData(BaseModel):
    """배터리 데이터 모델"""
    level: int
    voltage: float
    status: str
    estimated_runtime: str
    timestamp: str


class SensorResponse(BaseModel):
    """센서 응답 기본 모델"""
    success: bool
    timestamp: str


@router.get("/distance", response_model=DistanceSensorData)
async def get_distance_sensors():
    """적외선 센서 데이터를 조회합니다."""
    try:
        logger.info("적외선 센서 데이터 조회 요청")
        
        # Socket Bridge를 통해 최신 센서 데이터 조회
        socket_bridge = await get_socket_bridge()
        sensor_manager = socket_bridge.sensor_manager
        
        # 최신 센서 데이터 가져오기
        sensor_data = await sensor_manager.get_latest_sensor_data()
        
        if sensor_data:
            # 실제 센서 데이터 사용
            response_data = {
                'front': sensor_data.get('front_distance', 0),
                'drop_detection': sensor_data.get('drop_detection', False),
                'unit': 'cm',
                'timestamp': sensor_data.get('timestamp', datetime.now().isoformat()),
                'status': 'normal'
            }
        else:
            # 기본값 사용 (센서 데이터가 없는 경우)
            response_data = {
                'front': 25.5,  # 전방 적외선 센서 (5-30cm 감지 범위)
                'drop_detection': False,  # 낙하 감지 (적외선 센서)
                'unit': 'cm',
                'timestamp': datetime.now().isoformat(),
                'status': 'no_data'
            }
        
        return DistanceSensorData(**response_data)
        
    except Exception as e:
        logger.error(f"거리 센서 데이터 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"센서 데이터 조회 실패: {str(e)}")


@router.get("/position", response_model=PositionData)
async def get_position():
    """로봇의 현재 위치를 조회합니다."""
    try:
        logger.info("위치 데이터 조회 요청")
        
        # TODO: Socket Bridge를 통해 ESP32에서 위치 데이터 수신
        
        return PositionData(
            x=10.5,
            y=15.2,
            orientation=45,
            unit="cm",
            timestamp="2024-01-01T12:00:00Z",
            accuracy="high"
        )
        
    except Exception as e:
        logger.error(f"위치 데이터 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"위치 데이터 조회 실패: {str(e)}")


@router.get("/battery", response_model=BatteryData)
async def get_battery_status():
    """배터리 상태를 조회합니다."""
    try:
        logger.info("배터리 상태 조회 요청")
        
        # TODO: Socket Bridge를 통해 ESP32에서 배터리 데이터 수신
        
        return BatteryData(
            level=85,
            voltage=3.7,
            status="good",
            estimated_runtime="2.5 hours",
            timestamp="2024-01-01T12:00:00Z"
        )
        
    except Exception as e:
        logger.error(f"배터리 상태 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"배터리 상태 조회 실패: {str(e)}")


@router.get("/health")
async def sensors_health_check():
    """센서 모듈 헬스 체크"""
    return {
        "status": "healthy",
        "module": "sensors",
        "available_sensors": ["distance", "position", "battery"]
    }
