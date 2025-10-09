"""
API 엔드포인트 통합 테스트
"""

import pytest
import json
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock, patch
import tempfile
import os

from app.main import app
from app.database.database_manager import DatabaseManager


class TestAPIIntegration:
    """API 통합 테스트 클래스"""
    
    @pytest.fixture
    def client(self):
        """테스트 클라이언트 생성"""
        return TestClient(app)
    
    @pytest.fixture
    def temp_db_manager(self):
        """임시 데이터베이스 매니저 생성"""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        manager = DatabaseManager()
        manager.db_path = temp_db.name
        
        # 테스트용 테이블 생성
        with manager.get_connection() as conn:
            cursor = conn.cursor()
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
            conn.commit()
        
        yield manager
        os.unlink(temp_db.name)
    
    def test_root_endpoint(self, client):
        """루트 엔드포인트 테스트"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "redoc" in data
        assert "Deks 1.0" in data["message"]
    
    def test_health_check_endpoint(self, client):
        """헬스 체크 엔드포인트 테스트"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "deks-backend"
        assert "version" in data
        assert "timestamp" in data
    
    def test_socket_bridge_status_endpoint(self, client):
        """Socket Bridge 상태 엔드포인트 테스트"""
        response = client.get("/socket-bridge/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "is_running" in data
        assert "host" in data
        assert "port" in data
        assert "protocol_version" in data
    
    def test_docs_endpoint(self, client):
        """API 문서 엔드포인트 테스트"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_endpoint(self, client):
        """ReDoc 문서 엔드포인트 테스트"""
        response = client.get("/redoc")
        assert response.status_code == 200
    
    @patch('app.services.chat_service.ChatService.process_message')
    def test_chat_message_endpoint_success(self, mock_process_message, client):
        """채팅 메시지 엔드포인트 성공 테스트"""
        # 모킹된 응답 데이터
        mock_response = {
            "message_id": "msg_123",
            "response": "안녕하세요! 저는 덱스입니다.",
            "emotion": "happy",
            "conversation_type": "greeting",
            "timestamp": "2024-01-01T00:00:00",
            "context": {"session_id": "session_123"},
            "nlp_analysis": {"intent": "greeting", "confidence": 0.9}
        }
        mock_process_message.return_value = mock_response
        
        # 요청 데이터
        request_data = {
            "message": "안녕하세요",
            "user_id": "test_user",
            "session_id": "session_123"
        }
        
        response = client.post("/api/v1/chat/message", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message_id"] == "msg_123"
        assert data["response"] == "안녕하세요! 저는 덱스입니다."
        assert data["emotion"] == "happy"
        assert data["conversation_type"] == "greeting"
        assert "timestamp" in data
        assert data["context"]["session_id"] == "session_123"
        assert data["nlp_analysis"]["intent"] == "greeting"
        
        # 서비스 메서드가 호출되었는지 확인
        mock_process_message.assert_called_once_with(
            message="안녕하세요",
            user_id="test_user",
            session_id="session_123"
        )
    
    def test_chat_message_endpoint_invalid_request(self, client):
        """채팅 메시지 엔드포인트 잘못된 요청 테스트"""
        # 필수 필드 누락
        request_data = {
            "user_id": "test_user"
            # message 필드 누락
        }
        
        response = client.post("/api/v1/chat/message", json=request_data)
        
        assert response.status_code == 422  # Validation Error
    
    @patch('app.services.chat_service.ChatService.process_message')
    def test_chat_message_endpoint_service_error(self, mock_process_message, client):
        """채팅 메시지 엔드포인트 서비스 에러 테스트"""
        # 서비스에서 에러 발생
        mock_process_message.side_effect = Exception("서비스 오류")
        
        request_data = {
            "message": "안녕하세요",
            "user_id": "test_user"
        }
        
        response = client.post("/api/v1/chat/message", json=request_data)
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "오류가 발생했습니다" in data["detail"]
    
    @patch('app.services.chat_service.ChatService.get_chat_history')
    def test_chat_history_endpoint_success(self, mock_get_history, client):
        """채팅 기록 조회 엔드포인트 성공 테스트"""
        # 모킹된 응답 데이터
        mock_conversations = [
            {
                "id": 1,
                "message": "안녕하세요",
                "response": "안녕하세요!",
                "timestamp": "2024-01-01T00:00:00",
                "emotion": "happy"
            },
            {
                "id": 2,
                "message": "뭐해?",
                "response": "대기 중입니다.",
                "timestamp": "2024-01-01T00:01:00",
                "emotion": "neutral"
            }
        ]
        mock_get_history.return_value = mock_conversations
        
        response = client.get("/api/v1/chat/history?user_id=test_user&limit=10&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["conversations"]) == 2
        assert data["total_count"] >= 0
        assert "has_more" in data
        assert data["conversations"][0]["message"] == "안녕하세요"
        assert data["conversations"][1]["message"] == "뭐해?"
    
    def test_chat_history_endpoint_missing_user_id(self, client):
        """채팅 기록 조회 엔드포인트 - user_id 누락 테스트"""
        response = client.get("/api/v1/chat/history")
        
        assert response.status_code == 422  # Validation Error
    
    @patch('app.services.chat_service.ChatService.get_chat_context')
    def test_chat_context_endpoint_success(self, mock_get_context, client):
        """채팅 컨텍스트 조회 엔드포인트 성공 테스트"""
        # 모킹된 응답 데이터
        mock_context = {
            "session_id": "session_123",
            "user_id": "test_user",
            "current_emotion": "happy",
            "conversation_count": 5,
            "last_interaction": "2024-01-01T00:00:00"
        }
        mock_get_context.return_value = mock_context
        
        response = client.get("/api/v1/chat/context?user_id=test_user&session_id=session_123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["context"]["session_id"] == "session_123"
        assert data["context"]["user_id"] == "test_user"
        assert data["context"]["current_emotion"] == "happy"
    
    def test_chat_context_endpoint_missing_user_id(self, client):
        """채팅 컨텍스트 조회 엔드포인트 - user_id 누락 테스트"""
        response = client.get("/api/v1/chat/context")
        
        assert response.status_code == 422  # Validation Error
    
    @patch('app.services.chat_service.ChatService.update_emotion')
    def test_emotion_update_endpoint_success(self, mock_update_emotion, client):
        """감정 상태 업데이트 엔드포인트 성공 테스트"""
        # 모킹된 응답 데이터
        mock_emotion_data = {
            "emotion": "excited",
            "led_expression": "bright_eyes",
            "buzzer_sound": "happy_beep",
            "timestamp": "2024-01-01T00:00:00"
        }
        mock_update_emotion.return_value = mock_emotion_data
        
        request_data = {
            "emotion": "excited",
            "user_id": "test_user",
            "reason": "사용자가 기뻐함"
        }
        
        response = client.post("/api/v1/chat/emotion", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["emotion_updated"] == "excited"
        assert data["led_expression"] == "bright_eyes"
        assert data["buzzer_sound"] == "happy_beep"
        assert "timestamp" in data
        
        # 서비스 메서드가 호출되었는지 확인
        mock_update_emotion.assert_called_once_with(
            emotion="excited",
            user_id="test_user",
            reason="사용자가 기뻐함"
        )
    
    def test_emotion_update_endpoint_invalid_request(self, client):
        """감정 상태 업데이트 엔드포인트 잘못된 요청 테스트"""
        # 필수 필드 누락
        request_data = {
            "user_id": "test_user"
            # emotion 필드 누락
        }
        
        response = client.post("/api/v1/chat/emotion", json=request_data)
        
        assert response.status_code == 422  # Validation Error
    
    @patch('app.services.chat_service.ChatService.update_learning_data')
    def test_learning_data_endpoint_success(self, mock_update_learning, client):
        """학습 데이터 업데이트 엔드포인트 성공 테스트"""
        # 모킹된 응답 데이터
        mock_learning_result = {
            "patterns_learned": 2,
            "confidence_improved": 0.1,
            "new_keywords": ["안녕", "뭐해"]
        }
        mock_update_learning.return_value = mock_learning_result
        
        request_data = {
            "user_id": "test_user",
            "interaction_data": {
                "message": "안녕하세요",
                "response": "안녕하세요!",
                "success": True,
                "timestamp": "2024-01-01T00:00:00"
            }
        }
        
        response = client.post("/api/v1/chat/learning", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "학습 데이터가 성공적으로 업데이트되었습니다" in data["message"]
        assert data["learning_result"]["patterns_learned"] == 2
        assert "timestamp" in data
        
        # 서비스 메서드가 호출되었는지 확인
        mock_update_learning.assert_called_once_with(
            user_id="test_user",
            interaction_data=request_data["interaction_data"]
        )
    
    def test_learning_data_endpoint_invalid_request(self, client):
        """학습 데이터 업데이트 엔드포인트 잘못된 요청 테스트"""
        # 필수 필드 누락
        request_data = {
            "user_id": "test_user"
            # interaction_data 필드 누락
        }
        
        response = client.post("/api/v1/chat/learning", json=request_data)
        
        assert response.status_code == 422  # Validation Error
    
    @patch('app.services.chat_service.ChatService.get_conversation_patterns')
    def test_conversation_patterns_endpoint_success(self, mock_get_patterns, client):
        """대화 패턴 조회 엔드포인트 성공 테스트"""
        # 모킹된 응답 데이터
        mock_patterns = {
            "greeting": {
                "keywords": ["안녕", "하이", "헬로"],
                "responses": ["안녕하세요!", "반갑습니다!"]
            },
            "question": {
                "keywords": ["뭐야", "어떻게", "왜"],
                "responses": ["좋은 질문이네요!", "설명해드릴게요!"]
            }
        }
        mock_get_patterns.return_value = mock_patterns
        
        response = client.get("/api/v1/chat/patterns")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "greeting" in data["patterns"]
        assert "question" in data["patterns"]
        assert data["patterns"]["greeting"]["keywords"] == ["안녕", "하이", "헬로"]
        assert "timestamp" in data
    
    @patch('app.services.chat_service.ChatService.get_emotion_states')
    def test_emotion_states_endpoint_success(self, mock_get_emotions, client):
        """감정 상태 조회 엔드포인트 성공 테스트"""
        # 모킹된 응답 데이터
        mock_emotions = {
            "happy": {
                "description": "기쁨",
                "led_color": "yellow",
                "buzzer_sound": "happy_beep"
            },
            "sad": {
                "description": "슬픔",
                "led_color": "blue",
                "buzzer_sound": "sad_tone"
            }
        }
        mock_get_emotions.return_value = mock_emotions
        
        response = client.get("/api/v1/chat/emotions")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "happy" in data["emotions"]
        assert "sad" in data["emotions"]
        assert data["emotions"]["happy"]["description"] == "기쁨"
        assert data["emotions"]["happy"]["led_color"] == "yellow"
        assert "timestamp" in data
    
    def test_cors_headers(self, client):
        """CORS 헤더 테스트"""
        # OPTIONS 메서드 대신 GET 메서드로 CORS 헤더 확인
        response = client.get("/api/v1/chat/message")
        
        # CORS 헤더가 설정되어 있는지 확인
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Allow-Headers" in response.headers
    
    def test_api_v1_prefix(self, client):
        """API v1 프리픽스 테스트"""
        # 올바른 프리픽스로 요청
        response = client.get("/api/v1/chat/patterns")
        assert response.status_code == 200
        
        # 잘못된 프리픽스로 요청
        response = client.get("/api/v2/chat/patterns")
        assert response.status_code == 404
    
    @patch('app.services.chat_service.ChatService')
    def test_chat_service_integration_error_handling(self, mock_chat_service_class, client):
        """채팅 서비스 통합 에러 처리 테스트"""
        # 채팅 서비스 인스턴스 모킹
        mock_chat_service = AsyncMock()
        mock_chat_service.process_message.side_effect = Exception("데이터베이스 연결 오류")
        mock_chat_service_class.return_value = mock_chat_service
        
        # 패치 적용
        with patch('app.api.v1.endpoints.chat.chat_service', mock_chat_service):
            request_data = {
                "message": "안녕하세요",
                "user_id": "test_user"
            }
            
            response = client.post("/api/v1/chat/message", json=request_data)
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "오류가 발생했습니다" in data["detail"]
    
    def test_request_validation(self, client):
        """요청 데이터 검증 테스트"""
        # 빈 요청
        response = client.post("/api/v1/chat/message", json={})
        assert response.status_code == 422
        
        # 잘못된 타입
        response = client.post("/api/v1/chat/message", json={"message": 123})
        assert response.status_code == 422
        
        # 추가 필드 포함 (정상 처리되어야 함)
        request_data = {
            "message": "안녕하세요",
            "user_id": "test_user",
            "extra_field": "ignored"
        }
        
        with patch('app.services.chat_service.ChatService.process_message') as mock_process:
            mock_process.return_value = {
                "message_id": "msg_123",
                "response": "안녕하세요!",
                "emotion": "happy",
                "conversation_type": "greeting",
                "timestamp": "2024-01-01T00:00:00"
            }
            
            response = client.post("/api/v1/chat/message", json=request_data)
            assert response.status_code == 200
    
    @patch('app.services.chat_service.ChatService.process_message')
    def test_chat_message_with_optional_fields(self, mock_process_message, client):
        """선택적 필드를 포함한 채팅 메시지 테스트"""
        mock_response = {
            "message_id": "msg_123",
            "response": "안녕하세요!",
            "emotion": "happy",
            "conversation_type": "greeting",
            "timestamp": "2024-01-01T00:00:00"
        }
        mock_process_message.return_value = mock_response
        
        # session_id 없이 요청
        request_data = {
            "message": "안녕하세요",
            "user_id": "test_user"
        }
        
        response = client.post("/api/v1/chat/message", json=request_data)
        
        assert response.status_code == 200
        # session_id가 자동 생성되었는지 확인
        mock_process_message.assert_called_once()
        call_args = mock_process_message.call_args
        assert call_args[1]["message"] == "안녕하세요"
        assert call_args[1]["user_id"] == "test_user"
        assert call_args[1]["session_id"] is not None  # 자동 생성됨
    
    def test_query_parameters_validation(self, client):
        """쿼리 매개변수 검증 테스트"""
        # 정상적인 쿼리 매개변수
        with patch('app.services.chat_service.ChatService.get_chat_history') as mock_get_history:
            mock_get_history.return_value = []
            
            response = client.get("/api/v1/chat/history?user_id=test_user&limit=10&offset=0")
            assert response.status_code == 200
        
        # 잘못된 타입의 쿼리 매개변수
        response = client.get("/api/v1/chat/history?user_id=test_user&limit=invalid&offset=0")
        assert response.status_code == 422
        
        # 기본값 사용
        with patch('app.services.chat_service.ChatService.get_chat_history') as mock_get_history:
            mock_get_history.return_value = []
            
            response = client.get("/api/v1/chat/history?user_id=test_user")
            assert response.status_code == 200
            
            # 기본값이 사용되었는지 확인
            call_args = mock_get_history.call_args
            assert call_args[1]["limit"] == 20  # 기본값
            assert call_args[1]["offset"] == 0  # 기본값
