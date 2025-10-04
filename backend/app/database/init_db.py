"""
데이터베이스 초기화 모듈
"""

import sqlite3
import os
from pathlib import Path
from loguru import logger

from app.core.config import get_settings


def get_database_path() -> str:
    """데이터베이스 파일 경로를 반환합니다."""
    settings = get_settings()
    db_url = settings.database_url
    
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
        return db_path
    else:
        return "deks.db"


def create_tables():
    """데이터베이스 테이블을 생성합니다."""
    db_path = get_database_path()
    
    # 데이터베이스 디렉토리 생성
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 사용자 상호작용 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                command TEXT NOT NULL,
                response TEXT,
                success BOOLEAN,
                user_id TEXT DEFAULT 'default_user',
                session_id TEXT,
                command_id TEXT,
                confidence REAL,
                execution_time REAL
            )
        """)
        
        # 명령어 빈도 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_frequency (
                command TEXT PRIMARY KEY,
                count INTEGER DEFAULT 1,
                success_count INTEGER DEFAULT 0,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                avg_confidence REAL DEFAULT 0.0
            )
        """)
        
        # 에러 패턴 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                failed_command TEXT,
                error_type TEXT,
                user_id TEXT,
                error_message TEXT,
                context TEXT
            )
        """)
        
        # 감정 반응 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emotion_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                emotion TEXT,
                trigger_command TEXT,
                user_satisfaction INTEGER CHECK(user_satisfaction >= 1 AND user_satisfaction <= 5),
                user_id TEXT,
                session_id TEXT
            )
        """)
        
        # 로봇 상태 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS robot_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                robot_id TEXT DEFAULT 'deks_001',
                position_x REAL,
                position_y REAL,
                orientation REAL,
                battery_level INTEGER,
                is_moving BOOLEAN,
                safety_mode TEXT,
                sensor_data TEXT,  -- JSON 형태로 저장
                connection_status TEXT
            )
        """)
        
        # 센서 데이터 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                robot_id TEXT DEFAULT 'deks_001',
                front_distance REAL,
                left_distance REAL,
                right_distance REAL,
                drop_detected BOOLEAN,
                battery_voltage REAL,
                temperature REAL
            )
        """)
        
        # 명령 실행 로그 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                command_id TEXT,
                command_type TEXT,
                parameters TEXT,  -- JSON 형태로 저장
                user_id TEXT,
                robot_id TEXT DEFAULT 'deks_001',
                success BOOLEAN,
                execution_time REAL,
                error_message TEXT
            )
        """)
        
        # 인덱스 생성
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_interactions_timestamp ON user_interactions(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_interactions_user_id ON user_interactions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_robot_states_timestamp ON robot_states(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp ON sensor_data(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_command_execution_logs_timestamp ON command_execution_logs(timestamp)")
        
        conn.commit()
        logger.info("데이터베이스 테이블 생성 완료")
        
    except Exception as e:
        logger.error(f"데이터베이스 테이블 생성 중 오류 발생: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


async def init_database():
    """데이터베이스 초기화를 수행합니다."""
    try:
        create_tables()
        logger.info("데이터베이스 초기화 완료")
    except Exception as e:
        logger.error(f"데이터베이스 초기화 실패: {e}")
        raise


def get_connection():
    """데이터베이스 연결을 반환합니다."""
    db_path = get_database_path()
    return sqlite3.connect(db_path)


def get_cursor():
    """데이터베이스 커서를 반환합니다."""
    conn = get_connection()
    return conn.cursor()
