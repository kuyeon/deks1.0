"""
채팅 NLP 모듈 테스트 스크립트
"""

import httpx
import json
import time

# API 기본 URL
BASE_URL = "http://localhost:8000/api/v1"

def test_nlp_features():
    """NLP 기능 테스트"""
    print("🧠 채팅 NLP 모듈 테스트 시작...")
    
    # NLP 기능 테스트 케이스들
    test_cases = [
        {
            "message": "안녕하세요! 오늘 기분이 정말 좋아요!",
            "expected_intent": "greeting",
            "expected_emotion": "happy",
            "expected_question": False,
            "description": "긍정적인 인사"
        },
        {
            "message": "나는 김철수입니다. 만나서 반가워요!",
            "expected_intent": "introduction",
            "expected_emotion": "excited",
            "expected_question": False,
            "description": "자기소개"
        },
        {
            "message": "덱스야, 넌 뭐하는 로봇이야?",
            "expected_intent": "question_about_robot",
            "expected_emotion": "curious",
            "expected_question": True,
            "description": "로봇에 대한 질문"
        },
        {
            "message": "어떻게 해야 로봇을 움직일 수 있어?",
            "expected_intent": "request_help",
            "expected_emotion": "helpful",
            "expected_question": True,
            "description": "도움 요청"
        },
        {
            "message": "와! 정말 멋진 로봇이네요!",
            "expected_intent": "praise",
            "expected_emotion": "excited",
            "expected_question": False,
            "description": "칭찬"
        },
        {
            "message": "안녕히 가세요. 또 만나요!",
            "expected_intent": "farewell",
            "expected_emotion": "bittersweet",
            "expected_question": False,
            "description": "작별 인사"
        },
        {
            "message": "음... 뭔가 이해가 안 돼요.",
            "expected_intent": "confused",
            "expected_emotion": "confused",
            "expected_question": False,
            "description": "혼란 표현"
        }
    ]
    
    user_id = "test_nlp_user"
    session_id = "test_nlp_session"
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        message = test_case["message"]
        expected_intent = test_case["expected_intent"]
        expected_emotion = test_case["expected_emotion"]
        expected_question = test_case["expected_question"]
        description = test_case["description"]
        
        print(f"\n📤 테스트 {i}/{total_count}: {description}")
        print(f"   메시지: '{message}'")
        
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
                
                # 기본 응답 확인
                actual_intent = data['conversation_type']
                actual_emotion = data['emotion']
                actual_response = data['response']
                
                print(f"   응답: {actual_response}")
                print(f"   의도: {actual_intent} (예상: {expected_intent})")
                print(f"   감정: {actual_emotion} (예상: {expected_emotion})")
                
                # NLP 분석 결과 확인
                if 'nlp_analysis' in data:
                    nlp_data = data['nlp_analysis']
                    print(f"   🧠 NLP 분석:")
                    print(f"      의도 신뢰도: {nlp_data.get('intent_confidence', 0):.2f}")
                    print(f"      감정 신뢰도: {nlp_data.get('emotion_confidence', 0):.2f}")
                    print(f"      감정 점수: {nlp_data.get('sentiment_score', 0):.2f}")
                    print(f"      키워드: {nlp_data.get('keywords', [])}")
                    print(f"      개체명: {nlp_data.get('entities', {})}")
                    print(f"      질문 여부: {nlp_data.get('is_question', False)} (예상: {expected_question})")
                    print(f"      질문 유형: {nlp_data.get('question_type', 'unknown')}")
                    
                    # 정확도 평가
                    intent_correct = actual_intent == expected_intent
                    emotion_correct = actual_emotion == expected_emotion
                    question_correct = nlp_data.get('is_question', False) == expected_question
                    
                    if intent_correct and emotion_correct and question_correct:
                        print(f"   ✅ 모든 분석 정확!")
                        success_count += 1
                    else:
                        print(f"   ⚠️ 일부 분석 부정확")
                        if not intent_correct:
                            print(f"      의도 불일치: {actual_intent} != {expected_intent}")
                        if not emotion_correct:
                            print(f"      감정 불일치: {actual_emotion} != {expected_emotion}")
                        if not question_correct:
                            print(f"      질문 판단 불일치: {nlp_data.get('is_question')} != {expected_question}")
                else:
                    print(f"   ❌ NLP 분석 데이터 없음")
                
            else:
                print(f"   ❌ 오류: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ 요청 실패: {e}")
        
        time.sleep(0.5)  # 0.5초 대기
    
    print(f"\n📊 NLP 테스트 결과: {success_count}/{total_count} 성공 ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 모든 NLP 테스트 통과!")
    else:
        print("⚠️ 일부 NLP 테스트 실패 - 추가 개선 필요")

def test_advanced_nlp():
    """고급 NLP 기능 테스트"""
    print("\n🔬 고급 NLP 기능 테스트 시작...")
    
    advanced_tests = [
        {
            "message": "덱스야, 너는 어떤 센서를 가지고 있어?",
            "expected_entities": ["PERSON", "ROBOT", "OBJECT"],
            "description": "개체명 인식 테스트"
        },
        {
            "message": "로봇을 앞으로 이동시켜줘",
            "expected_entities": ["ROBOT", "ACTION"],
            "description": "동작 개체명 테스트"
        },
        {
            "message": "정말 감사합니다! 덕분에 문제가 해결되었어요!",
            "expected_sentiment": 0.7,  # 높은 긍정 감정
            "description": "감정 분석 테스트"
        },
        {
            "message": "이해가 안 되고 복잡해요...",
            "expected_sentiment": -0.3,  # 부정 감정
            "description": "부정 감정 테스트"
        }
    ]
    
    user_id = "test_advanced_nlp_user"
    
    for i, test in enumerate(advanced_tests, 1):
        message = test["message"]
        description = test["description"]
        
        print(f"\n📤 고급 테스트 {i}: {description}")
        print(f"   메시지: '{message}'")
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{BASE_URL}/chat/message",
                    json={
                        "message": message,
                        "user_id": user_id,
                        "session_id": f"advanced_test_{i}"
                    }
                )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'nlp_analysis' in data:
                    nlp_data = data['nlp_analysis']
                    
                    # 개체명 확인
                    if "expected_entities" in test:
                        entities = nlp_data.get('entities', {})
                        found_entities = list(entities.keys())
                        expected_entities = test["expected_entities"]
                        
                        print(f"   개체명: {found_entities} (예상: {expected_entities})")
                        
                        entity_match = any(entity in found_entities for entity in expected_entities)
                        if entity_match:
                            print(f"   ✅ 개체명 인식 성공!")
                        else:
                            print(f"   ⚠️ 개체명 인식 부족")
                    
                    # 감정 점수 확인
                    if "expected_sentiment" in test:
                        sentiment = nlp_data.get('sentiment_score', 0)
                        expected_sentiment = test["expected_sentiment"]
                        
                        print(f"   감정 점수: {sentiment:.2f} (예상: {expected_sentiment})")
                        
                        if abs(sentiment - expected_sentiment) < 0.3:
                            print(f"   ✅ 감정 분석 정확!")
                        else:
                            print(f"   ⚠️ 감정 분석 부정확")
                    
                    print(f"   키워드: {nlp_data.get('keywords', [])}")
                    print(f"   응답: {data['response']}")
                else:
                    print(f"   ❌ NLP 분석 데이터 없음")
            else:
                print(f"   ❌ 오류: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 요청 실패: {e}")

def main():
    """메인 테스트 함수"""
    print("🚀 채팅 NLP 모듈 테스트 시작!")
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
    test_nlp_features()
    test_advanced_nlp()
    
    print("\n🎉 모든 NLP 테스트 완료!")

if __name__ == "__main__":
    main()
