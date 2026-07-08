import os
import pandas as pd
from fuzzywuzzy import process


class NutritionService:

    def __init__(self):
        self.csv_path = "food_nutrition_db_20260424_weight.csv"

        if os.path.exists(self.csv_path):
            try:
                self.df = pd.read_csv(self.csv_path, encoding="utf-8")
                self.food_list = self.df["음 식 명"].tolist()
                print(
                    f"✅ DB 로드 완료: {len(self.food_list)}개의 음식 데이터가 있습니다."
                )
            except Exception as e:
                print(f"❌ DB 로드 오류: {e}")
                self.df = pd.DataFrame()
                self.food_list = []
        else:
            print(f"⚠️ 경고: {self.csv_path} 파일을 찾을 수 없습니다.")
            self.df = pd.DataFrame()
            self.food_list = []

    def get_nutrition_data(
        self, name_from_vision: str, estimated_weight: float = None
    ):
        """VisionService에서 넘어온 이름과 추정 중량(g)을 기반으로

        DB의 1인분 기준 중량과 비교하여 동적 배율을 계산하고 영양 성분을 반환합니다.
        '샐러드'의 경우 DB에 없으므로 하드코딩된 신뢰성 데이터를 즉시 반환합니다.
        """
        # -------------------------------------------------------
        # 🛠️ [하드코딩 예외 처리: DB에 없는 '샐러드' 직접 주입]
        # -------------------------------------------------------
        if name_from_vision == "샐러드":
            # 일반적인 건강식 샐러드 1인분(기준: 200g) 스펙 정의
            db_base_weight = 200.0

            # AI가 추정한 무게에 맞춰 스케일링 비율 연산
            if estimated_weight is not None and estimated_weight > 0:
                serving_ratio = estimated_weight / db_base_weight
            else:
                serving_ratio = 1.0

            print(
                f"ℹ️ [하드코딩 보정] '샐러드' 발견 (AI 추정: {estimated_weight}g / 기준: {db_base_weight}g) -> 배율: {serving_ratio:.2f}배"
            )

            # 요청하신 9가지 필수 영양소 항목 맞춤 제공 (배율 적용 및 반올림)
            return {
                "food_name": "샐러드",
                "nutrient_name": {
                    "kcal": round(180.0 * serving_ratio, 2),
                    "carbs": round(12.0 * serving_ratio, 2),
                    "protein": round(15.0 * serving_ratio, 2),
                    "fat": round(8.0 * serving_ratio, 2),
                    "sugar": round(4.0 * serving_ratio, 2),
                    "sodium": round(220.0 * serving_ratio, 2),
                    "cholesterol": round(35.0 * serving_ratio, 2),
                    "kalium": round(450.0 * serving_ratio, 2),
                    "phos": round(180.0 * serving_ratio, 2),
                },
            }
        # -------------------------------------------------------

        if self.df.empty:
            print("❌ DB가 비어있어 데이터를 가져올 수 없습니다.")
            return None

        if name_from_vision in ["Food", "Tableware", "Bowl", "Plate"]:
            print(f"⏩ 무의미한 라벨 건너뜀: {name_from_vision}")
            return None

        # 1. 유사도 기반 최종 매칭
        best_match, score = process.extractOne(
            name_from_vision, self.food_list
        )
        print(
            f"🔍 [AI 매칭 중] 입력: '{name_from_vision}' -> 매칭 후보: '{best_match}' (점수: {score})"
        )

        # 2. 유사도 문턱 검증 및 영양소 배율 연산
        if score >= 50:
            match = self.df[self.df["음 식 명"] == best_match]
            if not match.empty:
                row = match.iloc[0]

                # DB에 기록된 해당 음식의 표준 1인분 기준 중량 가져오기
                db_base_weight = float(row.get("1인분량", 200))

                # 중량이 정상 주입되었을 경우 '추정중량 / DB기준중량'으로 동적 배율(serving_ratio) 정의
                if estimated_weight is not None and db_base_weight > 0:
                    serving_ratio = estimated_weight / db_base_weight
                else:
                    serving_ratio = 1.0

                print(
                    f"📊 [배율 연산 로그] AI 추정: {estimated_weight}g / DB 기준: {db_base_weight}g -> 도출된 배율: {serving_ratio:.2f}배"
                )

                # 소수점 둘째 자리까지 반올림(round) 처리하여 영양소 수치 스케일링
                return {
                    "food_name": row["음 식 명"],
                    "nutrient_name": {
                        "kcal": round(
                            float(row.get("에너지(kcal)", 0)) * serving_ratio, 2
                        ),
                        "carbs": round(
                            float(row.get("탄수화물(g)", 0)) * serving_ratio, 2
                        ),
                        "protein": round(
                            float(row.get("단백질(g)", 0)) * serving_ratio, 2
                        ),
                        "fat": round(
                            float(row.get("지방(g)", 0)) * serving_ratio, 2
                        ),
                        "sugar": round(
                            float(row.get("당류(g)", 0)) * serving_ratio, 2
                        ),
                        "sodium": round(
                            float(row.get("나트륨(mg)", 0)) * serving_ratio, 2
                        ),
                        "cholesterol": round(
                            float(row.get("콜레스테롤(mg)", 0))
                            * serving_ratio,
                            2,
                        ),
                        "kalium": round(
                            float(row.get("칼륨(mg)", 0)) * serving_ratio, 2
                        ),
                        "phos": round(
                            float(row.get("인(mg)", 0)) * serving_ratio, 2
                        ),
                    },
                }

        print(
            f"❌ 매칭 실패: '{name_from_vision}'와 유사한 음식을 DB에서 찾지 못함"
        )
        return None