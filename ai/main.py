import os
import httpx 
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 서비스 임포트
from app.services.vision_service import VisionService
from app.services.nutrition_service import NutritionService
from app.services.analysis_service import AnalysisService # 추가된 서비스

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "storage/dangdang-494520-79c62a66d935.json"

app = FastAPI(title="DangDang AI Server - Real Integration")

# 서비스 객체 초기화
nutrition_service = NutritionService()
vision_service = VisionService()
analysis_service = AnalysisService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# [핵심 엔드포인트]
@app.post("/api/meals/analyze")
async def analyze_food(data: dict):
    print("\n🚀 [1단계] 이미지 분석 요청 수신")
    base64_image = data.get("image_base64") or data.get("image")
    
    if not base64_image:
        raise HTTPException(status_code=400, detail="이미지 데이터가 없습니다.")
    
    # 1. AI 이미지 분석 (음식명 & 좌표)
    detected_items = await vision_service.analyze_food_image(base64_image, food_list=nutrition_service.food_list)

    # 2. 백엔드 송신용 규격 구성 (좌표 제외)
    meal_data_to_send = []
    for item in detected_items:
        raw_name = item.get('food_name_en', '알 수 없는 음식')
        nutrition = nutrition_service.get_nutrition_data(raw_name)
        if nutrition:
            meal_data_to_send.append({
                "food_name": nutrition["food_name"],
                "nutrient_name": nutrition["nutrient_name"]
            })

    # 🚀 [Step 4 & 5: 외부 연동]
    print(f"📡 [AI 서버] 백엔드 주소로 HTTP POST 요청을 보냅니다...")
    user_diseases = []
    risk_results = []

    try:
        async with httpx.AsyncClient() as client:
            backend_url = "http://127.0.0.1:8080/api/meals/analyze?userId=myid123"
            response = await client.post(
                backend_url, 
                json={"detectedFoods": meal_data_to_send},
                timeout=5.0
            )
            if response.status_code == 200:
                res_data = response.json()
                user_diseases = res_data.get("user_diseases", [])
                risk_results = res_data.get("analysis_results", [])
                print(f"✅ [AI 서버] 백엔드로부터 데이터 수신 성공: {user_diseases}")
            else:
                raise Exception(f"Backend Error: {response.status_code}")
    except Exception as e:
        print(f"⚠️ [연동 실패] 외부 백엔드와 통신할 수 없음: {e}")
        user_diseases, risk_results = ["고혈압"], []

    # 3. 데이터 최종 결합 (수신한 위험도 + 기존 좌표)
    final_detected_items = []
    for i, food_info in enumerate(meal_data_to_send):
        risk_level = next((r["risk_level"] for r in risk_results if r["food_name"] == food_info["food_name"]), "안전")
        final_detected_items.append({
            "food_name": food_info["food_name"],
            "risk_level": risk_level,
            "coordinates": detected_items[i]['coordinates'], # 좌표 유지
            "nutrient_name": food_info["nutrient_name"]
        })

    # 🚀 [Step 6: AI 총평 생성] 
    # VisionService가 아닌 AnalysisService를 사용하도록 수정되었습니다.
    print("🤖 [6단계] 전용 분석 서비스를 통해 AI 식단 총평 생성 중...")
    ai_evaluation = await analysis_service.generate_ai_evaluation(user_diseases, final_detected_items)
    
    # 🏁 [7단계] 최종 반환
    print("🏁 [7단계] 모든 분석 완료! 프론트엔드로 반환합니다.")
    return {
        "status": "success",
        "data": {
            "detected_items": final_detected_items,
            "ai_evaluation": { "content": ai_evaluation }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)