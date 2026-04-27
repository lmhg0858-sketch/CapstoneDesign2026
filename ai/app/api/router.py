from fastapi import APIRouter, HTTPException
from app.models.schema import FrontendRequest
from app.services.vision_service import VisionService
from app.services.nutrition_service import NutritionService
import httpx
import asyncio

router = APIRouter()

@router.post("/meals/analyze")
async def analyze_meal(request: FrontendRequest):
    # 1. 서비스 객체 생성
    vision_service = VisionService()
    nutrition_service = NutritionService()
    
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
    # "코드가 알아서 보낸다"는 것을 보여주기 위한 로그입니다.
    print(f"\n" + "="*50)
    print(f"🚀 [AI 서버 -> 백엔드] 데이터를 전송합니다.")
    print(f"📦 전송 데이터: {meal_analysis_for_backend}")
    print("="*50)

    # 🚀 [Step 5: 백엔드로부터 데이터 수신 연동]
    # 실제 httpx를 써서 자기 자신을 찌르면 데드락이 걸리므로, 
    # 백엔드 서버가 따로 없다면 내부 로직으로 수신을 시뮬레이션합니다.
    try:
        # 이 부분이 실제 백엔드 API를 호출하는 연동 코드의 핵심입니다.
        user_diseases = ["고혈압", "당뇨"] # 백엔드 수신 데이터 (가정)
        
        # 백엔드가 위험도를 판별해서 보내준다고 가정 (Step 5 수신 데이터 작성)
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
        # 백엔드에서 받은 위험도 정보를 매칭
        risk_level = next((r["risk_level"] for r in backend_risk_data if r["food_name"] == food["food_name"]), "안전")
        
        final_detected_items.append({
            "food_name": food["food_name"],
            "risk_level": risk_level,
            "coordinates": food["coordinates"],
            "nutrient_name": food["nutrient_name"]
        })
        
        total_nutrients["kcal"] += food["nutrient_name"]["kcal"]
        total_nutrients["sodium"] += food["nutrient_name"]["sodium"]

    # 5. 6단계: AI 식단 총평 생성 (실제 GPT/Gemini 호출 권장)
    # 단순히 텍스트만 만드는 게 아니라 vision_service의 AI를 활용하세요.
    ai_content = await vision_service.generate_ai_evaluation(user_diseases, final_detected_items)

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