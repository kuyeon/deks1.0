"""
채팅 API 테스트 스크립트
"""

import httpx
import json
import time

# API 기본 URL
BASE_URL = "http://localhost:8000/api/v1"

def test_chat_message():
    """채팅 메시지 전송 테스트"""
    print("🧪 채팅 메시지 전송 테스트 시작...")
    
    # 테스트 메시지들
    test_messages = [
        "안녕 덱스",
        "나는 김철수야",
        "넌 뭐야?",
        "안녕히 가"
    ]
    
    user_id = "test_user_001"
    session_id = "test_session_001"
    
    for message in test_messages:
        print(f"\n📤 메시지 전송: '{message}'")
        
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
                print(f"✅ 응답: {data['response']}")
                print(f"   감정: {data['emotion']}")
                print(f"   대화 유형: {data['conversation_type']}")
                if data.get('context'):
                    print(f"   컨텍스트: {data['context']}")
            else:
                print(f"❌ 오류: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ 요청 실패: {e}")
        
        time.sleep(1)  # 1초 대기

def test_chat_history():
    """채팅 기록 조회 테스트"""
    print("\n🧪 채팅 기록 조회 테스트 시작...")
    
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{BASE_URL}/chat/history",
                params={
                    "user_id": "test_user_001",
                    "limit": 10,
                    "offset": 0
                }
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 총 대화 수: {data['total_count']}")
            print(f"   조회된 대화: {len(data['conversations'])}개")
            
            for i, conv in enumerate(data['conversations'][:3]):  # 처음 3개만 출력
                print(f"   {i+1}. 사용자: {conv['user_message']}")
                print(f"      로봇: {conv['robot_response']}")
                print(f"      감정: {conv['emotion_responded']}")
        else:
            print(f"❌ 오류: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {e}")

def test_chat_context():
    """채팅 컨텍스트 조회 테스트"""
    print("\n🧪 채팅 컨텍스트 조회 테스트 시작...")
    
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{BASE_URL}/chat/context",
                params={
                    "user_id": "test_user_001",
                    "session_id": "test_session_001"
                }
            )
        
        if response.status_code == 200:
            data = response.json()
            context = data['context']
            print(f"✅ 사용자: {context.get('user_name', 'Unknown')}")
            print(f"   대화 수: {context.get('conversation_count', 0)}")
            print(f"   로봇 기분: {context.get('robot_mood', 'Unknown')}")
            print(f"   현재 주제: {context.get('current_topic', 'Unknown')}")
        else:
            print(f"❌ 오류: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {e}")

def test_emotion_update():
    """감정 상태 업데이트 테스트"""
    print("\n🧪 감정 상태 업데이트 테스트 시작...")
    
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/chat/emotion",
                json={
                    "emotion": "happy",
                    "user_id": "test_user_001",
                    "reason": "테스트용 감정 업데이트"
                }
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 감정 업데이트: {data['emotion_updated']}")
            print(f"   LED 표정: {data['led_expression']}")
            print(f"   버저 소리: {data['buzzer_sound']}")
        else:
            print(f"❌ 오류: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {e}")

def test_conversation_patterns():
    """대화 패턴 조회 테스트"""
    print("\n🧪 대화 패턴 조회 테스트 시작...")
    
    try:
        with httpx.Client() as client:
            response = client.get(f"{BASE_URL}/chat/patterns")
        
        if response.status_code == 200:
            data = response.json()
            patterns = data['patterns']
            print(f"✅ 지원하는 대화 패턴: {len(patterns)}개")
            
            for pattern_name in list(patterns.keys())[:3]:  # 처음 3개만 출력
                pattern = patterns[pattern_name]
                print(f"   - {pattern_name}: {len(pattern['keywords'])}개 키워드")
        else:
            print(f"❌ 오류: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {e}")

def test_emotion_states():
    """감정 상태 조회 테스트"""
    print("\n🧪 감정 상태 조회 테스트 시작...")
    
    try:
        with httpx.Client() as client:
            response = client.get(f"{BASE_URL}/chat/emotions")
        
        if response.status_code == 200:
            data = response.json()
            emotions = data['emotions']
            print(f"✅ 지원하는 감정 상태: {len(emotions)}개")
            
            for emotion_name in emotions.keys():
                emotion = emotions[emotion_name]
                print(f"   - {emotion_name}: LED={emotion['led_expression']}, 버저={emotion['buzzer_sound']}")
        else:
            print(f"❌ 오류: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {e}")

def main():
    """메인 테스트 함수"""
    print("🚀 채팅 API 테스트 시작!")
    print("=" * 50)
    
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
    test_chat_message()
    test_chat_history()
    test_chat_context()
    test_emotion_update()
    test_conversation_patterns()
    test_emotion_states()
    
    print("\n🎉 모든 테스트 완료!")

if __name__ == "__main__":
    main()
