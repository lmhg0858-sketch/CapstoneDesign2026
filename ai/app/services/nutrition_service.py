import pandas as pd
import os
from fuzzywuzzy import process

class NutritionService:
    def __init__(self):
        # CSV 파일명 확인 (확장자 .csv 주의)
        self.csv_path = "food_nutrition_db_20260424_weight.csv"
        
        # DB 로드
        if os.path.exists(self.csv_path):
            try:
                # 인코딩 문제 방지를 위해 utf-8-sig 사용
                self.df = pd.read_csv(self.csv_path, encoding='utf-8')
                self.food_list = self.df['음 식 명'].tolist()
                print(f"✅ DB 로드 완료: {len(self.food_list)}개의 음식 데이터가 있습니다.")
            except Exception as e:
                print(f"❌ DB 로드 오류: {e}")
                self.df = pd.DataFrame()
                self.food_list = []
        else:
            print(f"⚠️ 경고: {self.csv_path} 파일을 찾을 수 없습니다.")
            self.df = pd.DataFrame()
            self.food_list = []

    def get_nutrition_data(self, name_from_vision: str):
        """
        VisionService에서 넘어온 이름(한글 또는 영어)을 
        우리 DB 형식에 맞게 최종 매칭하고 영양 성분을 반환합니다.
        """
        if self.df.empty:
            print("❌ DB가 비어있어 데이터를 가져올 수 없습니다.")
            return None

        # [필터링] 'Food'나 'Tableware' 등 무의미한 단어가 들어오면 무시
        if name_from_vision in ["Food", "Tableware", "Bowl", "Plate"]:
            print(f"⏩ 무의미한 라벨 건너뜀: {name_from_vision}")
            return None

        # 1. 유사도 기반 최종 매칭 (데이터 정규화)
        # Gemini가 준 이름이 DB에 정확히 없어도 가장 비슷한 걸 찾습니다.
        best_match, score = process.extractOne(name_from_vision, self.food_list)
        
        # 서버 터미널에 로그 출력 (이걸 봐야 어디서 틀렸는지 알 수 있습니다!)
        print(f"🔍 [AI 매칭 중] 입력: '{name_from_vision}' -> 매칭 후보: '{best_match}' (점수: {score})")
        
        # 2. 유사도 문턱을 50점으로 낮춤 (더 유연하게 매칭)
        if score >= 80:
            match = self.df[self.df['음 식 명'] == best_match]
            if not match.empty:
                row = match.iloc[0]
                return {
                    "food_name": row['음 식 명'],
                    "nutrient_name": {
                        "kcal": float(row.get('에너지(kcal)', 0)),
                        "carbs": float(row.get('탄수화물(g)', 0)),
                        "protein": float(row.get('단백질(g)', 0)),
                        "fat": float(row.get('지방(g)', 0)),
                        "sugar": float(row.get('당류(g)', 0)),
                        "sodium": float(row.get('나트륨(mg)', 0)),
                        "cholesterol": float(row.get('콜레스테롤(mg)', 0)),
                        "kalium": float(row.get('칼륨(mg)', 0)),
                        "phos": float(row.get('인(mg)', 0))
                    }
                }
        
        print(f"❌ 매칭 실패: '{name_from_vision}'와 유사한 음식을 DB에서 찾지 못함")
        return None