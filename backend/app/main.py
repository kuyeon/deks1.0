"""
Deks 1.0 백엔드 메인 애플리케이션
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys
from datetime import datetime

from app.core.config import get_settings
from app.api.v1 import api_router
from app.database.init_db import init_database
from app.core.error_handlers import register_error_handlers, get_error_statistics
from fastapi import WebSocket, WebSocketDisconnect
from app.services.socket_bridge import start_socket_bridge, stop_socket_bridge, get_socket_bridge
import json


# 설정 가져오기
settings = get_settings()

# 로깅 설정
logger.remove()  # 기본 핸들러 제거
logger.add(
    sys.stdout,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add(
    settings.log_file,
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="1 day",
    retention="30 days"
)

# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
    description="Deks 1.0 로봇을 위한 백엔드 API 서버",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 오리진 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 에러 핸들러 등록
register_error_handlers(app)

@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


# WebSocket 연결 관리
active_connections = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """간단한 WebSocket 엔드포인트"""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"WebSocket 연결됨. 총 연결 수: {len(active_connections)}")
    
    try:
        while True:
            # 클라이언트에서 메시지 수신
            data = await websocket.receive_text()
            message = json.loads(data)
            logger.info(f"WebSocket 메시지 수신: {message}")
            
            # 에코 응답
            await websocket.send_text(json.dumps({
                "type": "echo",
                "message": "메시지를 받았습니다",
                "original": message
            }))
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"WebSocket 연결 해제됨. 총 연결 수: {len(active_connections)}")
    except Exception as e:
        logger.error(f"WebSocket 오류: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행되는 이벤트"""
    logger.info("Deks 백엔드 서버 시작 중...")
    
    # 데이터베이스 초기화
    await init_database()
    logger.info("데이터베이스 초기화 완료")
    
    # Socket Bridge 초기화
    try:
        await start_socket_bridge()
        logger.info("Socket Bridge 초기화 완료")
    except Exception as e:
        logger.error(f"Socket Bridge 초기화 실패: {e}")
    
    logger.info("Deks 백엔드 서버 시작 완료")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행되는 이벤트"""
    logger.info("Deks 백엔드 서버 종료 중...")
    
    # Socket Bridge 정리
    try:
        await stop_socket_bridge()
        logger.info("Socket Bridge 정리 완료")
    except Exception as e:
        logger.error(f"Socket Bridge 정리 실패: {e}")
    
    logger.info("Deks 백엔드 서버 종료 완료")


# API 라우터 등록
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Deks 1.0 백엔드 서버에 오신 것을 환영합니다!",
        "version": settings.project_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    try:
        return {
            "status": "healthy",
            "service": "deks-backend",
            "version": settings.project_version,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"헬스 체크 실패: {e}")
        return {
            "status": "error",
            "service": "deks-backend",
            "version": settings.project_version,
            "error": str(e)
        }


@app.get("/socket-bridge/status")
async def socket_bridge_status():
    """Socket Bridge 상태 조회"""
    try:
        socket_bridge = await get_socket_bridge()
        status = await socket_bridge.get_connection_status()
        return status
    except Exception as e:
        logger.error(f"Socket Bridge 상태 조회 실패: {e}")
        return {"error": str(e)}


@app.get("/errors/statistics")
async def get_error_stats():
    """에러 통계 조회"""
    try:
        stats = get_error_statistics()
        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"에러 통계 조회 실패: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
