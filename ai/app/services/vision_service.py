import os
import base64
from openai import OpenAI  # OpenAI 라이브러리 추가
from google.cloud import vision

class VisionService:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()
        # ✅ OpenAI API 키 설정
        key_path = "storage/openai_key.txt"
        
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"❌ '{key_path}' 파일을 찾을 수 없습니다. 키 파일을 생성해 주세요.")
            
        with open(key_path, "r", encoding="utf-8") as f:
            api_key = f.read().strip()
            
        self.openai_client = OpenAI(api_key=api_key)

    def decode_image(self, base64_str: str):
        try:
            if "," in base64_str:
                base64_str = base64_str.split(",", 1)[1]
            return base64.b64decode(base64_str)
        except Exception:
            return None

    async def analyze_food_image(self, base64_str: str, food_list: list = None):
        image_bytes = self.decode_image(base64_str)
        if not image_bytes: return {"error": "이미지 디코딩 실패"}

        # 1. Vision API: 좌표 추출
        image = vision.Image(content=image_bytes)
        objects = self.client.object_localization(image=image).localized_object_annotations

        # 식기류 제외하고 진짜 음식 박스만 카운트
        food_boxes = [obj for obj in objects if obj.name not in ["Tableware", "Bowl", "Plate", "Container"]]
        box_count = len(food_boxes)
        

        # 2. AI 분석 (GPT-4o 또는 Gemini)
        detected_names = []
        if box_count > 0:
            try:
                pure_base64 = base64_str.split(",")[-1] if "," in base64_str else base64_str
                allowed_foods = ", ".join(food_list[:400]) if food_list else "한국 음식"
                
                # 💡 [프롬프트 튜닝] 개수를 지정해줍니다.
                prompt = f"""
        너는 최고의 식단 분석 전문가야. 
        사진 속에서 눈에 띄는 주요 한국 음식 {box_count}개를 찾아줘.
        
        [지시 사항]
        1. 반드시 아래의 [음식 리스트] 내에 존재하는 명칭으로만 대답해.
        2. 사진의 색상, 재료 구성을 보고 가장 시각적으로 일치하는 이름을 골라.
        3. 다른 설명 없이 음식 이름 {box_count}개만 콤마(,)로 구분해서 나열해.
        
        [음식 리스트]
        {allowed_foods}
        """

                # GPT-4o 사용 시 (Gemini 사용 시 해당 호출부로 변경)
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{pure_base64}"}}
                        ]
                    }]
                )
                gpt_text = response.choices[0].message.content
                detected_names = [name.strip() for name in gpt_text.split(",")]
                print(f"✅ AI 분석 결과: {detected_names}")
            except Exception as e:
                print(f"❌ AI 분석 실패: {e}")

        # 3. 매칭 및 결과 생성
        detected_foods = []
        for i, obj in enumerate(food_boxes):
            # AI가 준 이름이 있으면 쓰고, 부족하면 리스트의 마지막 이름이라도 씁니다.
            if detected_names:
                name_idx = min(i, len(detected_names) - 1)
                food_name = detected_names[name_idx]
            else:
                food_name = obj.name # 최후의 보루

            vertices = obj.bounding_poly.normalized_vertices
            detected_foods.append({
                "food_name_en": food_name, 
                "confidence": obj.score,
                "coordinates": [{"x": v.x, "y": v.y} for v in vertices]
            })

        return detected_foods