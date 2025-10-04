"""
Deks 백엔드 설정 관리 모듈
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 서버 설정
    host: str = Field(default="0.0.0.0", description="서버 호스트")
    port: int = Field(default=8000, description="서버 포트")
    debug: bool = Field(default=True, description="디버그 모드")
    
    # 데이터베이스 설정
    database_url: str = Field(default="sqlite:///./deks.db", description="데이터베이스 URL")
    
    # 로봇 통신 설정
    robot_tcp_port: int = Field(default=8888, description="로봇 TCP 포트")
    robot_connection_timeout: int = Field(default=30, description="로봇 연결 타임아웃 (초)")
    robot_command_timeout: int = Field(default=10, description="로봇 명령 타임아웃 (초)")
    
    # 보안 설정
    secret_key: str = Field(default="deks-secret-key-change-in-production", description="시크릿 키")
    access_token_expire_minutes: int = Field(default=30, description="토큰 만료 시간 (분)")
    
    # 로깅 설정
    log_level: str = Field(default="INFO", description="로그 레벨")
    log_file: str = Field(default="logs/deks.log", description="로그 파일 경로")
    
    # WebSocket 설정
    websocket_ping_interval: int = Field(default=30, description="WebSocket 핑 간격 (초)")
    websocket_ping_timeout: int = Field(default=10, description="WebSocket 핑 타임아웃 (초)")
    
    # 자연어 처리 설정
    nlp_confidence_threshold: float = Field(default=0.7, description="NLP 신뢰도 임계값")
    nlp_max_suggestions: int = Field(default=3, description="최대 제안 개수")
    
    # 사용자 분석 설정
    analytics_enabled: bool = Field(default=True, description="분석 기능 활성화")
    user_pattern_learning: bool = Field(default=True, description="사용자 패턴 학습 활성화")
    
    # API 설정
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 프리픽스")
    project_name: str = Field(default="Deks 1.0 Backend", description="프로젝트 이름")
    project_version: str = Field(default="1.0.0", description="프로젝트 버전")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 전역 설정 인스턴스
settings = Settings()


def get_settings() -> Settings:
    """설정 인스턴스를 반환합니다."""
    return settings
