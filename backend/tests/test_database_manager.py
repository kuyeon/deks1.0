"""
데이터베이스 매니저 모듈 단위 테스트
"""

import pytest
import sqlite3
import json
import os
import tempfile
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime

from app.database.database_manager import DatabaseManager


class TestDatabaseManager:
    """데이터베이스 매니저 테스트 클래스"""
    
    @pytest.fixture
    def temp_db_manager(self):
        """임시 데이터베이스 매니저 생성"""
        # 임시 데이터베이스 파일 생성
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        # 임시 데이터베이스 매니저 생성
        manager = DatabaseManager()
        manager.db_path = temp_db.name
        
        # 테스트용 테이블 생성
        with manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # 사용자 상호작용 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT,
                    response TEXT,
                    success BOOLEAN,
                    user_id TEXT,
                    session_id TEXT,
                    command_id TEXT,
                    confidence REAL,
                    execution_time REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 명령어 빈도 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS command_frequency (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT UNIQUE,
                    count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 에러 패턴 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS error_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    failed_command TEXT,
                    error_type TEXT,
                    user_id TEXT,
                    error_message TEXT,
                    context TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 로봇 상태 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS robot_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    robot_id TEXT,
                    position_x REAL,
                    position_y REAL,
                    orientation REAL,
                    battery_level INTEGER,
                    is_moving BOOLEAN,
                    safety_mode TEXT,
                    sensor_data TEXT,
                    connection_status TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 센서 데이터 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    robot_id TEXT,
                    front_distance REAL,
                    left_distance REAL,
                    right_distance REAL,
                    drop_detected BOOLEAN,
                    battery_voltage REAL,
                    temperature REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 명령 실행 로그 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS command_execution_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_id TEXT,
                    command_type TEXT,
                    parameters TEXT,
                    user_id TEXT,
                    robot_id TEXT,
                    success BOOLEAN,
                    execution_time REAL,
                    error_message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
        
        yield manager
        
        # 정리
        os.unlink(temp_db.name)
    
    def test_database_manager_initialization(self):
        """데이터베이스 매니저 초기화 테스트"""
        manager = DatabaseManager()
        
        assert manager.settings is not None
        assert manager.db_path is not None
        assert manager.db_path.endswith('.db')
    
    def test_get_database_path_sqlite_url(self):
        """SQLite URL에서 데이터베이스 경로 추출 테스트"""
        manager = DatabaseManager()
        
        with patch.object(manager.settings, 'database_url', 'sqlite:///test.db'):
            path = manager._get_database_path()
            assert path == 'test.db'
    
    def test_get_database_path_default(self):
        """기본 데이터베이스 경로 테스트"""
        manager = DatabaseManager()
        
        with patch.object(manager.settings, 'database_url', 'invalid_url'):
            path = manager._get_database_path()
            assert path == 'deks.db'
    
    def test_get_connection_success(self, temp_db_manager):
        """데이터베이스 연결 성공 테스트"""
        with temp_db_manager.get_connection() as conn:
            assert conn is not None
            assert isinstance(conn, sqlite3.Connection)
    
    def test_get_connection_error(self):
        """데이터베이스 연결 에러 테스트"""
        manager = DatabaseManager()
        manager.db_path = "/invalid/path/database.db"
        
        with pytest.raises(Exception):
            with manager.get_connection() as conn:
                pass
    
    def test_save_user_interaction_success(self, temp_db_manager):
        """사용자 상호작용 저장 성공 테스트"""
        interaction_data = {
            'command': '안녕하세요',
            'response': '안녕하세요! 저는 덱스입니다.',
            'success': True,
            'user_id': 'test_user',
            'session_id': 'session_123',
            'command_id': 'cmd_123',
            'confidence': 0.95,
            'execution_time': 1.5
        }
        
        result = temp_db_manager.save_user_interaction(interaction_data)
        
        assert result is True
        
        # 데이터가 실제로 저장되었는지 확인
        with temp_db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_interactions WHERE command_id = ?", ('cmd_123',))
            row = cursor.fetchone()
            
            assert row is not None
            assert row['command'] == '안녕하세요'
            assert row['response'] == '안녕하세요! 저는 덱스입니다.'
            assert row['success'] == 1  # SQLite에서는 BOOLEAN이 INTEGER로 저장
            assert row['user_id'] == 'test_user'
    
    def test_save_user_interaction_minimal_data(self, temp_db_manager):
        """최소 데이터로 사용자 상호작용 저장 테스트"""
        interaction_data = {
            'command': '테스트'
        }
        
        result = temp_db_manager.save_user_interaction(interaction_data)
        
        assert result is True
    
    def test_save_user_interaction_error(self, temp_db_manager):
        """사용자 상호작용 저장 에러 테스트"""
        # 잘못된 데이터로 에러 발생
        interaction_data = None
        
        with patch('app.database.database_manager.logger') as mock_logger:
            result = temp_db_manager.save_user_interaction(interaction_data)
        
        assert result is False
        mock_logger.error.assert_called()
    
    def test_update_command_frequency_new_command(self, temp_db_manager):
        """새 명령어 빈도 업데이트 테스트"""
        result = temp_db_manager.update_command_frequency('move_forward', success=True)
        
        assert result is True
        
        # 데이터가 실제로 저장되었는지 확인
        with temp_db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM command_frequency WHERE command = ?", ('move_forward',))
            row = cursor.fetchone()
            
            assert row is not None
            assert row['command'] == 'move_forward'
            assert row['count'] == 1
            assert row['success_count'] == 1
    
    def test_update_command_frequency_existing_command(self, temp_db_manager):
        """기존 명령어 빈도 업데이트 테스트"""
        # 첫 번째 실행
        temp_db_manager.update_command_frequency('move_forward', success=True)
        
        # 두 번째 실행 (실패)
        result = temp_db_manager.update_command_frequency('move_forward', success=False)
        
        assert result is True
        
        # 데이터가 업데이트되었는지 확인
        with temp_db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM command_frequency WHERE command = ?", ('move_forward',))
            row = cursor.fetchone()
            
            assert row['count'] == 2
            assert row['success_count'] == 1
    
    def test_update_command_frequency_error(self, temp_db_manager):
        """명령어 빈도 업데이트 에러 테스트"""
        # 잘못된 데이터로 에러 발생
        with patch('app.database.database_manager.logger') as mock_logger:
            with patch.object(temp_db_manager, 'get_connection', side_effect=Exception("DB 오류")):
                result = temp_db_manager.update_command_frequency('test_command')
        
        assert result is False
        mock_logger.error.assert_called()
    
    def test_save_error_pattern_success(self, temp_db_manager):
        """에러 패턴 저장 성공 테스트"""
        error_data = {
            'failed_command': 'move_forward',
            'error_type': 'motor_error',
            'user_id': 'test_user',
            'error_message': '모터 연결 실패',
            'context': {'speed': 50, 'distance': 100}
        }
        
        result = temp_db_manager.save_error_pattern(error_data)
        
        assert result is True
        
        # 데이터가 실제로 저장되었는지 확인
        with temp_db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM error_patterns WHERE error_type = ?", ('motor_error',))
            row = cursor.fetchone()
            
            assert row is not None
            assert row['failed_command'] == 'move_forward'
            assert row['error_message'] == '모터 연결 실패'
            
            # JSON 컨텍스트 확인
            context = json.loads(row['context'])
            assert context['speed'] == 50
            assert context['distance'] == 100
    
    def test_save_error_pattern_minimal_data(self, temp_db_manager):
        """최소 데이터로 에러 패턴 저장 테스트"""
        error_data = {
            'error_type': 'general_error'
        }
        
        result = temp_db_manager.save_error_pattern(error_data)
        
        assert result is True
    
    def test_save_robot_state_success(self, temp_db_manager):
        """로봇 상태 저장 성공 테스트"""
        state_data = {
            'robot_id': 'deks_001',
            'position': {'x': 10.5, 'y': 20.3},
            'orientation': 45.0,
            'battery': 85,
            'is_moving': True,
            'safety_mode': 'normal',
            'sensors': {'front_distance': 25.0, 'drop_detection': False},
            'connection_status': 'connected'
        }
        
        result = temp_db_manager.save_robot_state(state_data)
        
        assert result is True
        
        # 데이터가 실제로 저장되었는지 확인
        with temp_db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM robot_states WHERE robot_id = ?", ('deks_001',))
            row = cursor.fetchone()
            
            assert row is not None
            assert row['position_x'] == 10.5
            assert row['position_y'] == 20.3
            assert row['orientation'] == 45.0
            assert row['battery_level'] == 85
            assert row['is_moving'] == 1
            assert row['safety_mode'] == 'normal'
            assert row['connection_status'] == 'connected'
    
    def test_save_sensor_data_success(self, temp_db_manager):
        """센서 데이터 저장 성공 테스트"""
        sensor_data = {
            'robot_id': 'deks_001',
            'front_distance': 25.5,
            'left_distance': 30.0,
            'right_distance': 28.0,
            'drop_detected': False,
            'battery_voltage': 7.8,
            'temperature': 23.5
        }
        
        result = temp_db_manager.save_sensor_data(sensor_data)
        
        assert result is True
        
        # 데이터가 실제로 저장되었는지 확인
        with temp_db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sensor_data WHERE robot_id = ?", ('deks_001',))
            row = cursor.fetchone()
            
            assert row is not None
            assert row['front_distance'] == 25.5
            assert row['left_distance'] == 30.0
            assert row['right_distance'] == 28.0
            assert row['drop_detected'] == 0
            assert row['battery_voltage'] == 7.8
            assert row['temperature'] == 23.5
    
    def test_save_command_execution_log_success(self, temp_db_manager):
        """명령 실행 로그 저장 성공 테스트"""
        log_data = {
            'command_id': 'cmd_123',
            'command_type': 'move_forward',
            'parameters': {'speed': 50, 'distance': 100},
            'user_id': 'test_user',
            'robot_id': 'deks_001',
            'success': True,
            'execution_time': 2.5,
            'error_message': None
        }
        
        result = temp_db_manager.save_command_execution_log(log_data)
        
        assert result is True
        
        # 데이터가 실제로 저장되었는지 확인
        with temp_db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM command_execution_logs WHERE command_id = ?", ('cmd_123',))
            row = cursor.fetchone()
            
            assert row is not None
            assert row['command_type'] == 'move_forward'
            assert row['user_id'] == 'test_user'
            assert row['robot_id'] == 'deks_001'
            assert row['success'] == 1
            assert row['execution_time'] == 2.5
            
            # JSON 파라미터 확인
            params = json.loads(row['parameters'])
            assert params['speed'] == 50
            assert params['distance'] == 100
    
    def test_get_user_patterns_success(self, temp_db_manager):
        """사용자 패턴 조회 성공 테스트"""
        # 테스트 데이터 추가
        interaction_data = {
            'command': 'move_forward',
            'response': 'OK',
            'success': True,
            'user_id': 'test_user',
            'session_id': 'session_123',
            'command_id': 'cmd_1'
        }
        temp_db_manager.save_user_interaction(interaction_data)
        
        error_data = {
            'failed_command': 'move_backward',
            'error_type': 'motor_error',
            'user_id': 'test_user',
            'error_message': '모터 오류'
        }
        temp_db_manager.save_error_pattern(error_data)
        
        # 사용자 패턴 조회
        patterns = temp_db_manager.get_user_patterns('test_user', days=7)
        
        assert 'frequent_commands' in patterns
        assert 'error_patterns' in patterns
        assert 'analysis_period' in patterns
        assert patterns['analysis_period'] == '7_days'
        assert len(patterns['frequent_commands']) > 0
        assert len(patterns['error_patterns']) > 0
    
    def test_get_user_patterns_no_data(self, temp_db_manager):
        """사용자 패턴 조회 - 데이터 없음 테스트"""
        patterns = temp_db_manager.get_user_patterns('nonexistent_user', days=7)
        
        assert patterns['frequent_commands'] == []
        assert patterns['error_patterns'] == []
    
    def test_get_user_patterns_error(self, temp_db_manager):
        """사용자 패턴 조회 에러 테스트"""
        with patch('app.database.database_manager.logger') as mock_logger:
            with patch.object(temp_db_manager, 'get_connection', side_effect=Exception("DB 오류")):
                patterns = temp_db_manager.get_user_patterns('test_user')
        
        assert patterns == {'frequent_commands': [], 'error_patterns': []}
        mock_logger.error.assert_called()
    
    def test_get_command_frequency_stats_success(self, temp_db_manager):
        """명령어 빈도 통계 조회 성공 테스트"""
        # 테스트 데이터 추가
        temp_db_manager.update_command_frequency('move_forward', success=True)
        temp_db_manager.update_command_frequency('move_forward', success=True)
        temp_db_manager.update_command_frequency('turn_left', success=False)
        
        stats = temp_db_manager.get_command_frequency_stats()
        
        assert 'commands' in stats
        assert 'total_commands' in stats
        assert stats['total_commands'] >= 2
        
        # move_forward가 가장 빈도가 높아야 함
        move_forward_cmd = next((cmd for cmd in stats['commands'] if cmd['command'] == 'move_forward'), None)
        assert move_forward_cmd is not None
        assert move_forward_cmd['count'] == 2
        assert move_forward_cmd['success_count'] == 2
        assert move_forward_cmd['success_rate'] == 1.0
    
    def test_get_command_frequency_stats_no_data(self, temp_db_manager):
        """명령어 빈도 통계 조회 - 데이터 없음 테스트"""
        stats = temp_db_manager.get_command_frequency_stats()
        
        assert stats['commands'] == []
        assert stats['total_commands'] == 0
    
    def test_execute_query_select(self, temp_db_manager):
        """SELECT 쿼리 실행 테스트"""
        # 테스트 데이터 추가
        temp_db_manager.update_command_frequency('test_command', success=True)
        
        # SELECT 쿼리 실행
        results = temp_db_manager.execute_query(
            "SELECT * FROM command_frequency WHERE command = ?",
            ('test_command',)
        )
        
        assert len(results) == 1
        assert results[0]['command'] == 'test_command'
        assert results[0]['count'] == 1
    
    def test_execute_query_insert(self, temp_db_manager):
        """INSERT 쿼리 실행 테스트"""
        # INSERT 쿼리 실행
        results = temp_db_manager.execute_query(
            "INSERT INTO command_frequency (command, count, success_count) VALUES (?, ?, ?)",
            ('manual_command', 1, 1)
        )
        
        assert results == []
        
        # 데이터가 삽입되었는지 확인
        select_results = temp_db_manager.execute_query(
            "SELECT * FROM command_frequency WHERE command = ?",
            ('manual_command',)
        )
        
        assert len(select_results) == 1
        assert select_results[0]['command'] == 'manual_command'
    
    def test_execute_query_error(self, temp_db_manager):
        """쿼리 실행 에러 테스트"""
        with pytest.raises(Exception):
            temp_db_manager.execute_query("INVALID SQL QUERY")
    
    def test_connection_context_manager_rollback(self, temp_db_manager):
        """연결 컨텍스트 매니저 롤백 테스트"""
        try:
            with temp_db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO command_frequency (command, count) VALUES (?, ?)", ('test_rollback', 1))
                # 의도적으로 에러 발생
                raise Exception("테스트 에러")
        except Exception:
            pass
        
        # 롤백되었는지 확인 (데이터가 없어야 함)
        with temp_db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM command_frequency WHERE command = ?", ('test_rollback',))
            result = cursor.fetchone()
            assert result is None
    
    def test_connection_context_manager_close(self, temp_db_manager):
        """연결 컨텍스트 매니저 자동 종료 테스트"""
        conn = None
        try:
            with temp_db_manager.get_connection() as connection:
                conn = connection
                assert conn is not None
                # SQLite 연결에서 간단한 쿼리 실행으로 연결 상태 확인
                cursor = conn.execute("SELECT 1")
                result = cursor.fetchone()
                assert result[0] == 1
        except Exception:
            pass
        
        # 연결이 자동으로 종료되었는지 확인 (SQLite는 연결이 종료되면 쿼리 실행 불가)
        if conn:
            try:
                conn.execute("SELECT 1")
                # 연결이 여전히 열려있으면 테스트 실패
                assert False, "Connection should be closed"
            except sqlite3.ProgrammingError:
                # 연결이 닫혔으면 정상
                pass
    
    def test_database_file_creation(self):
        """데이터베이스 파일 생성 테스트"""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            manager = DatabaseManager()
            manager.db_path = temp_db.name
            
            # 연결을 통해 데이터베이스 파일이 생성되는지 확인
            with manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE test_table (id INTEGER)")
                conn.commit()
            
            # 파일이 실제로 생성되었는지 확인
            assert os.path.exists(temp_db.name)
            
            # 데이터베이스 파일이 유효한지 확인
            conn = sqlite3.connect(temp_db.name)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'")
            result = cursor.fetchone()
            conn.close()
            
            assert result is not None
            assert result[0] == 'test_table'
            
        finally:
            if os.path.exists(temp_db.name):
                os.unlink(temp_db.name)
