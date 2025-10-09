"""
pytest 설정 및 공통 픽스처
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import AsyncMock, Mock, MagicMock
from typing import Dict, Any

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.socket_bridge import SocketBridgeServer
from app.services.robot_controller import RobotController, RobotState, MovementType
from app.services.sensor_manager import SensorManager, SensorData
from app.services.connection_manager import ConnectionManager
from app.services.chat_nlp import ChatNLP
from app.services.chat_service import ChatService
from app.database.database_manager import DatabaseManager


@pytest.fixture
def event_loop():
    """이벤트 루프 픽스처"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_connection_manager():
    """모의 연결 관리자"""
    manager = AsyncMock(spec=ConnectionManager)
    manager.get_first_client = AsyncMock(return_value="test_client_001")
    manager.get_client_writer = AsyncMock(return_value=AsyncMock())
    manager.register_client = AsyncMock()
    manager.unregister_client = AsyncMock()
    manager.update_client_info = AsyncMock()
    manager.update_last_pong = AsyncMock()
    manager.increment_message_count = AsyncMock()
    manager.get_connected_clients = AsyncMock(return_value=["test_client_001"])
    manager.is_client_alive = AsyncMock(return_value=True)
    return manager


@pytest.fixture
def robot_controller():
    """로봇 제어기 인스턴스"""
    controller = RobotController()
    return controller


@pytest.fixture
def sensor_manager():
    """센서 관리자 인스턴스"""
    manager = SensorManager()
    return manager


@pytest.fixture
async def socket_bridge_server():
    """Socket Bridge 서버 인스턴스"""
    server = SocketBridgeServer(host="127.0.0.1", port=8888)
    return server


@pytest.fixture
async def chat_nlp():
    """Chat NLP 인스턴스"""
    nlp = ChatNLP()
    return nlp


@pytest.fixture
async def chat_service():
    """Chat Service 인스턴스"""
    service = ChatService()
    return service


@pytest.fixture
async def database_manager():
    """데이터베이스 매니저 인스턴스"""
    # 테스트용 임시 데이터베이스 파일
    manager = DatabaseManager(":memory:")
    await manager.initialize()
    return manager


@pytest.fixture
def sample_sensor_data():
    """샘플 센서 데이터"""
    return {
        "front_distance": 25.5,
        "drop_detection": False,
        "battery_level": 85,
        "battery_voltage": 7.8,
        "temperature": 23.5,
        "humidity": 45.2
    }


@pytest.fixture
def sample_robot_command():
    """샘플 로봇 명령"""
    return {
        "type": "forward",
        "speed": 50,
        "distance": 100,
        "timestamp": "2024-01-01T00:00:00"
    }


@pytest.fixture
def sample_esp32_message():
    """샘플 ESP32 메시지"""
    return {
        "type": "sensor_data",
        "data": {
            "front_distance": 30.0,
            "drop_detection": False,
            "battery_level": 90
        },
        "timestamp": "2024-01-01T00:00:00"
    }


@pytest.fixture
def sample_chat_message():
    """샘플 채팅 메시지"""
    return {
        "message": "안녕하세요, 로봇아",
        "user_id": "test_user",
        "timestamp": "2024-01-01T00:00:00"
    }


# 공통 테스트 헬퍼 함수들
class TestHelpers:
    """테스트 헬퍼 클래스"""
    
    @staticmethod
    async def wait_for_async_task(task, timeout=1.0):
        """비동기 태스크 완료 대기"""
        try:
            await asyncio.wait_for(task, timeout=timeout)
        except asyncio.TimeoutError:
            pass
    
    @staticmethod
    def create_mock_writer():
        """모의 StreamWriter 생성"""
        writer = AsyncMock()
        writer.write = Mock()
        writer.drain = AsyncMock()
        writer.close = Mock()
        writer.wait_closed = AsyncMock()
        writer.get_extra_info = Mock(return_value=('127.0.0.1', 12345))
        return writer
    
    @staticmethod
    def create_mock_reader():
        """모의 StreamReader 생성"""
        reader = AsyncMock()
        reader.readline = AsyncMock()
        return reader


@pytest.fixture
def temp_db_manager():
    """임시 데이터베이스 매니저"""
    import tempfile
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    db_manager = DatabaseManager(database_url=f"sqlite:///{temp_db.name}")
    
    yield db_manager
    
    # 정리
    import os
    try:
        os.unlink(temp_db.name)
    except OSError:
        pass

@pytest.fixture
def test_helpers():
    """테스트 헬퍼 인스턴스"""
    return TestHelpers()
