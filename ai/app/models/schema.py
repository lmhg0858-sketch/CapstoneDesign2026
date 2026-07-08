from pydantic import BaseModel
from typing import List

# UI 강조를 위한 좌표 모델
class BoxCoordinates(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

# 프론트엔드에서 보낼 요청 규격
class FrontendRequest(BaseModel):
    mime_type: str
    image_base64: str
    

class DailyRisk(BaseModel):
    date: str
    status: str
    total_count: int
    danger_count: int
    caution_count: int
    safe_count: int

class FoodLogItem(BaseModel):
    id: int
    userId: str
    foodName: str
    eatTime: str
    kcal: float
    carbs: float
    protein: float
    fat: float
    sugar: float
    sodium: float
    cholesterol: float
    kalium: float
    phos: float
    risk_level: str

# 1. 백엔드로부터 넘겨받는 전체 데이터 스키마 바인딩
class BackendMealLogRequest(BaseModel):
    user_diseases: List[str]
    daily_risk: DailyRisk
    food_log: List[FoodLogItem]

# 2. 프론트엔드로 내보낼 최종 추천 아이템 포맷
class DayRecomItem(BaseModel):
    food_name: str
    content: str

# 3. 프론트엔드로 내보낼 최종 종합 레이아웃 포맷
class DayEvaluation(BaseModel):
    risk_level: str
    evaluation_content: str

class FrontendMealLogResponse(BaseModel):
    id: int
    userId: str
    day_evaluation: DayEvaluation
    day_recom: List[DayRecomItem]