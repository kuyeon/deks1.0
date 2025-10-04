"""
WebSocket 실시간 통신 API 엔드포인트
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import asyncio
from loguru import logger

router = APIRouter()


class ConnectionManager:
    """WebSocket 연결 관리자"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.robot_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, connection_type: str = "client"):
        """WebSocket 연결을 수락합니다."""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if connection_type == "robot":
            # 로봇 연결인 경우 특별 처리
            await self.handle_robot_connection(websocket)
        else:
            logger.info(f"클라이언트 연결됨. 총 연결 수: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """WebSocket 연결을 종료합니다."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # 로봇 연결에서도 제거
        robot_id = None
        for rid, ws in self.robot_connections.items():
            if ws == websocket:
                robot_id = rid
                break
        
        if robot_id:
            del self.robot_connections[robot_id]
            logger.info(f"로봇 {robot_id} 연결 해제됨")
        
        logger.info(f"연결 해제됨. 총 연결 수: {len(self.active_connections)}")
    
    async def handle_robot_connection(self, websocket: WebSocket):
        """로봇 연결을 처리합니다."""
        try:
            # 로봇 ID 받기
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "robot_register":
                robot_id = message.get("robot_id", "unknown")
                self.robot_connections[robot_id] = websocket
                logger.info(f"로봇 {robot_id} 등록됨")
                
                # 등록 확인 응답
                await websocket.send_text(json.dumps({
                    "type": "robot_registered",
                    "robot_id": robot_id,
                    "status": "success"
                }))
            
        except Exception as e:
            logger.error(f"로봇 연결 처리 중 오류: {e}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """특정 WebSocket에 메시지를 전송합니다."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"개인 메시지 전송 중 오류: {e}")
    
    async def broadcast(self, message: str):
        """모든 연결된 클라이언트에 메시지를 브로드캐스트합니다."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"브로드캐스트 중 오류: {e}")
                disconnected.append(connection)
        
        # 연결이 끊어진 것들 제거
        for connection in disconnected:
            await self.disconnect(connection)
    
    async def send_to_robot(self, robot_id: str, message: str):
        """특정 로봇에 메시지를 전송합니다."""
        if robot_id in self.robot_connections:
            try:
                await self.robot_connections[robot_id].send_text(message)
                return True
            except Exception as e:
                logger.error(f"로봇 {robot_id}에 메시지 전송 중 오류: {e}")
                del self.robot_connections[robot_id]
        return False


# 전역 연결 관리자
manager = ConnectionManager()


@router.websocket("/robot")
async def websocket_robot_endpoint(websocket: WebSocket):
    """로봇과의 WebSocket 연결 엔드포인트"""
    await manager.connect(websocket, "robot")
    
    try:
        while True:
            # 로봇에서 메시지 수신
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"로봇 메시지 수신: {message}")
            
            # 메시지 타입에 따른 처리
            message_type = message.get("type")
            
            if message_type == "sensor_data":
                # 센서 데이터를 모든 클라이언트에 브로드캐스트
                await manager.broadcast(json.dumps({
                    "type": "sensor_stream",
                    "data": message.get("data", {}),
                    "timestamp": message.get("timestamp")
                }))
            
            elif message_type == "robot_status":
                # 로봇 상태를 모든 클라이언트에 브로드캐스트
                await manager.broadcast(json.dumps({
                    "type": "robot_status_update",
                    "data": message.get("data", {}),
                    "timestamp": message.get("timestamp")
                }))
            
            elif message_type == "command_result":
                # 명령 실행 결과를 모든 클라이언트에 브로드캐스트
                await manager.broadcast(json.dumps({
                    "type": "command_result",
                    "data": message.get("data", {}),
                    "timestamp": message.get("timestamp")
                }))
            
            elif message_type == "safety_warning":
                # 안전 경고를 모든 클라이언트에 브로드캐스트
                await manager.broadcast(json.dumps({
                    "type": "safety_warning",
                    "data": message.get("data", {}),
                    "timestamp": message.get("timestamp")
                }))
            
            elif message_type == "ping":
                # 핑 응답
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": message.get("timestamp")
                }))
    
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"로봇 WebSocket 처리 중 오류: {e}")
        await manager.disconnect(websocket)


@router.websocket("/client")
async def websocket_client_endpoint(websocket: WebSocket):
    """클라이언트와의 WebSocket 연결 엔드포인트"""
    await manager.connect(websocket, "client")
    
    try:
        while True:
            # 클라이언트에서 메시지 수신 (주로 명령 전송)
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"클라이언트 메시지 수신: {message}")
            
            # 클라이언트 메시지 처리 (향후 구현)
            # 예: 자연어 명령, 수동 제어 등
            
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"클라이언트 WebSocket 처리 중 오류: {e}")
        await manager.disconnect(websocket)


@router.get("/connections")
async def get_connections_status():
    """현재 WebSocket 연결 상태를 조회합니다."""
    try:
        return {
            "success": True,
            "connections": {
                "total_clients": len(manager.active_connections),
                "connected_robots": list(manager.robot_connections.keys()),
                "robot_count": len(manager.robot_connections)
            },
            "timestamp": "2024-01-01T12:00:00Z"
        }
    except Exception as e:
        logger.error(f"연결 상태 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"연결 상태 조회 실패: {str(e)}")


@router.get("/health")
async def websocket_health_check():
    """WebSocket 모듈 헬스 체크"""
    return {
        "status": "healthy",
        "module": "websocket",
        "active_connections": len(manager.active_connections),
        "robot_connections": len(manager.robot_connections)
    }
