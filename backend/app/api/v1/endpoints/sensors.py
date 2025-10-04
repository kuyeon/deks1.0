"""
센서 데이터 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from loguru import logger

from app.database.database_manager import db_manager

router = APIRouter()


# 응답 모델
class DistanceSensorData(BaseModel):
    """거리 센서 데이터 모델"""
    front: float
    left: float
    right: float
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
    """거리 센서 데이터를 조회합니다."""
    try:
        logger.info("거리 센서 데이터 조회 요청")
        
        # TODO: Socket Bridge를 통해 ESP32에서 실시간 센서 데이터 수신
        # 현재는 모의 데이터를 사용하지만, 실제 구현 시 ESP32에서 받은 데이터를 저장
        
        sensor_data = {
            'front': 25.5,
            'left': 30.2,
            'right': 28.8,
            'unit': 'cm',
            'timestamp': "2024-01-01T12:00:00Z",
            'status': 'normal'
        }
        
        # 센서 데이터를 데이터베이스에 저장 (실제 구현 시)
        # db_manager.save_sensor_data({
        #     'robot_id': 'deks_001',
        #     'front_distance': sensor_data['front'],
        #     'left_distance': sensor_data['left'],
        #     'right_distance': sensor_data['right'],
        #     'drop_detected': False,
        #     'battery_voltage': 3.7,
        #     'temperature': 25.0
        # })
        
        return DistanceSensorData(**sensor_data)
        
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
