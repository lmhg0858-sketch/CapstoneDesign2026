import os
import io
import base64
from openai import OpenAI
from google.cloud import vision
from PIL import Image

class VisionService:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()
        key_path = "storage/openai_key.txt"
        
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"❌ '{key_path}' 파일을 찾을 수 없습니다.")
            
        with open(key_path, "r", encoding="utf-8") as f:
            api_key = f.read().strip()
            
        self.openai_client = OpenAI(api_key=api_key)

    def decode_image(self, base64_str: str):
        """Base64 문자열을 디코딩하여 바이트 및 Pillow 이미지 객체로 반환"""
        try:
            if "," in base64_str:
                base64_str = base64_str.split(",", 1)[1]
            image_bytes = base64.b64decode(base64_str)
            pil_image = Image.open(io.BytesIO(image_bytes))
            return image_bytes, pil_image
        except Exception:
            return None, None

    def get_crop_coordinates(self, vertices, img_width, img_height):
        """정규화된 좌표를 Pillow 크롭용 실제 픽셀 좌표로 변환"""
        # 비어있는 좌표나 누락된 바운딩 박스 예외 처리 대비
        x_coords = [int(v.x * img_width) for v in vertices if v.x is not None]
        y_coords = [int(v.y * img_height) for v in vertices if v.y is not None]
        
        if not x_coords or not y_coords:
            return 0, 0, img_width, img_height
            
        return min(x_coords), min(y_coords), max(x_coords), max(y_coords)

    def analyze_single_crop(self, cropped_base64: str, food_list: list = None) -> str:
        """(3) 크롭한 이미지 조각마다 개별 음식 분석 요청 (GPT-4o 활용)"""
        try:
            allowed_foods = ", ".join(food_list[:400]) if food_list else "한국 음식"
            
            prompt = f"""
너는 최고의 식단 분석 전문가야. 
제공된 이미지는 전체 사진에서 하나의 음식 영역만 크롭한 조각 사진이야.
이 사진 속 음식을 확인하고, 아래의 [음식 리스트]에서 가장 정확한 매칭 명칭 하나만 답변해줘.

[지시 사항]
1. 반드시 아래의 [음식 리스트] 내 명칭만 사용해.
2. 어떠한 사족(설명, 인사말 등)도 절대 붙이지 말고 딱 '음식 이름' 한 단어만 반환해.
   예시: 떡국

[음식 리스트]
{allowed_foods}
"""
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{cropped_base64}"}}
                    ]
                }],
                temperature=0,
                max_tokens=20 # 음식 한 단어면 충분하므로 토큰 절약
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ 크롭 이미지 개별 분석 실패: {e}")
            return "알 수 없는 음식"

    async def analyze_food_image(self, base64_str: str, food_list: list = None):
        # 이미지 디코딩 및 Pillow 객체 획득
        image_bytes, pil_image = self.decode_image(base64_str)
        if not image_bytes or not pil_image: 
            return {"error": "이미지 디코딩 실패"}

        img_width, img_height = pil_image.size

        # (1) Vision API: 객체 탐지 진행
        image = vision.Image(content=image_bytes)
        objects = self.client.object_localization(image=image).localized_object_annotations

        # 식기류 및 노이즈 객체 필터링
        food_boxes = [obj for obj in objects if obj.name not in ["Tableware", "Bowl", "Plate", "Container", "Table ware"]]

        detected_foods = []

        # (2) 바운딩 박스 위치별 크롭 및 (3) 분석 루프 진행
        for obj in food_boxes:
            vertices = obj.bounding_poly.normalized_vertices
            
            # 1. 실제 픽셀 좌표 획득
            xmin, ymin, xmax, ymax = self.get_crop_coordinates(vertices, img_width, img_height)
            
            # 2. 이미지 크롭 진행
            cropped_pil = pil_image.crop((xmin, ymin, xmax, ymax))
            
            # 3. 크롭된 이미지를 GPT 전송용 Base64 문자열로 변환
            buffered = io.BytesIO()
            cropped_pil.save(buffered, format="JPEG")
            cropped_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            # 4. 개별 크롭 이미지 분석 요청
            food_name = self.analyze_single_crop(cropped_base64, food_list)
            
            # 5. 최종 데이터 포맷 적재
            detected_foods.append({
                "food_name_en": food_name,  # NIA 영양 데이터베이스 매핑용 키워드
                "confidence": obj.score,
                "coordinates": [{"x": v.x, "y": v.y} for v in vertices]
            })

        print(f"✅ AI 크롭 기반 최종 분석 완료: {[f['food_name_en'] for f in detected_foods]}")
        return detected_foods