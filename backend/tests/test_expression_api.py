"""
Deks 1.0 Expression API 테스트
5순위 작업: LED 표정, 버저 소리 제어 고도화
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app
from app.api.v1.endpoints.expression import (
    SUPPORTED_EXPRESSIONS,
    SUPPORTED_SOUNDS,
    EMOTION_EXPRESSIONS
)

client = TestClient(app)


class TestExpressionAPI:
    """Expression API 테스트"""
    
    def test_led_expression_basic(self):
        """기본 LED 표정 설정 테스트"""
        response = client.post("/api/v1/expression/led", json={
            "expression": "happy",
            "duration": 3000,
            "brightness": 100,
            "user_id": "test_user"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["expression"] == "happy"
        assert data["brightness"] == 100
        assert data["duration"] == 3000
        assert "command_id" in data
        assert "timestamp" in data
    
    def test_led_expression_with_animation(self):
        """애니메이션과 함께 LED 표정 설정 테스트"""
        response = client.post("/api/v1/expression/led", json={
            "expression": "happy",
            "duration": 2000,
            "brightness": 80,
            "animation": "sparkle",
            "user_id": "test_user"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["animation"] == "sparkle"
    
    def test_led_expression_invalid_expression(self):
        """잘못된 LED 표정 테스트"""
        response = client.post("/api/v1/expression/led", json={
            "expression": "invalid_expression",
            "duration": 3000,
            "user_id": "test_user"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "지원하지 않는 표정" in data["message"]
    
    def test_led_expression_invalid_animation(self):
        """잘못된 애니메이션 테스트"""
        response = client.post("/api/v1/expression/led", json={
            "expression": "happy",
            "duration": 3000,
            "animation": "invalid_animation",
            "user_id": "test_user"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "지원하지 않는 애니메이션" in data["message"]
    
    def test_led_expression_validation(self):
        """LED 표정 유효성 검사 테스트"""
        # 지속시간이 너무 짧은 경우
        response = client.post("/api/v1/expression/led", json={
            "expression": "happy",
            "duration": 50,  # 최소 100ms
            "user_id": "test_user"
        })
        assert response.status_code == 400  # Pydantic 유효성 검사는 400으로 처리됨
        
        # 지속시간이 너무 긴 경우
        response = client.post("/api/v1/expression/led", json={
            "expression": "happy",
            "duration": 35000,  # 최대 30000ms
            "user_id": "test_user"
        })
        assert response.status_code == 400  # Pydantic 유효성 검사는 400으로 처리됨
        
        # 밝기가 범위를 벗어난 경우
        response = client.post("/api/v1/expression/led", json={
            "expression": "happy",
            "brightness": 150,  # 최대 100%
            "user_id": "test_user"
        })
        assert response.status_code == 400  # Pydantic 유효성 검사는 400으로 처리됨
    
    def test_buzzer_sound_basic(self):
        """기본 버저 소리 설정 테스트"""
        response = client.post("/api/v1/expression/buzzer", json={
            "sound": "beep",
            "frequency": 1000,
            "duration": 500,
            "volume": 80,
            "user_id": "test_user"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["sound"] == "beep"
        assert data["frequency"] == 1000
        assert data["volume"] == 80
        assert data["duration"] == 500
    
    def test_buzzer_sound_with_melody(self):
        """커스텀 멜로디와 함께 버저 소리 설정 테스트"""
        response = client.post("/api/v1/expression/buzzer", json={
            "sound": "melody",
            "frequency": 1000,
            "duration": 1000,
            "volume": 90,
            "melody": [440, 523, 659, 784],  # A, C, E, G
            "user_id": "test_user"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["melody"] == [440, 523, 659, 784]
    
    def test_buzzer_sound_invalid_sound(self):
        """잘못된 버저 소리 테스트"""
        response = client.post("/api/v1/expression/buzzer", json={
            "sound": "invalid_sound",
            "frequency": 1000,
            "duration": 500,
            "user_id": "test_user"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "지원하지 않는 소리" in data["message"]
    
    def test_buzzer_sound_invalid_melody(self):
        """잘못된 멜로디 테스트"""
        # 너무 긴 멜로디
        response = client.post("/api/v1/expression/buzzer", json={
            "sound": "melody",
            "frequency": 1000,
            "duration": 1000,
            "melody": [440] * 25,  # 최대 20개
            "user_id": "test_user"
        })
        assert response.status_code == 400
        data = response.json()
        assert "최대 20개 음표" in data["message"]
        
        # 범위를 벗어난 주파수
        response = client.post("/api/v1/expression/buzzer", json={
            "sound": "melody",
            "frequency": 1000,
            "duration": 1000,
            "melody": [100, 6000],  # 200-5000Hz 범위
            "user_id": "test_user"
        })
        assert response.status_code == 400
        data = response.json()
        assert "200-5000Hz 범위" in data["message"]
    
    def test_buzzer_sound_validation(self):
        """버저 소리 유효성 검사 테스트"""
        # 주파수가 범위를 벗어난 경우
        response = client.post("/api/v1/expression/buzzer", json={
            "sound": "beep",
            "frequency": 100,  # 최소 200Hz
            "duration": 500,
            "user_id": "test_user"
        })
        assert response.status_code == 400  # Pydantic 유효성 검사는 400으로 처리됨
        
        # 지속시간이 너무 짧은 경우
        response = client.post("/api/v1/expression/buzzer", json={
            "sound": "beep",
            "frequency": 1000,
            "duration": 30,  # 최소 50ms
            "user_id": "test_user"
        })
        assert response.status_code == 400  # Pydantic 유효성 검사는 400으로 처리됨
        
        # 볼륨이 범위를 벗어난 경우
        response = client.post("/api/v1/expression/buzzer", json={
            "sound": "beep",
            "frequency": 1000,
            "duration": 500,
            "volume": 150,  # 최대 100%
            "user_id": "test_user"
        })
        assert response.status_code == 400  # Pydantic 유효성 검사는 400으로 처리됨
    
    def test_emotion_expression_basic(self):
        """기본 감정 표현 테스트"""
        response = client.post("/api/v1/expression/emotion", json={
            "emotion": "happy",
            "intensity": 1.0,
            "user_id": "test_user"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["emotion"] == "happy"
        assert data["intensity"] == 1.0
        assert data["expression"] == "happy"
        assert data["animation"] == "sparkle"
        assert data["sound"] == "success"
    
    def test_emotion_expression_with_intensity(self):
        """강도가 있는 감정 표현 테스트"""
        response = client.post("/api/v1/expression/emotion", json={
            "emotion": "sad",
            "intensity": 0.5,
            "user_id": "test_user"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["intensity"] == 0.5
        assert data["expression"] == "sad"
        assert data["animation"] == "fade"
        assert data["sound"] == "error"
    
    def test_emotion_expression_invalid_emotion(self):
        """잘못된 감정 테스트"""
        response = client.post("/api/v1/expression/emotion", json={
            "emotion": "invalid_emotion",
            "intensity": 1.0,
            "user_id": "test_user"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "지원하지 않는 감정" in data["message"]
    
    def test_emotion_expression_validation(self):
        """감정 표현 유효성 검사 테스트"""
        # 강도가 범위를 벗어난 경우
        response = client.post("/api/v1/expression/emotion", json={
            "emotion": "happy",
            "intensity": 1.5,  # 최대 1.0
            "user_id": "test_user"
        })
        assert response.status_code == 400  # Pydantic 유효성 검사는 400으로 처리됨
        
        response = client.post("/api/v1/expression/emotion", json={
            "emotion": "happy",
            "intensity": -0.5,  # 최소 0.0
            "user_id": "test_user"
        })
        assert response.status_code == 400  # Pydantic 유효성 검사는 400으로 처리됨
    
    def test_pattern_creation_led(self):
        """LED 패턴 생성 테스트"""
        response = client.post("/api/v1/expression/pattern", json={
            "pattern_name": "my_happy_pattern",
            "pattern_type": "led",
            "pattern_data": {
                "expression": "happy",
                "duration": 2000,
                "brightness": 90,
                "animation": "sparkle"
            },
            "user_id": "test_user"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["pattern_name"] == "my_happy_pattern"
        assert data["pattern_type"] == "led"
        assert data["pattern_data"]["expression"] == "happy"
    
    def test_pattern_creation_buzzer(self):
        """버저 패턴 생성 테스트"""
        response = client.post("/api/v1/expression/pattern", json={
            "pattern_name": "my_melody_pattern",
            "pattern_type": "buzzer",
            "pattern_data": {
                "sound": "melody",
                "frequency": 1000,
                "duration": 1500,
                "volume": 85,
                "melody": [440, 523, 659]
            },
            "user_id": "test_user"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["pattern_name"] == "my_melody_pattern"
        assert data["pattern_type"] == "buzzer"
        assert data["pattern_data"]["sound"] == "melody"
    
    def test_pattern_creation_invalid_type(self):
        """잘못된 패턴 타입 테스트"""
        response = client.post("/api/v1/expression/pattern", json={
            "pattern_name": "invalid_pattern",
            "pattern_type": "invalid_type",
            "pattern_data": {"test": "data"},
            "user_id": "test_user"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "led' 또는 'buzzer'" in data["message"]
    
    def test_pattern_creation_missing_fields(self):
        """필수 필드 누락 테스트"""
        # LED 패턴에서 필수 필드 누락
        response = client.post("/api/v1/expression/pattern", json={
            "pattern_name": "incomplete_led",
            "pattern_type": "led",
            "pattern_data": {
                "expression": "happy"
                # duration 누락
            },
            "user_id": "test_user"
        })
        assert response.status_code == 400
        data = response.json()
        assert "필요합니다" in data["message"]
        
        # 버저 패턴에서 필수 필드 누락
        response = client.post("/api/v1/expression/pattern", json={
            "pattern_name": "incomplete_buzzer",
            "pattern_type": "buzzer",
            "pattern_data": {
                "sound": "beep"
                # frequency, duration 누락
            },
            "user_id": "test_user"
        })
        assert response.status_code == 400
        data = response.json()
        assert "필요합니다" in data["message"]
    
    def test_auto_express_situation(self):
        """상황별 자동 표현 테스트"""
        response = client.post("/api/v1/expression/auto-express", params={
            "situation": "command_received",
            "user_id": "test_user"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["situation"] == "command_received"
        assert data["expression"] == "listening"
        assert data["sound"] == "beep"
        assert data["animation"] == "blink"
    
    def test_auto_express_invalid_situation(self):
        """잘못된 상황 테스트"""
        response = client.post("/api/v1/expression/auto-express", params={
            "situation": "invalid_situation",
            "user_id": "test_user"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "지원하지 않는 상황" in data["message"]
    
    def test_get_supported_expressions(self):
        """지원하는 표정 목록 조회 테스트"""
        response = client.get("/api/v1/expression/expressions")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "supported_expressions" in data
        assert "descriptions" in data
        assert "total_count" in data
        
        # 카테고리별 표정 확인
        expressions = data["supported_expressions"]
        assert "basic" in expressions
        assert "status" in expressions
        assert "animation" in expressions
        
        # 총 개수 확인
        total_count = sum(len(category) for category in expressions.values())
        assert data["total_count"] == total_count
    
    def test_get_supported_sounds(self):
        """지원하는 소리 목록 조회 테스트"""
        response = client.get("/api/v1/expression/sounds")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "supported_sounds" in data
        assert "descriptions" in data
        assert "total_count" in data
        
        # 카테고리별 소리 확인
        sounds = data["supported_sounds"]
        assert "notification" in sounds
        assert "melody" in sounds
        assert "alarm" in sounds
        
        # 총 개수 확인
        total_count = sum(len(category) for category in sounds.values())
        assert data["total_count"] == total_count
    
    def test_get_supported_emotions(self):
        """지원하는 감정 목록 조회 테스트"""
        response = client.get("/api/v1/expression/emotions")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "supported_emotions" in data
        assert "emotion_mappings" in data
        assert "total_count" in data
        
        # 감정 목록 확인
        emotions = data["supported_emotions"]
        assert "happy" in emotions
        assert "sad" in emotions
        assert "angry" in emotions
        
        # 매핑 정보 확인
        mappings = data["emotion_mappings"]
        assert "happy" in mappings
        assert mappings["happy"]["expression"] == "happy"
        assert mappings["happy"]["animation"] == "sparkle"
        assert mappings["happy"]["sound"] == "success"
    
    def test_health_check(self):
        """헬스 체크 테스트"""
        response = client.get("/api/v1/expression/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["module"] == "expression"
        assert "supported_expressions" in data
        assert "supported_sounds" in data
        assert "supported_emotions" in data
        assert "features" in data
        assert "timestamp" in data
        
        # 기능 목록 확인
        features = data["features"]
        expected_features = [
            "led_expressions", "buzzer_sounds", "emotion_mapping",
            "custom_patterns", "auto_situations", "animations"
        ]
        for feature in expected_features:
            assert feature in features


class TestExpressionAPIIntegration:
    """Expression API 통합 테스트"""
    
    def test_emotion_to_led_buzzer_flow(self):
        """감정 표현에서 LED/버저로의 흐름 테스트"""
        # 1. 감정 표현 요청
        emotion_response = client.post("/api/v1/expression/emotion", json={
            "emotion": "excited",
            "intensity": 0.8,
            "user_id": "test_user"
        })
        assert emotion_response.status_code == 200
        
        # 2. 해당 감정의 LED 표현 확인
        led_response = client.post("/api/v1/expression/led", json={
            "expression": "happy",  # excited는 happy로 매핑
            "duration": 2400,  # 3000 * 0.8
            "brightness": 80,  # 100 * 0.8
            "animation": "rainbow",
            "user_id": "test_user"
        })
        assert led_response.status_code == 200
        
        # 3. 해당 감정의 버저 소리 확인
        buzzer_response = client.post("/api/v1/expression/buzzer", json={
            "sound": "celebration",
            "frequency": 1000,
            "duration": 400,  # 500 * 0.8
            "volume": 64,  # 80 * 0.8
            "user_id": "test_user"
        })
        assert buzzer_response.status_code == 200
    
    def test_situation_auto_express_flow(self):
        """상황별 자동 표현 흐름 테스트"""
        situations = [
            "command_received", "command_completed", "command_error",
            "user_greeting", "user_farewell", "system_startup",
            "system_shutdown", "low_battery", "connection_lost"
        ]
        
        for situation in situations:
            response = client.post("/api/v1/expression/auto-express", params={
                "situation": situation,
                "user_id": "test_user"
            })
            assert response.status_code == 200
            data = response.json()
            assert data["situation"] == situation
            assert "expression" in data or data["expression"] is None
            assert "sound" in data or data["sound"] is None
            assert "animation" in data or data["animation"] is None
    
    def test_custom_pattern_usage_flow(self):
        """사용자 정의 패턴 사용 흐름 테스트"""
        # 1. LED 패턴 생성
        led_pattern_response = client.post("/api/v1/expression/pattern", json={
            "pattern_name": "welcome_pattern",
            "pattern_type": "led",
            "pattern_data": {
                "expression": "happy",
                "duration": 3000,
                "brightness": 100,
                "animation": "wave"
            },
            "user_id": "test_user"
        })
        assert led_pattern_response.status_code == 200
        
        # 2. 버저 패턴 생성
        buzzer_pattern_response = client.post("/api/v1/expression/pattern", json={
            "pattern_name": "welcome_sound",
            "pattern_type": "buzzer",
            "pattern_data": {
                "sound": "success",
                "frequency": 1200,
                "duration": 800,
                "volume": 90
            },
            "user_id": "test_user"
        })
        assert buzzer_pattern_response.status_code == 200
        
        # 3. 생성된 패턴으로 실제 표현 실행
        led_response = client.post("/api/v1/expression/led", json={
            "expression": "happy",
            "duration": 3000,
            "brightness": 100,
            "animation": "wave",
            "user_id": "test_user"
        })
        assert led_response.status_code == 200
        
        buzzer_response = client.post("/api/v1/expression/buzzer", json={
            "sound": "success",
            "frequency": 1200,
            "duration": 800,
            "volume": 90,
            "user_id": "test_user"
        })
        assert buzzer_response.status_code == 200


class TestExpressionAPIScenarios:
    """Expression API 시나리오 테스트"""
    
    def test_robot_startup_sequence(self):
        """로봇 시작 시퀀스 테스트"""
        # 1. 시스템 시작 알림
        startup_response = client.post("/api/v1/expression/auto-express", params={
            "situation": "system_startup",
            "user_id": "test_user"
        })
        assert startup_response.status_code == 200
        
        # 2. 사용자 인사 대응
        greeting_response = client.post("/api/v1/expression/auto-express", params={
            "situation": "user_greeting",
            "user_id": "test_user"
        })
        assert greeting_response.status_code == 200
        
        # 3. 명령 대기 상태
        waiting_response = client.post("/api/v1/expression/led", json={
            "expression": "waiting",
            "duration": 5000,
            "brightness": 60,
            "user_id": "test_user"
        })
        assert waiting_response.status_code == 200
    
    def test_command_execution_sequence(self):
        """명령 실행 시퀀스 테스트"""
        # 1. 명령 수신 확인
        received_response = client.post("/api/v1/expression/auto-express", params={
            "situation": "command_received",
            "user_id": "test_user"
        })
        assert received_response.status_code == 200
        
        # 2. 작업 중 상태
        working_response = client.post("/api/v1/expression/led", json={
            "expression": "working",
            "duration": 2000,
            "brightness": 80,
            "animation": "pulse",
            "user_id": "test_user"
        })
        assert working_response.status_code == 200
        
        # 3. 작업 완료 알림
        completed_response = client.post("/api/v1/expression/auto-express", params={
            "situation": "command_completed",
            "user_id": "test_user"
        })
        assert completed_response.status_code == 200
    
    def test_error_handling_sequence(self):
        """에러 처리 시퀀스 테스트"""
        # 1. 에러 발생 알림
        error_response = client.post("/api/v1/expression/auto-express", params={
            "situation": "command_error",
            "user_id": "test_user"
        })
        assert error_response.status_code == 200
        
        # 2. 에러 상태 표시
        error_led_response = client.post("/api/v1/expression/led", json={
            "expression": "error",
            "duration": 3000,
            "brightness": 100,
            "animation": "pulse",
            "user_id": "test_user"
        })
        assert error_led_response.status_code == 200
        
        # 3. 에러 소리 재생
        error_sound_response = client.post("/api/v1/expression/buzzer", json={
            "sound": "error",
            "frequency": 800,
            "duration": 1000,
            "volume": 90,
            "user_id": "test_user"
        })
        assert error_sound_response.status_code == 200
    
    def test_emotional_response_sequence(self):
        """감정적 반응 시퀀스 테스트"""
        emotions = ["happy", "sad", "angry", "surprised", "excited", "confused"]
        
        for emotion in emotions:
            # 감정 표현
            emotion_response = client.post("/api/v1/expression/emotion", json={
                "emotion": emotion,
                "intensity": 0.7,
                "user_id": "test_user"
            })
            assert emotion_response.status_code == 200
            
            # 감정에 따른 개별 LED 표현
            led_response = client.post("/api/v1/expression/led", json={
                "expression": EMOTION_EXPRESSIONS[emotion]["expression"],
                "duration": 2000,
                "brightness": 70,
                "animation": EMOTION_EXPRESSIONS[emotion]["animation"],
                "user_id": "test_user"
            })
            assert led_response.status_code == 200
            
            # 감정에 따른 개별 버저 소리
            if EMOTION_EXPRESSIONS[emotion]["sound"]:
                buzzer_response = client.post("/api/v1/expression/buzzer", json={
                    "sound": EMOTION_EXPRESSIONS[emotion]["sound"],
                    "frequency": 1000,
                    "duration": 500,
                    "volume": 70,
                    "user_id": "test_user"
                })
                assert buzzer_response.status_code == 200
    
    def test_custom_melody_sequence(self):
        """커스텀 멜로디 시퀀스 테스트"""
        # 간단한 멜로디 패턴들
        melodies = [
            [440, 523, 659, 784],  # A, C, E, G (Am7)
            [523, 659, 784, 880],  # C, E, G, A (C6)
            [659, 784, 880, 1047], # E, G, A, C (Em7)
        ]
        
        for i, melody in enumerate(melodies):
            response = client.post("/api/v1/expression/buzzer", json={
                "sound": "melody",
                "frequency": 1000,
                "duration": 2000,
                "volume": 80,
                "melody": melody,
                "user_id": "test_user"
            })
            assert response.status_code == 200
            data = response.json()
            assert data["melody"] == melody
    
    def test_animation_effects_sequence(self):
        """애니메이션 효과 시퀀스 테스트"""
        animations = ["blink", "fade", "rainbow", "wave", "pulse", "sparkle"]
        
        for animation in animations:
            response = client.post("/api/v1/expression/led", json={
                "expression": "happy",
                "duration": 2000,
                "brightness": 100,
                "animation": animation,
                "user_id": "test_user"
            })
            assert response.status_code == 200
            data = response.json()
            assert data["animation"] == animation


if __name__ == "__main__":
    pytest.main([__file__])
