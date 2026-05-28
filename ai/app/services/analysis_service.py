from openai import OpenAI
import os
# 🎯 우리가 완성한 한글 매트릭스 RAG 서비스 임포트
from app.services.rag_service import RAGService 

class AnalysisService:
    def __init__(self):
        # 기존 OpenAI API 키 로드 파이프라인
        key_path = "storage/openai_key.txt"
        
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"❌ '{key_path}' 파일을 찾을 수 없습니다. 키 파일을 생성해 주세요.")
            
        with open(key_path, "r", encoding="utf-8") as f:
            api_key = f.read().strip()
            
        self.openai_client = OpenAI(api_key=api_key)
        
        # 🎯 RAG 검색 서비스 객체를 엔진 시동 시 싱글톤 형태로 로드합니다.
        self.rag_service = RAGService()

    async def generate_ai_evaluation(self, user_diseases, final_items):
        """
        [6단계] 백엔드 수신 질병 정보, 다중 식단 위험도, 그리고 한국어 RAG 의학 지침을 
        종합 오케스트레이션하여 임상 기반 맞춤 영양사 AI 총평을 생성합니다.
        """
        try:
            # 1. 감지된 음식들의 요약본 구성 (음식명과 백엔드가 판별한 위험 등급 매핑)
            food_summary = ", ".join([f"{item['food_name']}(위험도:{item['risk_level']})" for item in final_items])
            
            # 2. 🎯 [RAG 인드라 지식 추출] 
            # 우리가 완성한 완전 동적 함수를 통해 질환 N개, 음식 M개의 매트릭스 임상 지침을 가져옵니다.
            print("🕵️‍♂️ [AI 총평 서비스] 로컬 벡터 DB에서 환자 맞춤형 RAG 지침 수집 중...")
            rag_medical_context = self.rag_service.retrieve_meal_evaluation_context(
                user_diseases=user_diseases, 
                final_items=final_items
            )
            
            # 3. 🎯 RAG 컨텍스트를 최우선 기준으로 삼도록 지시하는 초정밀 프롬프트 가공
            prompt = f"""
너는 대한민국 최고의 임상 영양사이자 만성질환 헬스케어 AI 컨설턴트야. 
제공된 [환자 맞춤형 임상 지침]을 '최우선 정답 기준'으로 삼아 사용자의 오늘 식단을 철저히 평가하고 처방을 내려줘.

[환자 및 오늘 식사 정보]
- 환자의 현재 만성질환: {user_diseases}
- 오늘 섭취한 식사 메뉴: {food_summary}

[환자 맞춤형 임상 지침 (RAG 기반 의학 가이드라인)]
{rag_medical_context}

[작성 가이드라인 (반드시 준수할 것)]
1. 환자가 쉽게 이해하고 실천할 수 있도록 '5문장 이하'로 매우 친절하고 따뜻하게 작성해줘.
2. [RAG 기반 의학 가이드라인]에 언급된 구체적인 행동 대안(예: 대체 식품 활용, 나트륨/당을 줄이는 조리 팁, 이로운 음식 궁합 등)을 반드시 본문에 직접 인용하여 실천 가능한 솔루션을 제공해줘.
3. 특히 '위험'이나 '주의' 판정을 받은 음식이 있다면, 가이드라인의 의학적 근거에 기반하여 왜 위험하고 어떻게 먹어야 안전한지 명확하게 경고해줘.
4. 가이드라인에 없는 일반 상식이나 거짓 정보를 지어내지 말고, 오직 제공된 임상 지침 데이터의 핵심 문맥을 바탕으로 신뢰성 있게 조언해줘.
"""
            
            # 4. GPT-4o 최적화 추론 가동
            # 임상 지침의 풍부한 대안(대체식품 등) 인용을 위해 토큰을 400으로 넉넉하게 늘려 가독성을 확보합니다.
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400, 
                temperature=0.3 # 일관되고 전문적인 답변 품질을 위해 온도를 낮춰 고정합니다.
            )
            
            final_output = response.choices[0].message.content.strip()
            print("✅ [AI 총평 서비스] RAG 융합형 전문 영양사 총평 텍스트 생성 완료!")
            return final_output
            
        except Exception as e:
            print(f"❌ [AI 총평 에러] RAG 연동 총평 생성 실패: {e}")
            return f"현재 {user_diseases} 관리 중이시므로 나트륨, 단순당 및 혈당 지수 관리에 각별히 유의하시기 바랍니다."