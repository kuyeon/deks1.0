"""
자연어 로봇 제어 기능 테스트
"""

import sys
sys.path.append('.')

from app.api.v1.endpoints.nlp import parse_natural_language_command

def test_natural_language_commands():
    """자연어 명령 파싱 테스트"""
    
    print("=" * 60)
    print("자연어 로봇 제어 기능 테스트")
    print("=" * 60)
    
    test_commands = [
        # 속도 제어 테스트
        "앞으로 가자",
        "빨리 앞으로 가자",
        "천천히 앞으로 가자",
        "아주 빨리 앞으로 가자",
        "매우 천천히 앞으로 가자",
        
        # 거리 제어 테스트
        "조금 앞으로 가자",
        "멀리 앞으로 가자",
        "빨리 멀리 앞으로 가자",
        "천천히 조금 앞으로 가자",
        
        # 다양한 명령 테스트
        "빨리 오른쪽으로 돌아줘",
        "천천히 왼쪽으로 돌아",
        "빠르게 회전해",
        "빙글빙글 천천히 돌아",
        "뒤로 가줘",
        "빨리 뒤로 가",
        "정지",
        
        # 자연스러운 표현
        "서둘러서 앞으로 가자",
        "살살 앞으로 가줘",
        "급하게 오른쪽으로 돌아",
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n{i}. 명령: '{command}'")
        result = parse_natural_language_command(command)
        
        if result["action"]:
            action = result["action"]
            parameters = result["parameters"]
            modifiers = result.get("modifiers", {})
            response = result.get("response", "")
            
            print(f"   동작: {action}")
            print(f"   속도: {modifiers.get('speed_value', 'N/A')} ({modifiers.get('speed', 'normal')})")
            print(f"   거리: {modifiers.get('distance_value', 'N/A')} ({modifiers.get('distance', 'normal')})")
            print(f"   파라미터: {parameters}")
            print(f"   응답: {response}")
        else:
            print(f"   ❌ 명령을 인식하지 못했습니다.")
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)

def test_speed_modifiers():
    """속도 수식어 테스트"""
    print("\n\n" + "=" * 60)
    print("속도 수식어 상세 테스트")
    print("=" * 60)
    
    speed_tests = {
        "기본 속도": "앞으로 가자",
        "매우 빠름 (100)": "아주 빨리 앞으로 가자",
        "빠름 (80)": "빨리 앞으로 가자",
        "보통 (50)": "보통 속도로 앞으로 가자",
        "느림 (30)": "천천히 앞으로 가자",
        "매우 느림 (15)": "아주 천천히 앞으로 가자",
    }
    
    for name, command in speed_tests.items():
        result = parse_natural_language_command(command)
        if result["action"]:
            speed = result["modifiers"]["speed_value"]
            print(f"{name:20} -> 속도: {speed}")

def test_distance_modifiers():
    """거리 수식어 테스트"""
    print("\n\n" + "=" * 60)
    print("거리 수식어 상세 테스트")
    print("=" * 60)
    
    distance_tests = {
        "기본 거리": "앞으로 가자",
        "매우 멀리 (200)": "아주 멀리 앞으로 가자",
        "멀리 (150)": "멀리 앞으로 가자",
        "보통 (100)": "적당히 앞으로 가자",
        "짧게 (50)": "짧게 앞으로 가자",
        "매우 짧게 (30)": "아주 짧게 앞으로 가자",
    }
    
    for name, command in distance_tests.items():
        result = parse_natural_language_command(command)
        if result["action"]:
            distance = result["modifiers"]["distance_value"]
            print(f"{name:20} -> 거리: {distance}")

def test_combined_modifiers():
    """속도 + 거리 조합 테스트"""
    print("\n\n" + "=" * 60)
    print("속도 + 거리 조합 테스트")
    print("=" * 60)
    
    combined_tests = [
        "빨리 멀리 앞으로 가자",
        "천천히 조금 앞으로 가자",
        "아주 빨리 아주 멀리 앞으로 가자",
        "매우 천천히 짧게 앞으로 가자",
    ]
    
    for command in combined_tests:
        result = parse_natural_language_command(command)
        if result["action"]:
            speed = result["modifiers"]["speed_value"]
            distance = result["modifiers"]["distance_value"]
            print(f"명령: {command}")
            print(f"  -> 속도: {speed}, 거리: {distance}")
            print(f"  -> 응답: {result['response']}\n")

if __name__ == "__main__":
    test_natural_language_commands()
    test_speed_modifiers()
    test_distance_modifiers()
    test_combined_modifiers()
    
    print("\n✅ 모든 테스트 완료!")
    print("\n사용 가능한 명령 예시:")
    print("  - '앞으로 가자' (기본 속도 50)")
    print("  - '빨리 앞으로 가자' (빠른 속도 80)")
    print("  - '천천히 앞으로 가자' (느린 속도 30)")
    print("  - '아주 빨리 앞으로 가자' (최고 속도 100)")
    print("  - '매우 천천히 앞으로 가자' (최저 속도 15)")
    print("  - '빨리 멀리 앞으로 가자' (속도 80, 거리 150)")
    print("  - '천천히 조금 앞으로 가자' (속도 30, 거리 50)")

