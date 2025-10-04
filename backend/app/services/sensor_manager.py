"""
센서 데이터 관리 모듈
ESP32로부터 받은 센서 데이터를 처리하고 저장
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from loguru import logger


@dataclass
class SensorData:
    """센서 데이터 클래스"""
    timestamp: datetime
    front_distance: float
    drop_detection: bool
    battery_level: Optional[int] = None
    battery_voltage: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None


class SensorManager:
    """센서 데이터 관리자"""
    
    def __init__(self):
        """센서 관리자 초기화"""
        self.latest_sensor_data: Optional[SensorData] = None
        self.sensor_history: List[SensorData] = []
        self.max_history_size = 1000  # 최대 1000개 데이터 저장
        
        # 센서 임계값 설정
        self.front_distance_warning = 10.0  # 10cm 이하면 경고
        self.front_distance_danger = 5.0    # 5cm 이하면 위험
        self.battery_low_threshold = 20      # 배터리 20% 이하면 경고
        self.battery_critical_threshold = 10 # 배터리 10% 이하면 위험
        
        # 데이터 업데이트 콜백들
        self.data_update_callbacks: List[callable] = []
        self.alert_callbacks: List[callable] = []
        
        # 실시간 데이터 스트리밍
        self.streaming_clients: List[Any] = []  # WebSocket 연결들
        
        logger.info("센서 관리자 초기화됨")
    
    async def initialize(self):
        """센서 관리자 초기화 (비동기)"""
        # 센서 데이터 정리 태스크 시작
        asyncio.create_task(self._cleanup_old_data_loop())
        
        logger.info("센서 관리자 초기화 완료")
    
    async def cleanup(self):
        """센서 관리자 정리"""
        # 스트리밍 클라이언트 정리
        self.streaming_clients.clear()
        self.data_update_callbacks.clear()
        self.alert_callbacks.clear()
        
        logger.info("센서 관리자 정리 완료")
    
    async def process_sensor_data(self, sensor_data: Dict[str, Any]):
        """ESP32로부터 받은 센서 데이터 처리"""
        try:
            # 현재 시간
            timestamp = datetime.now()
            
            # 센서 데이터 추출
            front_distance = sensor_data.get("front_distance", 0.0)
            drop_detection = sensor_data.get("drop_detection", False)
            battery_level = sensor_data.get("battery_level")
            battery_voltage = sensor_data.get("battery_voltage")
            temperature = sensor_data.get("temperature")
            humidity = sensor_data.get("humidity")
            
            # SensorData 객체 생성
            data = SensorData(
                timestamp=timestamp,
                front_distance=float(front_distance),
                drop_detection=bool(drop_detection),
                battery_level=battery_level,
                battery_voltage=battery_voltage,
                temperature=temperature,
                humidity=humidity
            )
            
            # 최신 데이터 업데이트
            self.latest_sensor_data = data
            
            # 히스토리에 추가
            self._add_to_history(data)
            
            # 데이터 검증 및 알림
            await self._check_sensor_alerts(data)
            
            # 콜백 함수들 호출
            await self._notify_data_update(data)
            
            # 실시간 스트리밍
            await self._stream_to_clients(data)
            
            logger.debug(f"센서 데이터 처리 완료 - 전방: {front_distance}cm, 낙하감지: {drop_detection}")
            
        except Exception as e:
            logger.error(f"센서 데이터 처리 중 오류: {e}")
    
    def _add_to_history(self, data: SensorData):
        """센서 데이터를 히스토리에 추가"""
        try:
            self.sensor_history.append(data)
            
            # 히스토리 크기 제한
            if len(self.sensor_history) > self.max_history_size:
                self.sensor_history.pop(0)
                
        except Exception as e:
            logger.error(f"센서 히스토리 추가 실패: {e}")
    
    async def _check_sensor_alerts(self, data: SensorData):
        """센서 데이터 기반 알림 확인"""
        try:
            alerts = []
            
            # 전방 거리 경고
            if data.front_distance <= self.front_distance_danger:
                alerts.append({
                    "type": "danger",
                    "message": f"전방 위험! 거리: {data.front_distance}cm",
                    "sensor": "front_distance",
                    "value": data.front_distance
                })
            elif data.front_distance <= self.front_distance_warning:
                alerts.append({
                    "type": "warning",
                    "message": f"전방 주의! 거리: {data.front_distance}cm",
                    "sensor": "front_distance",
                    "value": data.front_distance
                })
            
            # 낙하 감지
            if data.drop_detection:
                alerts.append({
                    "type": "danger",
                    "message": "낙하 위험 감지!",
                    "sensor": "drop_detection",
                    "value": True
                })
            
            # 배터리 경고
            if data.battery_level is not None:
                if data.battery_level <= self.battery_critical_threshold:
                    alerts.append({
                        "type": "critical",
                        "message": f"배터리 위험! {data.battery_level}%",
                        "sensor": "battery",
                        "value": data.battery_level
                    })
                elif data.battery_level <= self.battery_low_threshold:
                    alerts.append({
                        "type": "warning",
                        "message": f"배터리 부족! {data.battery_level}%",
                        "sensor": "battery",
                        "value": data.battery_level
                    })
            
            # 알림 콜백 호출
            for alert in alerts:
                await self._notify_alert(alert)
                
        except Exception as e:
            logger.error(f"센서 알림 확인 중 오류: {e}")
    
    async def _notify_data_update(self, data: SensorData):
        """데이터 업데이트 콜백 호출"""
        try:
            for callback in self.data_update_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    logger.error(f"데이터 업데이트 콜백 오류: {e}")
                    
        except Exception as e:
            logger.error(f"데이터 업데이트 알림 중 오류: {e}")
    
    async def _notify_alert(self, alert: Dict[str, Any]):
        """알림 콜백 호출"""
        try:
            for callback in self.alert_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(alert)
                    else:
                        callback(alert)
                except Exception as e:
                    logger.error(f"알림 콜백 오류: {e}")
                    
        except Exception as e:
            logger.error(f"알림 전송 중 오류: {e}")
    
    async def _stream_to_clients(self, data: SensorData):
        """실시간 스트리밍 클라이언트들에게 데이터 전송"""
        try:
            if not self.streaming_clients:
                return
            
            # 스트리밍 데이터 포맷
            stream_data = {
                "type": "sensor_data",
                "timestamp": data.timestamp.isoformat(),
                "data": {
                    "front_distance": data.front_distance,
                    "drop_detection": data.drop_detection,
                    "battery_level": data.battery_level,
                    "battery_voltage": data.battery_voltage,
                    "temperature": data.temperature,
                    "humidity": data.humidity
                }
            }
            
            # 연결이 끊어진 클라이언트들 제거
            disconnected_clients = []
            
            for client in self.streaming_clients:
                try:
                    if hasattr(client, 'send_text'):
                        await client.send_text(json.dumps(stream_data, ensure_ascii=False))
                    elif hasattr(client, 'write'):
                        message = f"{json.dumps(stream_data, ensure_ascii=False)}\n"
                        client.write(message.encode())
                        await client.drain()
                except Exception as e:
                    logger.debug(f"스트리밍 클라이언트 전송 실패: {e}")
                    disconnected_clients.append(client)
            
            # 연결 끊어진 클라이언트들 제거
            for client in disconnected_clients:
                self.streaming_clients.remove(client)
                
        except Exception as e:
            logger.error(f"실시간 스트리밍 중 오류: {e}")
    
    async def _cleanup_old_data_loop(self):
        """오래된 데이터 정리 루프"""
        while True:
            try:
                await asyncio.sleep(3600)  # 1시간마다 실행
                
                # 24시간 이전 데이터 제거
                cutoff_time = datetime.now() - timedelta(hours=24)
                
                original_size = len(self.sensor_history)
                self.sensor_history = [
                    data for data in self.sensor_history 
                    if data.timestamp > cutoff_time
                ]
                
                removed_count = original_size - len(self.sensor_history)
                if removed_count > 0:
                    logger.info(f"오래된 센서 데이터 정리: {removed_count}개 제거")
                    
            except Exception as e:
                logger.error(f"데이터 정리 루프 오류: {e}")
    
    def add_data_update_callback(self, callback: callable):
        """데이터 업데이트 콜백 추가"""
        self.data_update_callbacks.append(callback)
    
    def add_alert_callback(self, callback: callable):
        """알림 콜백 추가"""
        self.alert_callbacks.append(callback)
    
    def add_streaming_client(self, client: Any):
        """실시간 스트리밍 클라이언트 추가"""
        if client not in self.streaming_clients:
            self.streaming_clients.append(client)
    
    def remove_streaming_client(self, client: Any):
        """실시간 스트리밍 클라이언트 제거"""
        if client in self.streaming_clients:
            self.streaming_clients.remove(client)
    
    async def get_latest_sensor_data(self) -> Optional[Dict[str, Any]]:
        """최신 센서 데이터 조회"""
        try:
            if not self.latest_sensor_data:
                return None
            
            data = self.latest_sensor_data
            return {
                "timestamp": data.timestamp.isoformat(),
                "front_distance": data.front_distance,
                "drop_detection": data.drop_detection,
                "battery_level": data.battery_level,
                "battery_voltage": data.battery_voltage,
                "temperature": data.temperature,
                "humidity": data.humidity
            }
            
        except Exception as e:
            logger.error(f"최신 센서 데이터 조회 중 오류: {e}")
            return None
    
    async def get_sensor_history(self, limit: int = 100, 
                                start_time: Optional[datetime] = None,
                                end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """센서 히스토리 조회"""
        try:
            filtered_data = self.sensor_history
            
            # 시간 필터링
            if start_time:
                filtered_data = [d for d in filtered_data if d.timestamp >= start_time]
            
            if end_time:
                filtered_data = [d for d in filtered_data if d.timestamp <= end_time]
            
            # 개수 제한
            if limit > 0:
                filtered_data = filtered_data[-limit:]
            
            # 딕셔너리 형태로 변환
            result = []
            for data in filtered_data:
                result.append({
                    "timestamp": data.timestamp.isoformat(),
                    "front_distance": data.front_distance,
                    "drop_detection": data.drop_detection,
                    "battery_level": data.battery_level,
                    "battery_voltage": data.battery_voltage,
                    "temperature": data.temperature,
                    "humidity": data.humidity
                })
            
            return result
            
        except Exception as e:
            logger.error(f"센서 히스토리 조회 중 오류: {e}")
            return []
    
    async def get_sensor_statistics(self) -> Dict[str, Any]:
        """센서 통계 정보 조회"""
        try:
            if not self.sensor_history:
                return {"message": "센서 데이터가 없습니다"}
            
            # 최근 1시간 데이터
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_data = [d for d in self.sensor_history if d.timestamp >= one_hour_ago]
            
            if not recent_data:
                return {"message": "최근 1시간 센서 데이터가 없습니다"}
            
            # 통계 계산
            front_distances = [d.front_distance for d in recent_data]
            battery_levels = [d.battery_level for d in recent_data if d.battery_level is not None]
            
            stats = {
                "data_count": len(recent_data),
                "time_range": {
                    "start": recent_data[0].timestamp.isoformat(),
                    "end": recent_data[-1].timestamp.isoformat()
                },
                "front_distance": {
                    "min": min(front_distances),
                    "max": max(front_distances),
                    "avg": sum(front_distances) / len(front_distances)
                },
                "drop_detection_count": sum(1 for d in recent_data if d.drop_detection),
                "battery_level": {
                    "min": min(battery_levels) if battery_levels else None,
                    "max": max(battery_levels) if battery_levels else None,
                    "avg": sum(battery_levels) / len(battery_levels) if battery_levels else None
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"센서 통계 조회 중 오류: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """센서 관리자 헬스 체크"""
        try:
            return {
                "status": "healthy",
                "module": "sensor_manager",
                "latest_data_available": self.latest_sensor_data is not None,
                "history_size": len(self.sensor_history),
                "streaming_clients": len(self.streaming_clients),
                "update_callbacks": len(self.data_update_callbacks),
                "alert_callbacks": len(self.alert_callbacks)
            }
            
        except Exception as e:
            logger.error(f"센서 관리자 헬스 체크 실패: {e}")
            return {
                "status": "error",
                "module": "sensor_manager",
                "error": str(e)
            }
