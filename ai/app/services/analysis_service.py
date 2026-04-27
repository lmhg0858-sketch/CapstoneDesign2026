from openai import OpenAI
import os

class AnalysisService:
    def __init__(self):
        # 기존 VisionService에서 쓰던 클라이언트와 동일하게 설정
        key_path = "storage/openai_key.txt"
        
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"❌ '{key_path}' 파일을 찾을 수 없습니다. 키 파일을 생성해 주세요.")
            
        with open(key_path, "r", encoding="utf-8") as f:
            api_key = f.read().strip()
            
        self.openai_client = OpenAI(api_key=api_key)

    async def generate_ai_evaluation(self, user_diseases, final_items):
        """
        [6단계] 질병 정보와 식단 위험도를 종합하여 영양사 AI 총평 생성
        """
        try:
            # AI에게 줄 정보 요약
            food_summary = ", ".join([f"{item['food_name']}(위험도:{item['risk_level']})" for item in final_items])
            
            prompt = f"""
            너는 전문 영양사야. 
            사용자의 현재 질환: {user_diseases}
            오늘 식사 메뉴: {food_summary}
            
            위 정보를 바탕으로 건강 상태에 맞는 식단 평가와 조언을 5 문장 이하로 친절하게 작성해줘.
            특히 '위험' 판정을 받은 음식에 대해서는 왜 주의해야 하는지 언급해줘.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI 총평 생성 실패: {e}")
            return f"현재 {user_diseases} 관리 중이시므로 나트륨과 당분 섭취에 유의하시기 바랍니다."