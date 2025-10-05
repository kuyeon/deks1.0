"""
개선된 채팅 패턴 테스트 스크립트
"""

import httpx
import json
import time

# API 기본 URL
BASE_URL = "http://localhost:8000/api/v1"

def test_improved_patterns():
    """개선된 채팅 패턴 테스트"""
    print("🧪 개선된 채팅 패턴 테스트 시작...")
    
    # 개선된 테스트 케이스들
    test_cases = [
        # 이름 추출 테스트
        {
            "message": "나는 김철수야",
            "expected_intent": "introduction",
            "expected_name": "김철수"
        },
        {
            "message": "내 이름은 이영희입니다",
            "expected_intent": "introduction", 
            "expected_name": "이영희"
        },
        {
            "message": "저는 박민수",
            "expected_intent": "introduction",
            "expected_name": "박민수"
        },
        
        # 작별 인사 테스트
        {
            "message": "안녕히 가",
            "expected_intent": "farewell"
        },
        {
            "message": "잘 가",
            "expected_intent": "farewell"
        },
        {
            "message": "또 봐",
            "expected_intent": "farewell"
        },
        
        # 도움 요청 테스트
        {
            "message": "도와줘",
            "expected_intent": "request_help"
        },
        {
            "message": "어떻게 해야 해?",
            "expected_intent": "request_help"
        },
        
        # 칭찬 테스트
        {
            "message": "잘했어!",
            "expected_intent": "praise"
        },
        {
            "message": "훌륭해",
            "expected_intent": "praise"
        },
        
        # 혼란 테스트
        {
            "message": "모르겠어",
            "expected_intent": "confused"
        }
    ]
    
    user_id = "test_improved_user"
    session_id = "test_improved_session"
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        message = test_case["message"]
        expected_intent = test_case["expected_intent"]
        expected_name = test_case.get("expected_name")
        
        print(f"\n📤 테스트 {i}/{total_count}: '{message}'")
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{BASE_URL}/chat/message",
                    json={
                        "message": message,
                        "user_id": user_id,
                        "session_id": session_id
                    }
                )
            
            if response.status_code == 200:
                data = response.json()
                actual_intent = data['conversation_type']
                actual_response = data['response']
                
                # 의도 확인
                if actual_intent == expected_intent:
                    print(f"✅ 의도 매칭: {actual_intent}")
                    success_count += 1
                else:
                    print(f"❌ 의도 불일치: 예상={expected_intent}, 실제={actual_intent}")
                
                # 이름 추출 확인
                if expected_name:
                    if expected_name in actual_response:
                        print(f"✅ 이름 추출 성공: {expected_name}")
                    else:
                        print(f"❌ 이름 추출 실패: {expected_name}이 응답에 없음")
                
                print(f"   응답: {actual_response}")
                print(f"   감정: {data['emotion']}")
                
            else:
                print(f"❌ 오류: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ 요청 실패: {e}")
        
        time.sleep(0.5)  # 0.5초 대기
    
    print(f"\n📊 테스트 결과: {success_count}/{total_count} 성공 ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 모든 테스트 통과!")
    else:
        print("⚠️ 일부 테스트 실패 - 추가 개선 필요")

def test_edge_cases():
    """엣지 케이스 테스트"""
    print("\n🧪 엣지 케이스 테스트 시작...")
    
    edge_cases = [
        "안녕",  # 짧은 인사
        "덱스야",  # 로봇 이름 호출
        "뭐야?",  # 짧은 질문
        "ㅋㅋㅋ",  # 웃음
        "아무거나",  # 모호한 표현
        "고마워",  # 감사 표현
    ]
    
    user_id = "test_edge_user"
    
    for message in edge_cases:
        print(f"\n📤 엣지 케이스: '{message}'")
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{BASE_URL}/chat/message",
                    json={
                        "message": message,
                        "user_id": user_id,
                        "session_id": "edge_test_session"
                    }
                )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 응답: {data['response']}")
                print(f"   의도: {data['conversation_type']}")
                print(f"   감정: {data['emotion']}")
            else:
                print(f"❌ 오류: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 요청 실패: {e}")

def main():
    """메인 테스트 함수"""
    print("🚀 개선된 채팅 패턴 테스트 시작!")
    print("=" * 60)
    
    # 서버 연결 확인
    try:
        with httpx.Client() as client:
            response = client.get(f"{BASE_URL.replace('/api/v1', '')}/docs")
            if response.status_code != 200:
                print("❌ 서버가 실행되지 않았습니다. 서버를 먼저 시작해주세요.")
                return
    except:
        print("❌ 서버에 연결할 수 없습니다. 서버를 먼저 시작해주세요.")
        return
    
    # 각 테스트 실행
    test_improved_patterns()
    test_edge_cases()
    
    print("\n🎉 모든 테스트 완료!")

if __name__ == "__main__":
    main()
