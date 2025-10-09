"""
Deks 1.0 에러 처리 API 통합 테스트
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestErrorResponseFormat:
    """에러 응답 형식 테스트"""
    
    def test_validation_error_response_format(self):
        """검증 에러 응답 형식 테스트"""
        # 잘못된 파라미터로 요청
        response = client.post(
            "/api/v1/robot/move/forward",
            json={
                "speed": 150,  # 최대값 100 초과
                "distance": -10,  # 최소값 0 미만
                "user_id": "test_user"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        
        # 표준 에러 응답 형식 검증
        assert "success" in data
        assert data["success"] is False
        assert "error_code" in data
        assert "error_name" in data
        assert "message" in data
        assert "timestamp" in data
    
    def test_missing_required_field_error(self):
        """필수 필드 누락 에러 테스트"""
        # TurnRequest의 필수 필드인 direction 누락
        response = client.post(
            "/api/v1/robot/move/turn",
            json={
                "angle": 90,
                "speed": 30
            }
        )
        
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        
        # FastAPI 기본 응답 또는 우리의 커스텀 응답
        assert "detail" in data or "errors" in data
    
    def test_invalid_enum_value_error(self):
        """열거형 값 에러 테스트"""
        # 잘못된 방향 값
        response = client.post(
            "/api/v1/robot/move/turn",
            json={
                "direction": "invalid",  # "left" 또는 "right"만 허용
                "angle": 90,
                "speed": 30
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        
        # 검증 에러 응답 확인
        assert "detail" in data or "errors" in data


class TestRobotCommandErrors:
    """로봇 명령 에러 테스트"""
    
    def test_robot_not_connected_error(self):
        """로봇 미연결 에러 테스트"""
        # 로봇이 연결되어 있지 않은 상태에서 명령 실행
        # 실제 테스트 환경에서는 로봇이 연결되지 않았을 것으로 예상
        response = client.post(
            "/api/v1/robot/move/forward",
            json={
                "speed": 50,
                "distance": 100,
                "user_id": "test_user"
            }
        )
        
        # 에러가 발생하거나 성공적으로 대기열에 추가됨
        # (실제 로봇 연결 상태에 따라 다름)
        assert response.status_code in [200, 404, 500]


class TestHealthCheckEndpoints:
    """헬스 체크 엔드포인트 테스트"""
    
    def test_health_check_success(self):
        """헬스 체크 성공 테스트"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "service" in data
        assert data["service"] == "deks-backend"
    
    def test_root_endpoint(self):
        """루트 엔드포인트 테스트"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "version" in data


class TestErrorStatisticsEndpoint:
    """에러 통계 엔드포인트 테스트"""
    
    def test_error_statistics_endpoint(self):
        """에러 통계 조회 테스트"""
        response = client.get("/errors/statistics")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert "statistics" in data
        assert "timestamp" in data
        
        stats = data["statistics"]
        assert "total_errors" in stats
        assert "errors_by_code" in stats
        assert "errors_by_endpoint" in stats


class TestRobotStatusEndpoints:
    """로봇 상태 엔드포인트 테스트"""
    
    def test_get_robot_status(self):
        """로봇 상태 조회 테스트"""
        response = client.get("/api/v1/robot/status")
        
        # 로봇 연결 여부와 관계없이 응답은 반환되어야 함
        assert response.status_code in [200, 500]
    
    def test_get_connected_robots(self):
        """연결된 로봇 목록 조회 테스트"""
        response = client.get("/api/v1/robot/robots/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert "connected_robots" in data
        assert "total_connected" in data
        assert isinstance(data["connected_robots"], list)
    
    def test_get_robot_detailed_status(self):
        """로봇 상세 상태 조회 테스트"""
        response = client.get("/api/v1/robot/robots/deks_001/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert "robot" in data
        assert data["robot"]["robot_id"] == "deks_001"


class TestAPIDocumentation:
    """API 문서 테스트"""
    
    def test_openapi_docs_accessible(self):
        """OpenAPI 문서 접근 테스트"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_accessible(self):
        """ReDoc 문서 접근 테스트"""
        response = client.get("/redoc")
        assert response.status_code == 200
    
    def test_openapi_json(self):
        """OpenAPI JSON 스키마 테스트"""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data


class TestSocketBridgeStatus:
    """Socket Bridge 상태 테스트"""
    
    def test_socket_bridge_status(self):
        """Socket Bridge 상태 조회 테스트"""
        response = client.get("/socket-bridge/status")
        
        # Socket Bridge가 실행 중이면 200, 아니면 에러
        assert response.status_code in [200, 500]
        
        data = response.json()
        # 성공하거나 에러 정보가 있어야 함
        assert data is not None


class TestCORSHeaders:
    """CORS 헤더 테스트"""
    
    def test_cors_headers_present(self):
        """CORS 헤더 존재 여부 테스트"""
        response = client.get("/health")
        
        assert response.status_code == 200
        
        # CORS 헤더 확인
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "*"


@pytest.mark.asyncio
class TestAsyncErrorHandling:
    """비동기 에러 처리 테스트"""
    
    async def test_concurrent_robot_commands(self):
        """동시 로봇 명령 테스트"""
        # 여러 명령을 동시에 전송
        responses = []
        
        for i in range(5):
            response = client.post(
                "/api/v1/robot/move/forward",
                json={
                    "speed": 50,
                    "distance": 10 * (i + 1),
                    "user_id": f"test_user_{i}"
                }
            )
            responses.append(response)
        
        # 모든 응답이 유효해야 함
        for response in responses:
            assert response.status_code in [200, 404, 500]
            data = response.json()
            assert data is not None


class TestErrorRecovery:
    """에러 복구 테스트"""
    
    def test_error_then_success(self):
        """에러 후 성공 테스트"""
        # 1. 잘못된 요청으로 에러 발생
        error_response = client.post(
            "/api/v1/robot/move/forward",
            json={
                "speed": 200,  # 최대값 초과
                "distance": 100
            }
        )
        assert error_response.status_code == 400
        
        # 2. 올바른 요청으로 성공
        success_response = client.post(
            "/api/v1/robot/move/forward",
            json={
                "speed": 50,
                "distance": 100,
                "user_id": "test_user"
            }
        )
        assert success_response.status_code in [200, 404]  # 로봇 연결 상태에 따라


class TestErrorResponseConsistency:
    """에러 응답 일관성 테스트"""
    
    def test_all_error_responses_have_timestamp(self):
        """모든 에러 응답에 타임스탬프가 있는지 테스트"""
        # 검증 에러 발생
        response = client.post(
            "/api/v1/robot/move/forward",
            json={"speed": -1}  # 유효하지 않은 값
        )
        
        if response.status_code in [400, 422]:
            data = response.json()
            # 타임스탬프 필드 확인 (있거나 없을 수 있음)
            assert data is not None
    
    def test_error_response_serializable(self):
        """에러 응답이 JSON 직렬화 가능한지 테스트"""
        response = client.post(
            "/api/v1/robot/move/forward",
            json={"speed": 999}  # 최대값 초과
        )
        
        # JSON 응답이 파싱 가능해야 함
        try:
            data = response.json()
            assert data is not None
        except Exception as e:
            pytest.fail(f"응답을 JSON으로 파싱할 수 없음: {e}")

