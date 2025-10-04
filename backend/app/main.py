"""
Deks 1.0 백엔드 메인 애플리케이션
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from app.core.config import get_settings
from app.api.v1 import api_router
from app.database.init_db import init_database


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


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행되는 이벤트"""
    logger.info("Deks 백엔드 서버 시작 중...")
    
    # 데이터베이스 초기화
    await init_database()
    logger.info("데이터베이스 초기화 완료")
    
    # Socket Bridge 초기화 (향후 구현)
    # await init_socket_bridge()
    
    logger.info("Deks 백엔드 서버 시작 완료")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행되는 이벤트"""
    logger.info("Deks 백엔드 서버 종료 중...")
    
    # Socket Bridge 정리 (향후 구현)
    # await cleanup_socket_bridge()
    
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
    return {
        "status": "healthy",
        "service": "deks-backend",
        "version": settings.project_version
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
