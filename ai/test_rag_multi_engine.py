# ai/test_rag_multi_engine.py
import asyncio
from app.services.rag_service import RAGService

def test_rag_multi_retrieval():
    print("=" * 70)
    print("🏆 [RAG 완전 동적 질환 N개 & 음식 M개 검색 검증 테스트] 가동")
    print("=" * 70)
    
    rag_service = RAGService()
    
    # 🧪 [하드코어 확장 시나리오] 
    # 질환이 3개(고혈압, 당뇨, 고지혈증)인 복합 만성질환 환자가 
    # 3가지 음식(김치찌개, 현미밥, 제육볶음)을 동시에 섭취한 상황 시뮬레이션!
    mock_diseases = ["고혈압", "당뇨", "고지혈증"]
    
    mock_items = [
        {
            "food_name": "김치찌개",
            "risk_level": "위험",
            "nutrient_name": {"sodium": 950, "sugar": 4, "fat": 12, "kcal": 220, "cholesterol": 10}
        },
        {
            "food_name": "현미밥",
            "risk_level": "안전",
            "nutrient_name": {"sodium": 5, "sugar": 0.2, "fat": 1, "kcal": 150, "cholesterol": 0, "carbs": 38}
        },
        {
            "food_name": "제육볶음",
            "risk_level": "주의",
            "nutrient_name": {"sodium": 550, "sugar": 18, "fat": 24, "kcal": 380, "cholesterol": 120}
        }
    ]
    
    print(f"👤 환자 기저질환 리스트 (N={len(mock_diseases)}): {mock_diseases}")
    print(f"🍽️ 한 끼 섭취 식단 메뉴 (M={len(mock_items)}): {[item['food_name'] for item in mock_items]}")
    print("-" * 70)
    
    context_result = rag_service.retrieve_meal_evaluation_context(mock_diseases, mock_items)
    
    print("\n📥 [임베딩 DB 최종 동적 회수 통합본] :")
    print("=" * 70)
    print(context_result)
    print("=" * 70)

if __name__ == "__main__":
    test_rag_multi_retrieval()