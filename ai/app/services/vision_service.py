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
        x_coords = [int(v.x * img_width) for v in vertices if v.x is not None]
        y_coords = [int(v.y * img_height) for v in vertices if v.y is not None]
        
        if not x_coords or not y_coords:
            return 0, 0, img_width, img_height
            
        return min(x_coords), min(y_coords), max(x_coords), max(y_coords)

    def analyze_single_crop(self, cropped_base64: str, food_list: list = None) -> tuple:
        """
        🎯 [고도화 패치]: 크롭한 이미지 조각을 기반으로 음식명과 중량(g)을 쌍으로 추정합니다.
        """
        try:
            allowed_foods = ", ".join(food_list[:400]) if food_list else "한국 음식"
            
            # 크롭 이미지 전용 3차원 볼륨 및 100원 동전 대비 정밀 중량 추정 인스트럭션 심기
            prompt = f"""
너는 최고의 식단 분석 및 음식 중량(g) 추정 전문가야. 
제공된 이미지는 전체 사진에서 하나의 음식 영역만 크롭한 조각 사진이야.

[중요: 중량(g) 추정 지시]
전체 사진 속에는 크기 참조용 '100원 동전(지름 22.8mm)'이 함께 촬영되어 있어.
이 크롭된 음식의 면적과 3차원 부피감을 동전 및 주변 용기 크기와 상대적으로 비교하여, 실제 무게(g)를 최대한 과학적으로 추정해줘.
(예: 일반적인 공기밥 한 그릇 분량 크기면 200~210, 소량의 밑반찬 종지 크기면 30~50, 국그릇 크기면 300~400 등)

[지시 사항]
1. 반드시 아래의 [음식 리스트] 내 명칭 중 가장 정확한 매칭 명칭 하나만 골라야 해.
2. 어떠한 사족이나 설명, 마크다운, g 단위 문자도 절대 붙이지 말고, 반드시 '음식명:중량' 형태로 딱 한 쌍만 반환해.
   (출력 예시: 제육볶음:250)

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
                max_tokens=40 # 포맷이 짧으므로 소량 설정
            )
            
            gpt_text = response.choices[0].message.content.strip()
            
            # 결과 파싱 진행 ('음식명:중량' 형태 해체)
            if ":" in gpt_text:
                name_part, weight_part = gpt_text.split(":", 1)
                food_name = name_part.strip()
                try:
                    estimated_weight = float(weight_part.strip())
                except ValueError:
                    estimated_weight = 200.0 # 파싱 예외 발생 시 디폴트 보정값
            else:
                food_name = gpt_text
                estimated_weight = 200.0
                
            return food_name, estimated_weight
            
        except Exception as e:
            print(f"❌ 크롭 이미지 개별 분석 및 양 추정 실패: {e}")
            return "알 수 없는 음식", 200.0

    async def analyze_food_image(self, base64_str: str, food_list: list = None):
        image_bytes, pil_image = self.decode_image(base64_str)
        if not image_bytes or not pil_image: 
            return {"error": "이미지 디코딩 실패"}

        img_width, img_height = pil_image.size

        # (1) Vision API: 객체 탐지 진행
        image = vision.Image(content=image_bytes)
        objects = self.client.object_localization(image=image).localized_object_annotations

        # 식기류 필터링
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
            
            # 4. 개별 크롭 이미지 분석 및 중량 추정 동시 요청
            food_name, estimated_weight = self.analyze_single_crop(cropped_base64, food_list)
            
            # 5. 최종 데이터 포맷 적재 (estimated_weight 추가)
            detected_foods.append({
                "food_name_en": food_name,  # DB 매핑용 한글명
                "confidence": obj.score,
                "estimated_weight": estimated_weight,  # 추정 중량(float) 주입
                "coordinates": [{"x": v.x, "y": v.y} for v in vertices]
            })

        print(f"✅ AI 크롭 및 양 추정 최종 완성: {[(f['food_name_en'], f['estimated_weight']) for f in detected_foods]}")
        return detected_foods