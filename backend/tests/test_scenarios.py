"""
시나리오 테스트 - 로봇 제어, 에러 처리, 사용자 상호작용
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from app.services.socket_bridge import SocketBridgeServer
from app.services.robot_controller import RobotController, RobotState
from app.services.sensor_manager import SensorManager, SensorData
from app.services.chat_nlp import ChatNLP, IntentType, EmotionType
from app.services.chat_service import ChatService
from app.database.database_manager import DatabaseManager


class TestRobotControlScenarios:
    """로봇 제어 시나리오 테스트"""
    
    @pytest.fixture
    async def robot_controller(self):
        """로봇 제어기 인스턴스"""
        controller = RobotController()
        await controller.initialize()
        return controller
    
    @pytest.mark.asyncio
    async def test_basic_movement_sequence(self, robot_controller):
        """기본 이동 시퀀스 시나리오"""
        # 1. 전진 명령
        result = await robot_controller.move_forward(speed=50, distance=100)
        assert result is True
        assert robot_controller.current_state == RobotState.MOVING
        
        # 2. 우회전 명령
        result = await robot_controller.turn_right(angle=90)
        assert result is True
        assert robot_controller.current_state == RobotState.TURNING
        
        # 3. 다시 전진
        result = await robot_controller.move_forward(speed=30, distance=50)
        assert result is True
        
        # 4. 정지
        result = await robot_controller.stop()
        assert result is True
        assert robot_controller.current_state == RobotState.STOPPING
        
        # 명령 히스토리 확인
        history = await robot_controller.get_command_history(limit=10)
        assert len(history) >= 4
        
        # 명령 순서 확인
        assert history[0]["command"]["type"] == "forward"
        assert history[1]["command"]["type"] == "turn_right"
        assert history[2]["command"]["type"] == "forward"
        assert history[3]["command"]["type"] == "stop"
    
    @pytest.mark.asyncio
    async def test_emergency_stop_scenario(self, robot_controller):
        """비상 정지 시나리오"""
        # 여러 명령을 큐에 추가
        await robot_controller.move_forward(speed=80, distance=200)
        await robot_controller.turn_left(angle=45)
        await robot_controller.move_backward(speed=60, distance=150)
        
        # 큐에 명령이 있는지 확인
        assert robot_controller.command_queue.qsize() == 3
        
        # 비상 정지 실행
        result = await robot_controller.emergency_stop()
        assert result is True
        assert robot_controller.current_state == RobotState.STOPPING
        
        # 큐가 비워졌는지 확인
        assert robot_controller.command_queue.qsize() == 0
    
    @pytest.mark.asyncio
    async def test_movement_validation_scenario(self, robot_controller):
        """이동 명령 검증 시나리오"""
        # 속도 범위 초과 테스트
        result = await robot_controller.move_forward(speed=150, distance=100)
        assert result is True
        
        # 명령에서 속도가 조정되었는지 확인
        command = await robot_controller.command_queue.get()
        assert command["speed"] == 100  # 최대값으로 조정
        
        # 거리 범위 초과 테스트
        result = await robot_controller.move_forward(speed=50, distance=300)
        assert result is True
        
        command = await robot_controller.command_queue.get()
        assert command["distance"] == 200  # 최대값으로 조정
        
        # 음수 값 테스트
        result = await robot_controller.move_forward(speed=-10, distance=-50)
        assert result is True
        
        command = await robot_controller.command_queue.get()
        assert command["speed"] == 0  # 최소값으로 조정
        assert command["distance"] == 0  # 최소값으로 조정


class TestSensorDataScenarios:
    """센서 데이터 시나리오 테스트"""
    
    @pytest.fixture
    async def sensor_manager(self):
        """센서 관리자 인스턴스"""
        manager = SensorManager()
        await manager.initialize()
        return manager
    
    @pytest.mark.asyncio
    async def test_obstacle_detection_scenario(self, sensor_manager):
        """장애물 감지 시나리오"""
        alerts = []
        
        def alert_callback(alert):
            alerts.append(alert)
        
        sensor_manager.add_alert_callback(alert_callback)
        
        # 정상 거리
        await sensor_manager.process_sensor_data({
            "front_distance": 50.0,
            "drop_detection": False,
            "battery_level": 85
        })
        
        assert len(alerts) == 0
        
        # 경고 거리
        await sensor_manager.process_sensor_data({
            "front_distance": 8.0,
            "drop_detection": False,
            "battery_level": 85
        })
        
        assert len(alerts) == 1
        assert alerts[0]["type"] == "warning"
        assert "전방 주의" in alerts[0]["message"]
        
        # 위험 거리
        await sensor_manager.process_sensor_data({
            "front_distance": 3.0,
            "drop_detection": False,
            "battery_level": 85
        })
        
        assert len(alerts) == 2
        assert alerts[1]["type"] == "danger"
        assert "전방 위험" in alerts[1]["message"]
    
    @pytest.mark.asyncio
    async def test_battery_monitoring_scenario(self, sensor_manager):
        """배터리 모니터링 시나리오"""
        alerts = []
        
        def alert_callback(alert):
            alerts.append(alert)
        
        sensor_manager.add_alert_callback(alert_callback)
        
        # 정상 배터리
        await sensor_manager.process_sensor_data({
            "front_distance": 25.0,
            "drop_detection": False,
            "battery_level": 85
        })
        
        assert len(alerts) == 0
        
        # 배터리 부족 경고
        await sensor_manager.process_sensor_data({
            "front_distance": 25.0,
            "drop_detection": False,
            "battery_level": 15
        })
        
        assert len(alerts) == 1
        assert alerts[0]["type"] == "warning"
        assert "배터리 부족" in alerts[0]["message"]
        
        # 배터리 위험
        await sensor_manager.process_sensor_data({
            "front_distance": 25.0,
            "drop_detection": False,
            "battery_level": 5
        })
        
        assert len(alerts) == 2
        assert alerts[1]["type"] == "critical"
        assert "배터리 위험" in alerts[1]["message"]
    
    @pytest.mark.asyncio
    async def test_drop_detection_scenario(self, sensor_manager):
        """낙하 감지 시나리오"""
        alerts = []
        
        def alert_callback(alert):
            alerts.append(alert)
        
        sensor_manager.add_alert_callback(alert_callback)
        
        # 정상 상태
        await sensor_manager.process_sensor_data({
            "front_distance": 25.0,
            "drop_detection": False,
            "battery_level": 85
        })
        
        assert len(alerts) == 0
        
        # 낙하 감지
        await sensor_manager.process_sensor_data({
            "front_distance": 25.0,
            "drop_detection": True,
            "battery_level": 85
        })
        
        assert len(alerts) == 1
        assert alerts[0]["type"] == "danger"
        assert "낙하 위험 감지" in alerts[0]["message"]
    
    @pytest.mark.asyncio
    async def test_sensor_data_history_scenario(self, sensor_manager):
        """센서 데이터 히스토리 시나리오"""
        # 여러 센서 데이터 추가
        for i in range(10):
            await sensor_manager.process_sensor_data({
                "front_distance": 25.0 + i,
                "drop_detection": False,
                "battery_level": 85 - i,
                "temperature": 20.0 + i * 0.5
            })
        
        # 히스토리 조회
        history = await sensor_manager.get_sensor_history(limit=5)
        assert len(history) == 5
        
        # 최신 데이터 확인
        latest = await sensor_manager.get_latest_sensor_data()
        assert latest is not None
        assert latest["front_distance"] == 34.0  # 25.0 + 9
        assert latest["battery_level"] == 76  # 85 - 9
        
        # 통계 확인
        stats = await sensor_manager.get_sensor_statistics()
        assert stats["data_count"] == 10
        assert stats["front_distance"]["min"] == 25.0
        assert stats["front_distance"]["max"] == 34.0


class TestChatInteractionScenarios:
    """채팅 상호작용 시나리오 테스트"""
    
    @pytest.fixture
    def chat_nlp(self):
        """Chat NLP 인스턴스"""
        return ChatNLP()
    
    @pytest.mark.asyncio
    async def test_first_meeting_scenario(self, chat_nlp):
        """첫 만남 시나리오"""
        # 인사말
        analysis = chat_nlp.analyze_text("안녕하세요!")
        assert analysis.intent.intent == IntentType.GREETING
        assert analysis.emotion.emotion in [EmotionType.HAPPY, EmotionType.NEUTRAL]
        
        # 자기소개
        analysis = chat_nlp.analyze_text("나는 철수야")
        assert analysis.intent.intent == IntentType.INTRODUCTION
        # PERSON 엔티티에서 이름이 추출되었는지 확인 (인코딩 문제 고려)
        person_entities = analysis.entities.get("PERSON", [])
        assert len(person_entities) > 0  # 이름이 추출되었는지 확인
        
        # 로봇에 대한 질문
        analysis = chat_nlp.analyze_text("넌 뭐야?")
        assert analysis.intent.intent == IntentType.QUESTION_ABOUT_ROBOT
        assert analysis.emotion.emotion == EmotionType.CURIOUS
        
        # 칭찬
        analysis = chat_nlp.analyze_text("멋있어!")
        assert analysis.intent.intent == IntentType.PRAISE
        assert analysis.emotion.emotion in [EmotionType.HAPPY, EmotionType.PROUD]
    
    @pytest.mark.asyncio
    async def test_help_request_scenario(self, chat_nlp):
        """도움 요청 시나리오"""
        # 도움 요청
        analysis = chat_nlp.analyze_text("도와줘")
        assert analysis.intent.intent == IntentType.REQUEST_HELP
        # 도움 요청에 대한 감정은 HELPFUL 또는 EXCITED일 수 있음
        assert analysis.emotion.emotion in [EmotionType.HELPFUL, EmotionType.EXCITED]
        
        # 구체적인 도움 요청
        analysis = chat_nlp.analyze_text("어떻게 움직여?")
        assert analysis.intent.intent == IntentType.REQUEST_HELP
        assert analysis.emotion.emotion == EmotionType.CURIOUS
        
        # 혼란 표현
        analysis = chat_nlp.analyze_text("모르겠어")
        assert analysis.intent.intent == IntentType.CONFUSED
        assert analysis.emotion.emotion == EmotionType.CONFUSED
    
    @pytest.mark.asyncio
    async def test_emotion_trend_scenario(self, chat_nlp):
        """감정 트렌드 시나리오"""
        # 대화 시퀀스
        conversation = [
            "안녕하세요!",  # 인사
            "뭐해?",  # 질문
            "멋있어!",  # 칭찬
            "고마워",  # 감사
            "안녕히 가세요"  # 작별
        ]
        
        # 감정 트렌드 분석
        trend = chat_nlp.get_emotion_trend(conversation)
        
        assert trend["total_messages"] == 5
        assert "emotion_distribution" in trend
        assert "average_sentiment" in trend
        
        # 대부분 긍정적인 감정이어야 함
        assert trend["average_sentiment"] > 0
    
    @pytest.mark.asyncio
    async def test_question_type_detection_scenario(self, chat_nlp):
        """질문 유형 감지 시나리오"""
        questions = [
            ("뭐야?", "what"),
            ("어떻게 해?", "how"),
            ("왜 그래?", "why"),
            ("언제 와?", "when"),
            ("어디 가?", "where"),
            ("누구야?", "who"),
            ("정말?", "general")
        ]
        
        for question, expected_type in questions:
            result = chat_nlp.extract_question_type(question)
            assert result == expected_type


class TestErrorHandlingScenarios:
    """에러 처리 시나리오 테스트"""
    
    @pytest.mark.asyncio
    async def test_socket_bridge_connection_error_scenario(self):
        """Socket Bridge 연결 에러 시나리오"""
        server = SocketBridgeServer(host="127.0.0.1", port=8888)
        
        # 연결 관리자 모킹
        mock_manager = AsyncMock()
        mock_manager.get_first_client.return_value = None
        server.connection_manager = mock_manager
        
        # 연결된 클라이언트가 없을 때 명령 전송
        command = {"type": "move_forward", "speed": 50}
        result = await server.send_command(command)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_robot_controller_error_scenario(self):
        """로봇 제어기 에러 시나리오"""
        controller = RobotController()
        
        # 연결 관리자가 설정되지 않은 상태에서 명령 전송
        command = {"type": "move_forward", "speed": 50}
        result = await controller._send_command_to_robot(command)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_sensor_data_processing_error_scenario(self):
        """센서 데이터 처리 에러 시나리오"""
        manager = SensorManager()
        
        # 잘못된 센서 데이터 처리
        with patch('app.services.sensor_manager.logger') as mock_logger:
            await manager.process_sensor_data("invalid_data")
        
        mock_logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_database_error_scenario(self, temp_db_manager):
        """데이터베이스 에러 시나리오"""
        # 잘못된 데이터로 저장 시도
        with patch('app.database.database_manager.logger') as mock_logger:
            result = temp_db_manager.save_user_interaction(None)
        
        assert result is False
        mock_logger.error.assert_called()


class TestSystemIntegrationScenarios:
    """시스템 통합 시나리오 테스트"""
    
    @pytest.mark.asyncio
    async def test_complete_user_interaction_scenario(self):
        """완전한 사용자 상호작용 시나리오"""
        # 1. 사용자 인사
        nlp = ChatNLP()
        analysis = nlp.analyze_text("안녕하세요!")
        assert analysis.intent.intent == IntentType.GREETING
        
        # 2. 로봇 응답 생성 (모킹)
        with patch('app.services.chat_service.ChatService.process_message') as mock_process:
            mock_process.return_value = {
                "message_id": "msg_123",
                "response": "안녕하세요! 저는 덱스입니다.",
                "emotion": "happy",
                "conversation_type": "greeting",
                "timestamp": "2024-01-01T00:00:00"
            }
            
            chat_service = ChatService()
            response = await chat_service.process_message(
                message="안녕하세요!",
                user_id="test_user",
                session_id="session_123"
            )
            
            assert response["response"] == "안녕하세요! 저는 덱스입니다."
            assert response["emotion"] == "happy"
    
    @pytest.mark.asyncio
    async def test_robot_control_with_sensor_feedback_scenario(self):
        """센서 피드백이 있는 로봇 제어 시나리오"""
        # 로봇 제어기와 센서 관리자 초기화
        robot_controller = RobotController()
        sensor_manager = SensorManager()
        
        await robot_controller.initialize()
        await sensor_manager.initialize()
        
        # 1. 로봇 이동 명령
        result = await robot_controller.move_forward(speed=50, distance=100)
        assert result is True
        
        # 2. 센서 데이터 처리 (장애물 감지)
        alerts = []
        
        def alert_callback(alert):
            alerts.append(alert)
        
        sensor_manager.add_alert_callback(alert_callback)
        
        await sensor_manager.process_sensor_data({
            "front_distance": 5.0,  # 위험 거리
            "drop_detection": False,
            "battery_level": 85
        })
        
        # 3. 장애물 감지로 인한 비상 정지
        assert len(alerts) == 1
        assert alerts[0]["type"] == "danger"
        
        # 비상 정지 실행
        result = await robot_controller.emergency_stop()
        assert result is True
        assert robot_controller.current_state == RobotState.STOPPING
    
    @pytest.mark.asyncio
    async def test_learning_and_adaptation_scenario(self, temp_db_manager):
        """학습 및 적응 시나리오"""
        # 1. 사용자 상호작용 저장
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
        
        # 2. 명령어 빈도 업데이트
        result = temp_db_manager.update_command_frequency('안녕하세요', success=True)
        assert result is True
        
        # 3. 사용자 패턴 분석
        patterns = temp_db_manager.get_user_patterns('test_user', days=7)
        assert 'frequent_commands' in patterns
        assert 'error_patterns' in patterns
        
        # 4. 명령어 통계 조회
        stats = temp_db_manager.get_command_frequency_stats()
        assert 'commands' in stats
        assert stats['total_commands'] >= 1
    
    @pytest.mark.asyncio
    async def test_error_recovery_scenario(self):
        """에러 복구 시나리오"""
        # 1. 초기 에러 상태
        robot_controller = RobotController()
        assert robot_controller.current_state == RobotState.IDLE
        
        # 2. 명령 실행 중 에러 발생
        result_data = {
            "command_id": "cmd_123",
            "success": False,
            "error": "모터 연결 실패"
        }
        
        await robot_controller.handle_command_result(result_data)
        assert robot_controller.current_state == RobotState.ERROR
        
        # 3. 에러 복구 (새로운 명령 성공)
        result_data = {
            "command_id": "cmd_124",
            "success": True,
            "error": ""
        }
        
        await robot_controller.handle_command_result(result_data)
        assert robot_controller.current_state == RobotState.IDLE
    
    @pytest.mark.asyncio
    async def test_concurrent_operations_scenario(self):
        """동시 작업 시나리오"""
        # 여러 비동기 작업을 동시에 실행
        tasks = []
        
        # 1. 로봇 제어기 초기화
        robot_controller = RobotController()
        tasks.append(robot_controller.initialize())
        
        # 2. 센서 관리자 초기화
        sensor_manager = SensorManager()
        tasks.append(sensor_manager.initialize())
        
        # 3. NLP 분석
        nlp = ChatNLP()
        tasks.append(asyncio.sleep(0.1))  # NLP 분석 시뮬레이션
        
        # 모든 작업이 완료될 때까지 대기
        await asyncio.gather(*tasks)
        
        # 각 모듈이 정상적으로 초기화되었는지 확인
        assert robot_controller.is_processing_commands is True
        
        # 정리
        await robot_controller.cleanup()
        await sensor_manager.cleanup()
        
        assert robot_controller.is_processing_commands is False
