"""
연결 상태 관리 모듈
ESP32 클라이언트들의 연결 상태를 추적하고 관리
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from loguru import logger


class ConnectionManager:
    """ESP32 클라이언트 연결 상태 관리자"""
    
    def __init__(self):
        """연결 관리자 초기화"""
        self.clients: Dict[str, Dict[str, Any]] = {}
        self.client_writers: Dict[str, asyncio.StreamWriter] = {}
        self.last_pong_times: Dict[str, datetime] = {}
        self.connection_timeout = 60  # 60초 연결 타임아웃
        
        logger.info("연결 관리자 초기화됨")
    
    async def initialize(self):
        """연결 관리자 초기화 (비동기)"""
        logger.info("연결 관리자 초기화 완료")
    
    async def cleanup(self):
        """연결 관리자 정리"""
        # 모든 연결 정리
        for client_id in list(self.clients.keys()):
            await self.unregister_client(client_id)
        
        logger.info("연결 관리자 정리 완료")
    
    async def register_client(self, client_id: str, writer: asyncio.StreamWriter):
        """새로운 클라이언트 등록"""
        try:
            client_info = {
                "client_id": client_id,
                "connected_at": datetime.now(),
                "last_activity": datetime.now(),
                "status": "connected",
                "message_count": 0,
                "error_count": 0
            }
            
            self.clients[client_id] = client_info
            self.client_writers[client_id] = writer
            self.last_pong_times[client_id] = datetime.now()
            
            logger.info(f"클라이언트 등록됨 - {client_id}")
            
        except Exception as e:
            logger.error(f"클라이언트 등록 실패 - {client_id}: {e}")
            raise
    
    async def unregister_client(self, client_id: str):
        """클라이언트 등록 해제"""
        try:
            # 클라이언트 정보 제거
            if client_id in self.clients:
                del self.clients[client_id]
            
            # Writer 제거
            if client_id in self.client_writers:
                writer = self.client_writers[client_id]
                if not writer.is_closing():
                    writer.close()
                    await writer.wait_closed()
                del self.client_writers[client_id]
            
            # Pong 시간 제거
            if client_id in self.last_pong_times:
                del self.last_pong_times[client_id]
            
            logger.info(f"클라이언트 등록 해제됨 - {client_id}")
            
        except Exception as e:
            logger.error(f"클라이언트 등록 해제 실패 - {client_id}: {e}")
    
    async def update_client_info(self, client_id: str, info: Dict[str, Any]):
        """클라이언트 정보 업데이트"""
        try:
            if client_id in self.clients:
                self.clients[client_id].update(info)
                self.clients[client_id]["last_activity"] = datetime.now()
                logger.debug(f"클라이언트 정보 업데이트됨 - {client_id}")
            else:
                logger.warning(f"존재하지 않는 클라이언트 정보 업데이트 시도 - {client_id}")
                
        except Exception as e:
            logger.error(f"클라이언트 정보 업데이트 실패 - {client_id}: {e}")
    
    async def update_last_pong(self, client_id: str):
        """마지막 Pong 시간 업데이트"""
        try:
            self.last_pong_times[client_id] = datetime.now()
            
            if client_id in self.clients:
                self.clients[client_id]["last_activity"] = datetime.now()
                
        except Exception as e:
            logger.error(f"Pong 시간 업데이트 실패 - {client_id}: {e}")
    
    async def is_client_alive(self, client_id: str) -> bool:
        """클라이언트가 살아있는지 확인"""
        try:
            if client_id not in self.last_pong_times:
                return False
            
            last_pong = self.last_pong_times[client_id]
            time_since_pong = datetime.now() - last_pong
            
            # 연결 타임아웃 체크
            if time_since_pong > timedelta(seconds=self.connection_timeout):
                logger.warning(f"클라이언트 연결 타임아웃 - {client_id}")
                await self.unregister_client(client_id)
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"클라이언트 생존 확인 실패 - {client_id}: {e}")
            return False
    
    async def get_client_writer(self, client_id: str) -> Optional[asyncio.StreamWriter]:
        """클라이언트 Writer 반환"""
        try:
            return self.client_writers.get(client_id)
        except Exception as e:
            logger.error(f"클라이언트 Writer 조회 실패 - {client_id}: {e}")
            return None
    
    async def get_first_client(self) -> Optional[str]:
        """첫 번째 연결된 클라이언트 ID 반환"""
        try:
            alive_clients = []
            for client_id in list(self.clients.keys()):
                if await self.is_client_alive(client_id):
                    alive_clients.append(client_id)
            
            return alive_clients[0] if alive_clients else None
            
        except Exception as e:
            logger.error(f"첫 번째 클라이언트 조회 실패: {e}")
            return None
    
    async def get_connected_clients(self) -> List[Dict[str, Any]]:
        """연결된 모든 클라이언트 정보 반환"""
        try:
            connected_clients = []
            current_time = datetime.now()
            
            for client_id, client_info in self.clients.items():
                if await self.is_client_alive(client_id):
                    # 연결 시간 계산
                    connected_duration = current_time - client_info["connected_at"]
                    
                    client_summary = {
                        "client_id": client_id,
                        "connected_at": client_info["connected_at"].isoformat(),
                        "connected_duration": str(connected_duration),
                        "last_activity": client_info["last_activity"].isoformat(),
                        "status": client_info["status"],
                        "message_count": client_info["message_count"],
                        "error_count": client_info["error_count"]
                    }
                    
                    connected_clients.append(client_summary)
            
            return connected_clients
            
        except Exception as e:
            logger.error(f"연결된 클라이언트 목록 조회 실패: {e}")
            return []
    
    async def increment_message_count(self, client_id: str):
        """클라이언트 메시지 카운트 증가"""
        try:
            if client_id in self.clients:
                self.clients[client_id]["message_count"] += 1
                self.clients[client_id]["last_activity"] = datetime.now()
                
        except Exception as e:
            logger.error(f"메시지 카운트 증가 실패 - {client_id}: {e}")
    
    async def increment_error_count(self, client_id: str):
        """클라이언트 에러 카운트 증가"""
        try:
            if client_id in self.clients:
                self.clients[client_id]["error_count"] += 1
                
        except Exception as e:
            logger.error(f"에러 카운트 증가 실패 - {client_id}: {e}")
    
    async def get_connection_statistics(self) -> Dict[str, Any]:
        """연결 통계 정보 반환"""
        try:
            total_clients = len(self.clients)
            alive_clients = len([c for c in self.clients.keys() if await self.is_client_alive(c)])
            
            total_messages = sum(client["message_count"] for client in self.clients.values())
            total_errors = sum(client["error_count"] for client in self.clients.values())
            
            return {
                "total_clients": total_clients,
                "alive_clients": alive_clients,
                "total_messages": total_messages,
                "total_errors": total_errors,
                "connection_timeout": self.connection_timeout,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"연결 통계 조회 실패: {e}")
            return {}
    
    async def broadcast_to_all(self, message: Dict[str, Any]) -> int:
        """모든 연결된 클라이언트에게 메시지 브로드캐스트"""
        try:
            sent_count = 0
            
            for client_id, writer in list(self.client_writers.items()):
                if await self.is_client_alive(client_id):
                    try:
                        message_json = f"{json.dumps(message, ensure_ascii=False)}\n"
                        writer.write(message_json.encode())
                        await writer.drain()
                        sent_count += 1
                        
                    except Exception as e:
                        logger.error(f"브로드캐스트 전송 실패 - {client_id}: {e}")
                        await self.unregister_client(client_id)
            
            logger.debug(f"브로드캐스트 완료 - {sent_count}개 클라이언트에게 전송")
            return sent_count
            
        except Exception as e:
            logger.error(f"브로드캐스트 실패: {e}")
            return 0
    
    async def health_check(self) -> Dict[str, Any]:
        """연결 관리자 헬스 체크"""
        try:
            alive_clients = len([c for c in self.clients.keys() if await self.is_client_alive(c)])
            
            return {
                "status": "healthy",
                "module": "connection_manager",
                "total_clients": len(self.clients),
                "alive_clients": alive_clients,
                "connection_timeout": self.connection_timeout
            }
            
        except Exception as e:
            logger.error(f"연결 관리자 헬스 체크 실패: {e}")
            return {
                "status": "error",
                "module": "connection_manager",
                "error": str(e)
            }
