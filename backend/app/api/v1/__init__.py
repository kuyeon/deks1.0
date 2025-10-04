"""
API v1 라우터 초기화
"""

from fastapi import APIRouter

from app.api.v1.endpoints import robot, nlp, sensors, analytics, expression, websocket

api_router = APIRouter()

# 각 엔드포인트 라우터 등록
api_router.include_router(robot.router, prefix="/robot", tags=["robot"])
api_router.include_router(nlp.router, prefix="/nlp", tags=["nlp"])
api_router.include_router(sensors.router, prefix="/sensors", tags=["sensors"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(expression.router, prefix="/expression", tags=["expression"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
