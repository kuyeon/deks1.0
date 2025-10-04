"""
데이터베이스 기능 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database_manager import db_manager
from app.database.init_db import init_database
import asyncio


async def test_database():
    """데이터베이스 기능을 테스트합니다."""
    print("🗄️ 데이터베이스 테스트 시작...")
    
    try:
        # 1. 데이터베이스 초기화 테스트
        print("\n1. 데이터베이스 초기화 테스트...")
        await init_database()
        print("✅ 데이터베이스 초기화 성공")
        
        # 2. 사용자 상호작용 저장 테스트
        print("\n2. 사용자 상호작용 저장 테스트...")
        interaction_data = {
            'command': '앞으로 가줘',
            'response': '앞으로 이동합니다!',
            'success': True,
            'user_id': 'test_user_001',
            'session_id': 'session_123',
            'command_id': 'cmd_test_001',
            'confidence': 0.95,
            'execution_time': 0.1
        }
        
        result = db_manager.save_user_interaction(interaction_data)
        print(f"✅ 사용자 상호작용 저장: {'성공' if result else '실패'}")
        
        # 3. 명령어 빈도 업데이트 테스트
        print("\n3. 명령어 빈도 업데이트 테스트...")
        result = db_manager.update_command_frequency('앞으로 가줘', success=True)
        print(f"✅ 명령어 빈도 업데이트: {'성공' if result else '실패'}")
        
        # 4. 에러 패턴 저장 테스트
        print("\n4. 에러 패턴 저장 테스트...")
        error_data = {
            'failed_command': '알 수 없는 명령',
            'error_type': 'unknown_command',
            'user_id': 'test_user_001',
            'error_message': '명령을 이해할 수 없습니다',
            'context': {'session_id': 'session_123'}
        }
        
        result = db_manager.save_error_pattern(error_data)
        print(f"✅ 에러 패턴 저장: {'성공' if result else '실패'}")
        
        # 5. 로봇 상태 저장 테스트
        print("\n5. 로봇 상태 저장 테스트...")
        state_data = {
            'robot_id': 'deks_001',
            'position': {'x': 10.5, 'y': 15.2},
            'orientation': 45,
            'battery': 85,
            'is_moving': False,
            'safety_mode': 'normal',
            'sensors': {
                'front_distance': 25.5,
                'left_distance': 30.2,
                'right_distance': 28.8
            },
            'connection_status': 'connected'
        }
        
        result = db_manager.save_robot_state(state_data)
        print(f"✅ 로봇 상태 저장: {'성공' if result else '실패'}")
        
        # 6. 센서 데이터 저장 테스트
        print("\n6. 센서 데이터 저장 테스트...")
        sensor_data = {
            'robot_id': 'deks_001',
            'front_distance': 25.5,
            'left_distance': 30.2,
            'right_distance': 28.8,
            'drop_detected': False,
            'battery_voltage': 3.7,
            'temperature': 25.0
        }
        
        result = db_manager.save_sensor_data(sensor_data)
        print(f"✅ 센서 데이터 저장: {'성공' if result else '실패'}")
        
        # 7. 명령 실행 로그 저장 테스트
        print("\n7. 명령 실행 로그 저장 테스트...")
        log_data = {
            'command_id': 'cmd_test_002',
            'command_type': 'move_forward',
            'parameters': {'speed': 50, 'distance': 100},
            'user_id': 'test_user_001',
            'robot_id': 'deks_001',
            'success': True,
            'execution_time': 2.5,
            'error_message': None
        }
        
        result = db_manager.save_command_execution_log(log_data)
        print(f"✅ 명령 실행 로그 저장: {'성공' if result else '실패'}")
        
        # 8. 사용자 패턴 분석 테스트
        print("\n8. 사용자 패턴 분석 테스트...")
        patterns = db_manager.get_user_patterns('test_user_001', days=7)
        print(f"✅ 사용자 패턴 분석:")
        print(f"   - 자주 사용하는 명령: {len(patterns.get('frequent_commands', []))}개")
        print(f"   - 에러 패턴: {len(patterns.get('error_patterns', []))}개")
        
        # 9. 명령어 빈도 통계 테스트
        print("\n9. 명령어 빈도 통계 테스트...")
        stats = db_manager.get_command_frequency_stats()
        print(f"✅ 명령어 빈도 통계:")
        print(f"   - 총 명령어: {stats.get('total_commands', 0)}개")
        
        print("\n🎉 모든 데이터베이스 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 데이터베이스 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_database())
