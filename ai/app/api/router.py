from fastapi import APIRouter, HTTPException, status # 🎯 status 추가
from app.models.schema import FrontendRequest, BackendMealLogRequest # 🎯 BackendMealLogRequest 추가
from app.services.vision_service import VisionService
from app.services.nutrition_service import NutritionService
from app.services.analysis_service import AnalysisService # 🎯 AnalysisService 임포트 추가
import httpx
import asyncio

router = APIRouter()

# 🎯 라우터 수준에서 영양소 서비스 객체를 싱글톤처럼 미리 띄워놓으면 
# 매번 API가 호출될 때마다 무거운 CSV 파일을 다시 읽지 않아 훨씬 빠르고 효율적입니다.
nutrition_service = NutritionService()

@router.post("/meals/analyze")
async def analyze_meal(request: FrontendRequest):
    # 1. 서비스 객체 생성 (기존 로컬 변수는 글로벌 인스턴스를 바라보게 유지)
    vision_service = VisionService()
    
    # 2. 1단계: 이미지 분석 (좌표 + 음식명 추출)
    detected_items = await vision_service.analyze_food_image(
        request.image_base64, 
        food_list=nutrition_service.food_list
    )
    
    if isinstance(detected_items, dict) and "error" in detected_items:
        raise HTTPException(status_code=400, detail=detected_items["error"])

    # 3. 2단계 & 3단계: 영양 정보 결합 (DB 추출)
    meal_analysis_for_backend = []
    for item in detected_items:
        raw_name = item.get('food_name_en', '알 수 없는 음식')
        nutrition_data = nutrition_service.get_nutrition_data(raw_name)
        
        if nutrition_data:
            food_info = {
                "food_name": nutrition_data["food_name"],
                "nutrient_name": nutrition_data["nutrient_name"],
                "coordinates": item['coordinates']
            }
            meal_analysis_for_backend.append(food_info)

    # 🚀 [Step 4: 백엔드로 데이터 자동 송신 로그]
    print(f"\n" + "="*50)
    print(f"🚀 [AI 서버 -> 백엔드] 데이터를 전송합니다.")
    print(f"📦 전송 데이터: {meal_analysis_for_backend}")
    print("="*50)

    # 🚀 [Step 5: 백엔드로부터 데이터 수신 연동 시뮬레이션]
    try:
        user_diseases = ["고혈압", "당뇨"] 
        backend_risk_data = []
        for food in meal_analysis_for_backend:
            sodium = food["nutrient_name"].get("sodium", 0)
            risk = "위험" if sodium > 800 else "안전"
            backend_risk_data.append({
                "food_name": food["food_name"],
                "risk_level": risk
            })
        
        print(f"📡 [백엔드 -> AI 서버] 데이터를 수신했습니다.")
        print(f"🏥 사용자 질병: {user_diseases}")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"❌ 연동 실패: {e}")
        user_diseases = ["정보 없음"]
        backend_risk_data = []

    # 4. 결과 재구성 (위험도 반영)
    final_detected_items = []
    total_nutrients = {"kcal": 0, "sodium": 0}

    for food in meal_analysis_for_backend:
        risk_level = next((r["risk_level"] for r in backend_risk_data if r["food_name"] == food["food_name"]), "안전")
        
        final_detected_items.append({
            "food_name": food["food_name"],
            "risk_level": risk_level,
            "coordinates": food["coordinates"],
            "nutrient_name": food["nutrient_name"]
        })
        
        total_nutrients["kcal"] += food["nutrient_name"]["kcal"]
        total_nutrients["sodium"] += food["nutrient_name"]["sodium"]

    # 5. 6단계: AI 식단 총평 생성 
    # 분석 서비스에 내장된 기존 단일 분석 호출 함수를 연동합니다.
    analysis_service = AnalysisService()
    ai_content = await analysis_service.generate_ai_evaluation(user_diseases, final_detected_items)

    # 6. 7단계: 최종 결과 반환
    return {
        "status": "success",
        "data": {
            "detected_items": final_detected_items,
            "ai_evaluation": {
                "content": ai_content.strip()
            }
        }
    }


# # --------------------------------------------------------------------
# # 📊 [수정 반영 파트] 홈화면 누적 식단 분석 및 우리 DB 맞춤형 음식 추천
# # --------------------------------------------------------------------
# @router.get("/api/meals/recom")
# async def get_daily_diet_recommendation_and_summary(userId: str):
#     """
#     프론트엔드 요청 수신 ➔ 백엔드(8080) 데이터 조회 ➔ 실패 시 즉시 에러 발생!
#     """
#     print(f"\n🏠 [홈화면 자동 분석] 프론트엔드로부터 유저 '{userId}' 요청 수신")
#     analysis_service = AnalysisService()
    
#     backend_fetch_url = f"http://localhost:8080/api/meals/logs?userId={userId}"
    
#     try:
#         async with httpx.AsyncClient() as client:
#             print(f"📡 [AI ➔ 백엔드] 모든 식사 로그 조회 요청 전송: {backend_fetch_url}")
#             response = await client.get(backend_fetch_url, timeout=4.0)
            
#             if response.status_code != 200:
#                 raise HTTPException(
#                     status_code=response.status_code, 
#                     detail=f"백엔드 서버에서 에러를 반환했습니다: {response.text}"
#                 )
                
#             validated_data = BackendMealLogRequest(**response.json())
#             print(f"✅ [백엔드 수신 완료] 로그 데이터 파싱 성공")
            
#     except httpx.RequestError as exc:
#         print(f"❌ [연동 에러] 백엔드 서버(8080)가 응답하지 않습니다.")
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail=f"백엔드 메인 서버가 오프라인 상태입니다. 통신 실패 원인: {exc}"
#         )

#     # 🎯 [핵심 변경 사항]: 3가지 음식을 우리 DB 명칭으로 검증하기 위해 nutrition_service 객체를 함께 주입합니다.
#     final_result = await analysis_service.generate_daily_summary_and_recommendation(
#         log_data=validated_data, 
#         nutrition_service=nutrition_service
#     )
    
#     print("🏁 [분석 완료] 프론트엔드로 최종 3가지 추천 한식 JSON 데이터를 전송합니다.")
#     return final_result





# --------------------------------------------------------------------
# 📊 [임시 단독 테스트 버전] 홈화면 누적 식단 분석 및 3가지 음식 추천
# --------------------------------------------------------------------
@router.get("/api/meals/recom")
async def get_daily_diet_recommendation_and_summary(userId: str):
    """
    [테스트용] 백엔드 조회를 패스하고 가상 로그 데이터를 사용해 RAG+GPT를 돌립니다.
    """
    print(f"\n🏠 [테스트 모드 가동] 백엔드 통신을 패스하고 가상 데이터로 테스트를 진행합니다.")
    analysis_service = AnalysisService()
    
    # 🎯 질문자님이 주신 규격 데이터를 그대로 테스트용 박스로 선언
    mock_data = {
        "user_diseases" : ["당뇨", "고지혈증"],
        "daily_risk": {"date": "2026-05-27", "status": "주의", "total_count": 4, "danger_count": 1, "caution_count": 3, "safe_count": 0},
        "food_log": [
            {"id": 8, "userId": userId, "foodName": "바나나우유", "eatTime": "2026-05-27T17:09:50", "kcal": 210, "carbs": 35, "protein": 6, "fat": 5, "sugar": 30, "sodium": 120, "cholesterol": 20, "kalium": 250, "phos": 150, "risk_level": "주의"},
            {"id": 7, "userId": userId, "foodName": "떡볶이", "eatTime": "2026-05-27T17:09:50", "kcal": 520, "carbs": 95, "protein": 10, "fat": 8, "sugar": 28, "sodium": 900, "cholesterol": 15, "kalium": 350, "phos": 180, "risk_level": "위험"},
            {"id": 4, "userId": userId, "foodName": "삶은 계란", "eatTime": "2026-05-27T16:57:56", "kcal": 80, "carbs": 1, "protein": 7, "fat": 5, "sugar": 0, "sodium": 60, "cholesterol": 180, "kalium": 70, "phos": 90, "risk_level": "주의"},
            {"id": 3, "userId": userId, "foodName": "김치찌개", "eatTime": "2026-05-27T16:57:56", "kcal": 350, "carbs": 20, "protein": 18, "fat": 22, "sugar": 5, "sodium": 1200, "cholesterol": 40, "kalium": 500, "phos": 200, "risk_level": "주의"}
        ]
    }
    
    # 팩토리 객체화
    validated_data = BackendMealLogRequest(**mock_data)

    # 3가지 음식 우리 DB 명칭 매핑 알고리즘 태우기
    final_result = await analysis_service.generate_daily_summary_and_recommendation(
        log_data=validated_data, 
        nutrition_service=nutrition_service
    )
    
    print("🏁 [테스트 분석 완료] 가공된 최종 3가지 추천 한식 JSON 데이터를 반환합니다.")
    return final_result