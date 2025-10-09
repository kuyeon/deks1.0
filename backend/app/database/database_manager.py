"""
데이터베이스 매니저 클래스
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from contextlib import contextmanager
from loguru import logger

from app.core.config import get_settings


class DatabaseManager:
    """SQLite 데이터베이스 매니저"""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_path = self._get_database_path()
    
    def _get_database_path(self) -> str:
        """데이터베이스 파일 경로를 반환합니다."""
        db_url = self.settings.database_url
        
        if db_url.startswith("sqlite:///"):
            db_path = db_url.replace("sqlite:///", "")
            return db_path
        else:
            return "deks.db"
    
    @contextmanager
    def get_connection(self):
        """데이터베이스 연결 컨텍스트 매니저"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 결과 반환
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"데이터베이스 연결 오류: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def save_user_interaction(self, interaction_data: Dict[str, Any]) -> bool:
        """사용자 상호작용을 저장합니다."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO user_interactions 
                    (command, response, success, user_id, session_id, command_id, confidence, execution_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    interaction_data.get('command', ''),
                    interaction_data.get('response', ''),
                    interaction_data.get('success', False),
                    interaction_data.get('user_id', 'default_user'),
                    interaction_data.get('session_id'),
                    interaction_data.get('command_id'),
                    interaction_data.get('confidence', 0.0),
                    interaction_data.get('execution_time', 0.0)
                ))
                
                conn.commit()
                logger.info(f"사용자 상호작용 저장 완료: {interaction_data.get('command_id')}")
                return True
                
        except Exception as e:
            logger.error(f"사용자 상호작용 저장 실패: {e}")
            return False
    
    def update_command_frequency(self, command: str, success: bool = True) -> bool:
        """명령어 사용 빈도를 업데이트합니다."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 기존 데이터 조회
                cursor.execute("SELECT count, success_count FROM command_frequency WHERE command = ?", (command,))
                result = cursor.fetchone()
                
                if result:
                    # 기존 데이터 업데이트
                    count = result['count'] + 1
                    success_count = result['success_count'] + (1 if success else 0)
                    
                    cursor.execute("""
                        UPDATE command_frequency 
                        SET count = ?, success_count = ?, last_used = CURRENT_TIMESTAMP
                        WHERE command = ?
                    """, (count, success_count, command))
                else:
                    # 새 데이터 삽입
                    cursor.execute("""
                        INSERT INTO command_frequency (command, count, success_count, last_used)
                        VALUES (?, 1, ?, CURRENT_TIMESTAMP)
                    """, (command, 1 if success else 0))
                
                conn.commit()
                logger.debug(f"명령어 빈도 업데이트: {command}")
                return True
                
        except Exception as e:
            logger.error(f"명령어 빈도 업데이트 실패: {e}")
            return False
    
    def save_error_pattern(self, error_data: Dict[str, Any]) -> bool:
        """에러 패턴을 저장합니다."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO error_patterns 
                    (failed_command, error_type, user_id, error_message, context)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    error_data.get('failed_command', ''),
                    error_data.get('error_type', ''),
                    error_data.get('user_id', 'default_user'),
                    error_data.get('error_message', ''),
                    json.dumps(error_data.get('context', {}))
                ))
                
                conn.commit()
                logger.info(f"에러 패턴 저장 완료: {error_data.get('error_type')}")
                return True
                
        except Exception as e:
            logger.error(f"에러 패턴 저장 실패: {e}")
            return False
    
    def save_robot_state(self, state_data: Dict[str, Any]) -> bool:
        """로봇 상태를 저장합니다."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO robot_states 
                    (robot_id, position_x, position_y, orientation, battery_level, 
                     is_moving, safety_mode, sensor_data, connection_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    state_data.get('robot_id', 'deks_001'),
                    state_data.get('position', {}).get('x'),
                    state_data.get('position', {}).get('y'),
                    state_data.get('orientation'),
                    state_data.get('battery'),
                    state_data.get('is_moving', False),
                    state_data.get('safety_mode', 'normal'),
                    json.dumps(state_data.get('sensors', {})),
                    state_data.get('connection_status', 'connected')
                ))
                
                conn.commit()
                logger.debug(f"로봇 상태 저장 완료: {state_data.get('robot_id')}")
                return True
                
        except Exception as e:
            logger.error(f"로봇 상태 저장 실패: {e}")
            return False
    
    def save_sensor_data(self, sensor_data: Dict[str, Any]) -> bool:
        """센서 데이터를 저장합니다."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO sensor_data 
                    (robot_id, front_distance, left_distance, right_distance, 
                     drop_detected, battery_voltage, temperature)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    sensor_data.get('robot_id', 'deks_001'),
                    sensor_data.get('front_distance'),
                    sensor_data.get('left_distance'),
                    sensor_data.get('right_distance'),
                    sensor_data.get('drop_detected', False),
                    sensor_data.get('battery_voltage'),
                    sensor_data.get('temperature')
                ))
                
                conn.commit()
                logger.debug(f"센서 데이터 저장 완료")
                return True
                
        except Exception as e:
            logger.error(f"센서 데이터 저장 실패: {e}")
            return False
    
    def save_command_execution_log(self, log_data: Dict[str, Any]) -> bool:
        """명령 실행 로그를 저장합니다."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO command_execution_logs 
                    (command_id, command_type, parameters, user_id, robot_id, 
                     success, execution_time, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    log_data.get('command_id'),
                    log_data.get('command_type'),
                    json.dumps(log_data.get('parameters', {})),
                    log_data.get('user_id', 'default_user'),
                    log_data.get('robot_id', 'deks_001'),
                    log_data.get('success', False),
                    log_data.get('execution_time', 0.0),
                    log_data.get('error_message')
                ))
                
                conn.commit()
                logger.debug(f"명령 실행 로그 저장 완료: {log_data.get('command_id')}")
                return True
                
        except Exception as e:
            logger.error(f"명령 실행 로그 저장 실패: {e}")
            return False
    
    def get_user_patterns(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """사용자 패턴을 분석합니다."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 자주 사용하는 명령어 조회
                cursor.execute("""
                    SELECT command, COUNT(*) as frequency, 
                           AVG(CASE WHEN success = 1 THEN 1.0 ELSE 0.0 END) as success_rate
                    FROM user_interactions 
                    WHERE user_id = ? AND timestamp >= datetime('now', '-{} days')
                    GROUP BY command 
                    ORDER BY frequency DESC 
                    LIMIT 10
                """.format(days), (user_id,))
                
                frequent_commands = []
                for row in cursor.fetchall():
                    frequent_commands.append({
                        'command': row['command'],
                        'frequency': row['frequency'],
                        'success_rate': round(row['success_rate'], 2)
                    })
                
                # 에러 패턴 조회
                cursor.execute("""
                    SELECT error_type, COUNT(*) as frequency
                    FROM error_patterns 
                    WHERE user_id = ? AND timestamp >= datetime('now', '-{} days')
                    GROUP BY error_type 
                    ORDER BY frequency DESC
                """.format(days), (user_id,))
                
                error_patterns = []
                for row in cursor.fetchall():
                    error_patterns.append({
                        'error_type': row['error_type'],
                        'frequency': row['frequency']
                    })
                
                return {
                    'frequent_commands': frequent_commands,
                    'error_patterns': error_patterns,
                    'analysis_period': f"{days}_days"
                }
                
        except Exception as e:
            logger.error(f"사용자 패턴 분석 실패: {e}")
            return {'frequent_commands': [], 'error_patterns': []}
    
    def get_command_frequency_stats(self) -> Dict[str, Any]:
        """명령어 빈도 통계를 조회합니다."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT command, count, success_count, 
                           (success_count * 1.0 / count) as success_rate,
                           last_used
                    FROM command_frequency 
                    ORDER BY count DESC
                """)
                
                commands = []
                for row in cursor.fetchall():
                    commands.append({
                        'command': row['command'],
                        'count': row['count'],
                        'success_count': row['success_count'],
                        'success_rate': round(row['success_rate'], 2),
                        'last_used': row['last_used']
                    })
                
                return {
                    'commands': commands,
                    'total_commands': len(commands)
                }
                
        except Exception as e:
            logger.error(f"명령어 빈도 통계 조회 실패: {e}")
            return {'commands': [], 'total_commands': 0}
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """SQL 쿼리를 실행하고 결과를 반환합니다."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                # SELECT 쿼리인 경우 결과 반환
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    # INSERT, UPDATE, DELETE 등의 경우 커밋
                    conn.commit()
                    return []
                    
        except Exception as e:
            logger.error(f"쿼리 실행 실패: {e}")
            raise


# 전역 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager()
