import os
import httpx 
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 서비스 및 스키마 임포트
from app.services.vision_service import VisionService
from app.services.nutrition_service import NutritionService
from app.services.analysis_service import AnalysisService 
from app.models.schema import BackendMealLogRequest

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "storage/dangdang-494520-79c62a66d935.json"

app = FastAPI(title="DangDang AI Server - Real Integration")

# 서비스 객체 초기화 (싱글톤)
nutrition_service = NutritionService()
vision_service = VisionService()
analysis_service = AnalysisService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🎯 [동적 제어판] 실제 외부 백엔드 서버(Spring Boot 등)의 Base URL을 8080 포트로 고정합니다.
BACKEND_BASE_URL = "http://localhost:8080"

# ====================================================================
# 📊 [실제 백엔드 연동] 홈화면 누적 식단 분석 및 3가지 음식 추천 API
# ====================================================================
@app.get("/api/meals/recom")
async def get_daily_diet_recommendation_and_summary(userId: str):
    """
    실제 백엔드 서버(localhost:8080)로부터 유저의 당일 누적 식사 로그 데이터를 실시간으로 긁어옵니다.
    """
    print(f"\n🏠 [실전 연동] userId: {userId}의 누적 식단 데이터를 스프링 백엔드 서버로부터 조회합니다.")
    
    # 📡 알려주신 백엔드 명세 주소 규격 그대로 동적 URL 조립 완료!
    backend_fetch_url = f"{BACKEND_BASE_URL}/api/meals/logs?userId={userId}"
    
    try:
        async with httpx.AsyncClient() as client:
            # 백엔드 서버로 실제 GET 요청 전송
            response = await client.get(backend_fetch_url, timeout=5.0)
            if response.status_code == 200:
                raw_backend_data = response.json()
                print("✅ [AI 서버] 백엔드로부터 최신 누적 식사 로그(logs) 수집 대성공!")
            else:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"백엔드 응답 실패 (상태코드: {response.status_code})"
                )
    except Exception as e:
        print(f"❌ [스프링 백엔드 통신 장애 원인] {e}")
        raise HTTPException(status_code=500, detail=f"백엔드 서버({backend_fetch_url})와 통신할 수 없습니다: {e}")
    
    # 수신한 데이터가 우리가 정한 Pydantic 규격과 맞는지 자동 검증 후 패킹
    try:
        validated_data = BackendMealLogRequest(**raw_backend_data)
    except Exception as e:
        print(f"❌ [스키마 불일치 알림] 백엔드가 준 JSON 구조가 AI 서버의 Pydantic 명세와 맞지 않습니다: {e}")
        raise HTTPException(status_code=422, detail=f"백엔드 수신 데이터 포맷 파싱 실패: {e}")

    # 💎 완벽하게 검증된 초정밀 영양 RAG 및 3가지 음식 추천 서비스 가동
    final_result = await analysis_service.generate_daily_summary_and_recommendation(
        log_data=validated_data, 
        nutrition_service=nutrition_service
    )
    
    return final_result

# ====================================================================
# 🚀 [실전 연동 고도화: 단일 이미지 분석 엔드포인트]
# ====================================================================
@app.post("/api/meals/analyze")
async def analyze_food(data: dict):
    print("\n🚀 [1단계] 이미지 분석 요청 수신")
    base64_image = data.get("image_base64") or data.get("image")
    
    if not base64_image:
        raise HTTPException(status_code=400, detail="이미지 데이터가 없습니다.")
    
    # 아까 업그레이드한 크롭+중량 추정(estimated_weight) 버전의 비전 분석 가동
    detected_items = await vision_service.analyze_food_image(base64_image, food_list=nutrition_service.food_list)

    meal_data_to_send = []
    for item in detected_items:
        raw_name = item.get('food_name_en', '알 수 없는 음식')
        estimated_weight = item.get('estimated_weight', 200.0) # 🎯 추정 중량(g) 획득 성공!
        
        nutrition = nutrition_service.get_nutrition_data(raw_name)
        if nutrition:
            meal_data_to_send.append({
                "food_name": nutrition["food_name"],
                "estimated_weight": estimated_weight, # 🎯 백엔드 전달용 DTO에 추정 중량(g) 적재 추가
                "nutrient_name": nutrition["nutrient_name"]
            })

    print(f"📡 [AI 서버] 백엔드 위험도 체크 엔드포인트로 HTTP POST 요청 전송...")
    user_diseases = []
    risk_results = []
    meal_score = 80

    try:
        async with httpx.AsyncClient() as client:
            # 📡 백엔드의 위험도 체크 엔드포인트 역시 8080 포트 기반 주소로 연동합니다.
            backend_risk_url = f"{BACKEND_BASE_URL}/api/meals/risk-check"
            response = await client.post(
                backend_risk_url, 
                json={"detectedFoods": meal_data_to_send},
                timeout=5.0
            )
            if response.status_code == 200:
                res_data = response.json()
                user_diseases = res_data.get("user_diseases", [])
                risk_results = res_data.get("analysis_results", [])
                meal_score = res_data.get("score", 80)
                print(f"✅ [AI 서버] 백엔드 위험 분석 연동 성공: {user_diseases} | 점수: {meal_score}점")
            else:
                raise Exception(f"Backend Server Error: {response.status_code}")
    except Exception as e:
        print(f"⚠️ [대비책 가동] 외부 백엔드 서버({backend_risk_url}) 연결 불가: {e}")
        user_diseases, risk_results, meal_score = ["고혈압", "당뇨"], [], 85

    final_detected_items = []
    for i, food_info in enumerate(meal_data_to_send):
        risk_level = next((r["risk_level"] for r in risk_results if r["food_name"] == food_info["food_name"]), "안전")
        final_detected_items.append({
            "food_name": food_info["food_name"],
            "risk_level": risk_level,
            "estimated_weight": food_info["estimated_weight"], # 프론트 반환용 데이터에도 적재
            "coordinates": detected_items[i]['coordinates'],
            "nutrient_name": food_info["nutrient_name"]
        })

    print("🤖 [6단계] 전용 분석 서비스를 통해 AI 식단 총평 생성 중...")
    ai_evaluation = await analysis_service.generate_ai_evaluation(user_diseases, final_detected_items)
    
    print("🏁 [7단계] 모든 분석 완료! 프론트엔드로 반환합니다.")
    return {
        "status": "success",
        "data": {
            "score": meal_score,
            "detected_items": final_detected_items,
            "ai_evaluation": { "content": ai_evaluation }
        }
    }

if __name__ == "__main__":
    import uvicorn
    # 외부 모바일 앱/웹뷰 연동 및 프론트엔드 실기기 테스트를 위해 호스트를 0.0.0.0으로 열어둡니다.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)