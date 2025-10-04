"""
Deks 백엔드 서버 실행 스크립트
"""

import uvicorn
from app.main import app
from app.core.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    print(f"🚀 Deks 1.0 백엔드 서버 시작 중...")
    print(f"📍 서버 주소: http://{settings.host}:{settings.port}")
    print(f"📚 API 문서: http://{settings.host}:{settings.port}/docs")
    print(f"🔧 디버그 모드: {settings.debug}")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )
