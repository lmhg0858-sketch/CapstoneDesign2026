import os
from app.services.rag_service import RAGService

# 쌀밥 데이터를 우리가 만든 서비스 규격에 맞게 모의(Mock) 클래스로 정의합니다.
class MockFoodLog:
    def __init__(self, foodName, sugar, carbs, kcal, sodium, fat, risk_level="안전"):
        self.foodName = foodName
        self.sugar = sugar
        self.carbs = carbs
        self.kcal = kcal
        self.sodium = sodium
        self.fat = fat
        self.risk_level = risk_level

def run_perfect_rag_leak_test():
    print("=" * 80)
    print("🕵️‍♂️ [RAG 서비스 통합 검증] 진짜 서비스 로직(RAGService)을 통한 컨텍스트 회수 테스트")
    print("=" * 80)

    try:
        # 우리가 만든 서비스 레이어 본체를 가동합니다.
        rag_service = RAGService()
    except Exception as e:
        print(f"❌ RAG 인프라 로드 실패: {e}")
        return

    # 1. 👤 테스트할 유저 기저질환 세팅 (백엔드 규격인 "당뇨"로 찌릅니다!)
    user_diseases = ["당뇨", "고지혈증"]
    
    # 2. 🍽️ 터미널 로그에 찍혔던 유저의 음식 로그를 서비스 데이터 규격으로 조립합니다.
    # 흰쌀밥은 당류(sugar)와 탄수화물(carbs), 칼로리(kcal) 지표가 있는 상태로 가정합니다.
    food_log = [
        MockFoodLog(
            foodName="흰쌀밥", 
            sugar=2.0, 
            carbs=65.0, 
            kcal=300.0, 
            sodium=5.0, 
            fat=0.5, 
            risk_level="주의" # '주의' 등급 판정을 받았다고 시뮬레이션
        )
    ]
    
    # 단일 식사용 딕셔너리 규격도 함께 준비 (두 함수 모두 검증하기 위함)
    final_items = [
        {
            "food_name": "흰쌀밥",
            "nutrient_name": {
                "sugar": 2.0, "carbs": 65.0, "kcal": 300.0, "sodium": 5.0, "fat": 0.5
            }
        }
    ]

    print(f"👤 유저 입력 질환: {user_diseases}")
    print(f"🍽️ 입력된 푸드 로그: 흰쌀밥 (주의 등급)")
    print("-" * 60)

    # 🚀 [테스트 A] 단일 사진 분석용 RAG 엔진 작동
    print("\n[A] 단일 식사 분석 RAG (retrieve_meal_evaluation_context) 가동...")
    try:
        meal_context = rag_service.retrieve_meal_evaluation_context(user_diseases, final_items)
        print("\n📊 [A] 엔진 최종 출력 결과:")
        print(meal_context if meal_context else "⚠️ 회수된 컨텍스트가 없습니다.")
    except Exception as e:
        print(f"❌ 단일 식사 RAG 실행 에러: {e}")

    print("-" * 60)

    # 🚀 [테스트 B] 홈 화면 누적 리포트용 RAG 엔진 작동
    print("\n[B] 누적 식단 리포트 RAG (retrieve_daily_accumulation_context) 가동...")
    try:
        daily_context = rag_service.retrieve_daily_accumulation_context(user_diseases, food_log)
        print("\n📊 [B] 엔진 최종 출력 결과:")
        print(daily_context if daily_context else "⚠️ 회수된 컨텍스트가 없습니다.")
    except Exception as e:
        print(f"❌ 누적 식단 RAG 실행 에러: {e}")

    print("\n" + "=" * 80)
    print("🏁 RAG 서비스 레이어 실제 기능 검증 완료.")
    print("=" * 80)

if __name__ == "__main__":
    run_perfect_rag_leak_test()