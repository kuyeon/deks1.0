"""
센서 관리자 모듈 단위 테스트
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta

from app.services.sensor_manager import SensorManager, SensorData


class TestSensorData:
    """센서 데이터 클래스 테스트"""
    
    def test_sensor_data_creation(self):
        """센서 데이터 생성 테스트"""
        timestamp = datetime.now()
        data = SensorData(
            timestamp=timestamp,
            front_distance=25.5,
            drop_detection=False,
            battery_level=85,
            battery_voltage=7.8,
            temperature=23.5,
            humidity=45.2
        )
        
        assert data.timestamp == timestamp
        assert data.front_distance == 25.5
        assert data.drop_detection is False
        assert data.battery_level == 85
        assert data.battery_voltage == 7.8
        assert data.temperature == 23.5
        assert data.humidity == 45.2
    
    def test_sensor_data_optional_fields(self):
        """센서 데이터 선택적 필드 테스트"""
        timestamp = datetime.now()
        data = SensorData(
            timestamp=timestamp,
            front_distance=30.0,
            drop_detection=True
        )
        
        assert data.timestamp == timestamp
        assert data.front_distance == 30.0
        assert data.drop_detection is True
        assert data.battery_level is None
        assert data.battery_voltage is None
        assert data.temperature is None
        assert data.humidity is None


class TestSensorManager:
    """센서 관리자 테스트 클래스"""
    
    @pytest.mark.asyncio
    async def test_sensor_manager_initialization(self):
        """센서 관리자 초기화 테스트"""
        manager = SensorManager()
        
        assert manager.latest_sensor_data is None
        assert manager.sensor_history == []
        assert manager.max_history_size == 1000
        assert manager.front_distance_warning == 10.0
        assert manager.front_distance_danger == 5.0
        assert manager.battery_low_threshold == 20
        assert manager.battery_critical_threshold == 10
        assert manager.data_update_callbacks == []
        assert manager.alert_callbacks == []
        assert manager.streaming_clients == []
    
    @pytest.mark.asyncio
    async def test_initialize_and_cleanup(self):
        """초기화 및 정리 테스트"""
        manager = SensorManager()
        
        # 초기화
        with patch.object(manager, '_cleanup_old_data_loop', new_callable=AsyncMock):
            await manager.initialize()
        
        # 정리
        await manager.cleanup()
        
        assert len(manager.streaming_clients) == 0
        assert len(manager.data_update_callbacks) == 0
        assert len(manager.alert_callbacks) == 0
    
    @pytest.mark.asyncio
    async def test_process_sensor_data_success(self):
        """센서 데이터 처리 성공 테스트"""
        manager = SensorManager()
        
        sensor_data = {
            "front_distance": 25.5,
            "drop_detection": False,
            "battery_level": 85,
            "battery_voltage": 7.8,
            "temperature": 23.5,
            "humidity": 45.2
        }
        
        with patch.object(manager, '_add_to_history') as mock_add:
            with patch.object(manager, '_check_sensor_alerts', new_callable=AsyncMock) as mock_alerts:
                with patch.object(manager, '_notify_data_update', new_callable=AsyncMock) as mock_notify:
                    with patch.object(manager, '_stream_to_clients', new_callable=AsyncMock) as mock_stream:
                        await manager.process_sensor_data(sensor_data)
        
        # 최신 데이터가 설정되었는지 확인
        assert manager.latest_sensor_data is not None
        assert manager.latest_sensor_data.front_distance == 25.5
        assert manager.latest_sensor_data.drop_detection is False
        assert manager.latest_sensor_data.battery_level == 85
        
        # 각 메서드가 호출되었는지 확인
        mock_add.assert_called_once()
        mock_alerts.assert_called_once()
        mock_notify.assert_called_once()
        mock_stream.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_sensor_data_minimal(self):
        """최소 센서 데이터 처리 테스트"""
        manager = SensorManager()
        
        sensor_data = {
            "front_distance": 30.0,
            "drop_detection": True
        }
        
        await manager.process_sensor_data(sensor_data)
        
        assert manager.latest_sensor_data is not None
        assert manager.latest_sensor_data.front_distance == 30.0
        assert manager.latest_sensor_data.drop_detection is True
        assert manager.latest_sensor_data.battery_level is None
    
    @pytest.mark.asyncio
    async def test_process_sensor_data_error(self):
        """센서 데이터 처리 에러 테스트"""
        manager = SensorManager()
        
        # 잘못된 데이터
        invalid_data = "invalid_data"
        
        with patch('app.services.sensor_manager.logger') as mock_logger:
            await manager.process_sensor_data(invalid_data)
        
        mock_logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_add_to_history(self):
        """히스토리에 데이터 추가 테스트"""
        manager = SensorManager()
        
        data = SensorData(
            timestamp=datetime.now(),
            front_distance=25.5,
            drop_detection=False
        )
        
        manager._add_to_history(data)
        
        assert len(manager.sensor_history) == 1
        assert manager.sensor_history[0] == data
    
    @pytest.mark.asyncio
    async def test_add_to_history_size_limit(self):
        """히스토리 크기 제한 테스트"""
        manager = SensorManager()
        manager.max_history_size = 3
        
        # 4개의 데이터 추가
        for i in range(4):
            data = SensorData(
                timestamp=datetime.now(),
                front_distance=float(i),
                drop_detection=False
            )
            manager._add_to_history(data)
        
        assert len(manager.sensor_history) == 3
        # 첫 번째 데이터가 제거되었는지 확인
        assert manager.sensor_history[0].front_distance == 1.0
        assert manager.sensor_history[-1].front_distance == 3.0
    
    @pytest.mark.asyncio
    async def test_check_sensor_alerts_front_distance_danger(self):
        """전방 거리 위험 알림 테스트"""
        manager = SensorManager()
        
        data = SensorData(
            timestamp=datetime.now(),
            front_distance=3.0,  # 위험 거리
            drop_detection=False,
            battery_level=85
        )
        
        with patch.object(manager, '_notify_alert', new_callable=AsyncMock) as mock_notify:
            await manager._check_sensor_alerts(data)
        
        mock_notify.assert_called_once()
        alert = mock_notify.call_args[0][0]
        assert alert["type"] == "danger"
        assert "전방 위험" in alert["message"]
        assert alert["sensor"] == "front_distance"
        assert alert["value"] == 3.0
    
    @pytest.mark.asyncio
    async def test_check_sensor_alerts_front_distance_warning(self):
        """전방 거리 경고 알림 테스트"""
        manager = SensorManager()
        
        data = SensorData(
            timestamp=datetime.now(),
            front_distance=8.0,  # 경고 거리
            drop_detection=False,
            battery_level=85
        )
        
        with patch.object(manager, '_notify_alert', new_callable=AsyncMock) as mock_notify:
            await manager._check_sensor_alerts(data)
        
        mock_notify.assert_called_once()
        alert = mock_notify.call_args[0][0]
        assert alert["type"] == "warning"
        assert "전방 주의" in alert["message"]
    
    @pytest.mark.asyncio
    async def test_check_sensor_alerts_drop_detection(self):
        """낙하 감지 알림 테스트"""
        manager = SensorManager()
        
        data = SensorData(
            timestamp=datetime.now(),
            front_distance=25.0,
            drop_detection=True,  # 낙하 감지
            battery_level=85
        )
        
        with patch.object(manager, '_notify_alert', new_callable=AsyncMock) as mock_notify:
            await manager._check_sensor_alerts(data)
        
        mock_notify.assert_called_once()
        alert = mock_notify.call_args[0][0]
        assert alert["type"] == "danger"
        assert "낙하 위험 감지" in alert["message"]
        assert alert["sensor"] == "drop_detection"
    
    @pytest.mark.asyncio
    async def test_check_sensor_alerts_battery_critical(self):
        """배터리 위험 알림 테스트"""
        manager = SensorManager()
        
        data = SensorData(
            timestamp=datetime.now(),
            front_distance=25.0,
            drop_detection=False,
            battery_level=5  # 위험 수준
        )
        
        with patch.object(manager, '_notify_alert', new_callable=AsyncMock) as mock_notify:
            await manager._check_sensor_alerts(data)
        
        mock_notify.assert_called_once()
        alert = mock_notify.call_args[0][0]
        assert alert["type"] == "critical"
        assert "배터리 위험" in alert["message"]
        assert alert["sensor"] == "battery"
        assert alert["value"] == 5
    
    @pytest.mark.asyncio
    async def test_check_sensor_alerts_battery_low(self):
        """배터리 부족 알림 테스트"""
        manager = SensorManager()
        
        data = SensorData(
            timestamp=datetime.now(),
            front_distance=25.0,
            drop_detection=False,
            battery_level=15  # 부족 수준
        )
        
        with patch.object(manager, '_notify_alert', new_callable=AsyncMock) as mock_notify:
            await manager._check_sensor_alerts(data)
        
        mock_notify.assert_called_once()
        alert = mock_notify.call_args[0][0]
        assert alert["type"] == "warning"
        assert "배터리 부족" in alert["message"]
        assert alert["sensor"] == "battery"
    
    @pytest.mark.asyncio
    async def test_check_sensor_alerts_multiple(self):
        """다중 알림 테스트"""
        manager = SensorManager()
        
        data = SensorData(
            timestamp=datetime.now(),
            front_distance=3.0,  # 위험 거리
            drop_detection=True,  # 낙하 감지
            battery_level=5  # 위험 배터리
        )
        
        with patch.object(manager, '_notify_alert', new_callable=AsyncMock) as mock_notify:
            await manager._check_sensor_alerts(data)
        
        # 3개의 알림이 발생해야 함
        assert mock_notify.call_count == 3
        
        # 호출된 알림들 확인
        calls = mock_notify.call_args_list
        alert_types = [call[0][0]["type"] for call in calls]
        assert "danger" in alert_types  # 전방 거리 위험
        assert "danger" in alert_types  # 낙하 감지
        assert "critical" in alert_types  # 배터리 위험
    
    @pytest.mark.asyncio
    async def test_notify_data_update(self):
        """데이터 업데이트 알림 테스트"""
        manager = SensorManager()
        
        data = SensorData(
            timestamp=datetime.now(),
            front_distance=25.0,
            drop_detection=False
        )
        
        # 콜백 함수들 추가
        sync_callback = Mock()
        async_callback = AsyncMock()
        manager.data_update_callbacks = [sync_callback, async_callback]
        
        await manager._notify_data_update(data)
        
        sync_callback.assert_called_once_with(data)
        async_callback.assert_called_once_with(data)
    
    @pytest.mark.asyncio
    async def test_notify_alert(self):
        """알림 전송 테스트"""
        manager = SensorManager()
        
        alert = {
            "type": "warning",
            "message": "테스트 알림",
            "sensor": "test_sensor",
            "value": 10
        }
        
        # 콜백 함수들 추가
        sync_callback = Mock()
        async_callback = AsyncMock()
        manager.alert_callbacks = [sync_callback, async_callback]
        
        await manager._notify_alert(alert)
        
        sync_callback.assert_called_once_with(alert)
        async_callback.assert_called_once_with(alert)
    
    @pytest.mark.asyncio
    async def test_stream_to_clients_success(self):
        """클라이언트 스트리밍 성공 테스트"""
        manager = SensorManager()
        
        data = SensorData(
            timestamp=datetime.now(),
            front_distance=25.0,
            drop_detection=False,
            battery_level=85
        )
        
        # WebSocket 클라이언트 모킹
        mock_client1 = AsyncMock()
        mock_client1.send_text = AsyncMock()
        mock_client1.__class__.__name__ = "WebSocket"
        
        # StreamWriter 클라이언트 모킹 (hasattr 체크를 통과하도록)
        class MockStreamWriter:
            def __init__(self):
                self.write = Mock()
                self.drain = AsyncMock()
        
        mock_client2 = MockStreamWriter()
        
        manager.streaming_clients = [mock_client1, mock_client2]
        
        await manager._stream_to_clients(data)
        
        # WebSocket 클라이언트
        mock_client1.send_text.assert_called_once()
        call_args = mock_client1.send_text.call_args[0][0]
        stream_data = json.loads(call_args)
        assert stream_data["type"] == "sensor_data"
        assert stream_data["data"]["front_distance"] == 25.0
        
        # StreamWriter 클라이언트
        mock_client2.write.assert_called_once()
        mock_client2.drain.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stream_to_clients_disconnected(self):
        """연결 끊어진 클라이언트 처리 테스트"""
        manager = SensorManager()
        
        data = SensorData(
            timestamp=datetime.now(),
            front_distance=25.0,
            drop_detection=False
        )
        
        # 정상 클라이언트와 연결 끊어진 클라이언트
        mock_client1 = AsyncMock()
        mock_client1.send_text = AsyncMock()
        
        mock_client2 = AsyncMock()
        mock_client2.send_text = AsyncMock(side_effect=Exception("연결 끊어짐"))
        
        manager.streaming_clients = [mock_client1, mock_client2]
        
        await manager._stream_to_clients(data)
        
        # 정상 클라이언트는 전송됨
        mock_client1.send_text.assert_called_once()
        
        # 연결 끊어진 클라이언트는 제거됨
        assert len(manager.streaming_clients) == 1
        assert manager.streaming_clients[0] == mock_client1
    
    @pytest.mark.asyncio
    async def test_cleanup_old_data_loop(self):
        """오래된 데이터 정리 루프 테스트"""
        manager = SensorManager()
        
        # 현재 시간과 25시간 전 데이터 추가
        now = datetime.now()
        old_data = SensorData(
            timestamp=now - timedelta(hours=25),
            front_distance=25.0,
            drop_detection=False
        )
        recent_data = SensorData(
            timestamp=now - timedelta(minutes=30),
            front_distance=30.0,
            drop_detection=False
        )
        
        manager.sensor_history = [old_data, recent_data]
        
        # 정리 루프 실행 (24시간 이전 데이터 제거)
        await manager._cleanup_old_data_loop()
        
        # 오래된 데이터만 제거되었는지 확인
        assert len(manager.sensor_history) == 1
        assert manager.sensor_history[0].front_distance == 30.0
    
    def test_add_data_update_callback(self):
        """데이터 업데이트 콜백 추가 테스트"""
        manager = SensorManager()
        callback = Mock()
        
        manager.add_data_update_callback(callback)
        
        assert callback in manager.data_update_callbacks
    
    def test_add_alert_callback(self):
        """알림 콜백 추가 테스트"""
        manager = SensorManager()
        callback = Mock()
        
        manager.add_alert_callback(callback)
        
        assert callback in manager.alert_callbacks
    
    def test_add_streaming_client(self):
        """스트리밍 클라이언트 추가 테스트"""
        manager = SensorManager()
        client = Mock()
        
        manager.add_streaming_client(client)
        
        assert client in manager.streaming_clients
        
        # 중복 추가 방지 테스트
        manager.add_streaming_client(client)
        assert manager.streaming_clients.count(client) == 1
    
    def test_remove_streaming_client(self):
        """스트리밍 클라이언트 제거 테스트"""
        manager = SensorManager()
        client = Mock()
        
        manager.streaming_clients = [client]
        manager.remove_streaming_client(client)
        
        assert client not in manager.streaming_clients
    
    @pytest.mark.asyncio
    async def test_get_latest_sensor_data(self):
        """최신 센서 데이터 조회 테스트"""
        manager = SensorManager()
        
        # 데이터가 없는 경우
        result = await manager.get_latest_sensor_data()
        assert result is None
        
        # 데이터가 있는 경우
        data = SensorData(
            timestamp=datetime.now(),
            front_distance=25.0,
            drop_detection=False,
            battery_level=85
        )
        manager.latest_sensor_data = data
        
        result = await manager.get_latest_sensor_data()
        
        assert result is not None
        assert result["front_distance"] == 25.0
        assert result["drop_detection"] is False
        assert result["battery_level"] == 85
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_get_sensor_history_no_filter(self):
        """센서 히스토리 조회 - 필터 없음 테스트"""
        manager = SensorManager()
        
        # 히스토리에 데이터 추가
        for i in range(5):
            data = SensorData(
                timestamp=datetime.now() - timedelta(minutes=i),
                front_distance=float(i),
                drop_detection=False
            )
            manager.sensor_history.append(data)
        
        # 제한 없이 조회
        history = await manager.get_sensor_history(limit=0)
        assert len(history) == 5
        
        # 제한하여 조회
        history = await manager.get_sensor_history(limit=3)
        assert len(history) == 3
        assert history[0]["front_distance"] == 2.0  # 뒤에서 3개
    
    @pytest.mark.asyncio
    async def test_get_sensor_history_with_time_filter(self):
        """센서 히스토리 조회 - 시간 필터 테스트"""
        manager = SensorManager()
        
        now = datetime.now()
        
        # 다양한 시간의 데이터 추가
        old_data = SensorData(
            timestamp=now - timedelta(hours=2),
            front_distance=10.0,
            drop_detection=False
        )
        recent_data1 = SensorData(
            timestamp=now - timedelta(minutes=30),
            front_distance=20.0,
            drop_detection=False
        )
        recent_data2 = SensorData(
            timestamp=now - timedelta(minutes=10),
            front_distance=30.0,
            drop_detection=False
        )
        
        manager.sensor_history = [old_data, recent_data1, recent_data2]
        
        # 1시간 이전부터 조회
        start_time = now - timedelta(hours=1)
        history = await manager.get_sensor_history(start_time=start_time)
        
        assert len(history) == 2
        assert history[0]["front_distance"] == 20.0
        assert history[1]["front_distance"] == 30.0
    
    @pytest.mark.asyncio
    async def test_get_sensor_statistics(self):
        """센서 통계 조회 테스트"""
        manager = SensorManager()
        
        # 데이터가 없는 경우
        stats = await manager.get_sensor_statistics()
        assert "message" in stats
        assert "센서 데이터가 없습니다" in stats["message"]
        
        # 1시간 이내 데이터 추가
        now = datetime.now()
        for i in range(10):
            data = SensorData(
                timestamp=now - timedelta(minutes=i*5),
                front_distance=10.0 + i,
                drop_detection=i % 3 == 0,  # 3개마다 낙하 감지
                battery_level=80 - i
            )
            manager.sensor_history.append(data)
        
        stats = await manager.get_sensor_statistics()
        
        assert stats["data_count"] == 10
        assert "time_range" in stats
        assert stats["front_distance"]["min"] == 10.0
        assert stats["front_distance"]["max"] == 19.0
        assert stats["front_distance"]["avg"] == 14.5
        assert stats["drop_detection_count"] == 4  # 0, 3, 6, 9번째
        assert stats["battery_level"]["min"] == 71
        assert stats["battery_level"]["max"] == 80
        assert stats["battery_level"]["avg"] == 75.5
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self):
        """헬스 체크 - 정상 상태 테스트"""
        manager = SensorManager()
        
        # 데이터 및 콜백 설정
        data = SensorData(
            timestamp=datetime.now(),
            front_distance=25.0,
            drop_detection=False
        )
        manager.latest_sensor_data = data
        manager.data_update_callbacks = [Mock()]
        manager.alert_callbacks = [Mock()]
        manager.streaming_clients = [Mock()]
        
        health = await manager.health_check()
        
        assert health["status"] == "healthy"
        assert health["module"] == "sensor_manager"
        assert health["latest_data_available"] is True
        assert health["history_size"] == 0
        assert health["streaming_clients"] == 1
        assert health["update_callbacks"] == 1
        assert health["alert_callbacks"] == 1
    
    @pytest.mark.asyncio
    async def test_health_check_error(self):
        """헬스 체크 - 에러 상태 테스트"""
        manager = SensorManager()
        
        # 에러 발생시키기
        with patch('len', side_effect=Exception("길이 계산 오류")):
            health = await manager.health_check()
        
        assert health["status"] == "error"
        assert health["module"] == "sensor_manager"
        assert "길이 계산 오류" in health["error"]
