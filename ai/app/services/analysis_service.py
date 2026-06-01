from openai import OpenAI
import os
from app.services.rag_service import RAGService 
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from app.models.schema import BackendMealLogRequest, FrontendMealLogResponse
from fuzzywuzzy import process # 🎯 우리 CSV DB 진짜 명칭 역추적 매칭용 라이브러리

class AnalysisService:
    def __init__(self):
        # 기존 OpenAI API 키 로드 파이프라인
        key_path = "storage/openai_key.txt"
        
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"❌ '{key_path}' 파일을 찾을 수 없습니다. 키 파일을 생성해 주세요.")
            
        with open(key_path, "r", encoding="utf-8") as f:
            api_key = f.read().strip()
            
        self.openai_client = OpenAI(api_key=api_key)
        self.rag_service = RAGService()

    async def generate_ai_evaluation(self, user_diseases, final_items):
        """
        [기존 기능] 단일 식사 사진 분석용 AI 총평 생성
        """
        try:
            food_summary = ", ".join([f"{item['food_name']}(위험도:{item['risk_level']})" for item in final_items])
            print("🕵️‍♂️ [AI 총평 서비스] 로컬 벡터 DB에서 환자 맞춤형 RAG 지침 수집 중...")
            rag_medical_context = self.rag_service.retrieve_meal_evaluation_context(
                user_diseases=user_diseases, 
                final_items=final_items
            )
            
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
2. [RAG 기반 의학 가이드라인]에 언급된 구체적인 행동 대안을 반드시 본문에 직접 인용하여 실천 가능한 솔루션을 제공해줘.
3. 가이드라인에 없는 일반 상식이나 거짓 정보를 지어내지 말고, 오직 제공된 임상 지침 데이터의 핵심 문맥을 바탕으로 신뢰성 있게 조언해줘.
"""
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400, 
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ [AI 총평 에러] RAG 연동 총평 생성 실패: {e}")
            return f"현재 {user_diseases} 관리 중이시므로 나트륨, 단순당 및 혈당 지수 관리에 각별히 유의하시기 바랍니다."


    # ====================================================================
    # 📊 [초고도화 패치] 홈 화면 누적 식단 평가 및 3가지 한식 추천 (Fuzzy 매칭)
    # ====================================================================
    async def generate_daily_summary_and_recommendation(self, log_data: BackendMealLogRequest, nutrition_service) -> dict:
        """
        스프링 누적 로그 분석 ➔ 4대 기준 RAG 검색 ➔ 대학병원 수석 임상 영양사급 초정밀 진단 ➔ 우리 DB 진짜 명칭 역추적 매칭
        """
        diseases_str = ", ".join(log_data.user_diseases)
        
        # [Step 1] 전성분 확장형 누적 RAG 엔진 호출
        print(f"🕵️‍♂️ [AI 서비스] 복합 질환({diseases_str}) 기반 누적 RAG 임상 컨텍스트 수집 가동...")
        rag_context = self.rag_service.retrieve_daily_accumulation_context(
            user_diseases=log_data.user_diseases,
            food_log=log_data.food_log
        )

        # [Step 2] 출력 JSON 구조 파서 세팅
        parser = JsonOutputParser(pydantic_object=FrontendMealLogResponse)

        # [Step 3] 💎 3대 인스트럭션 규칙 기반 초정밀 프롬프트 가공 (페르소나 및 병태생리 유도)
        prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 대한민국 최고의 대학병원 만성질환 전문 수석 임상 영양사입니다.
제공된 [의학 가이드라인 RAG 컨텍스트]는 공인된 학술 지침이므로, 이를 '최우선 판단 가이드라인'으로 삼아 환자의 식단을 냉정하고 과학적으로 해부해야 합니다.
당신의 진단은 환자의 복합적인 만성질환 메커니즘을 꿰뚫어야 합니다.

반드시 다른 인사말이나 마크다운 태그(```json) 없이, 오직 지정된 JSON 포맷 구조로만 응답하세요.

[의학 가이드라인 RAG 컨텍스트]
{rag_context}"""),
            ("human", """
[환자 진단 질환]: {diseases}
[오늘 하루 누적 식사 상세 로그]: {food_log_json}

위 임상 데이터를 기반으로, 아래 3대 인스트럭션 원칙에 맞춰 JSON 명세를 완성해 주세요:

1. `day_evaluation` 작성 원칙:
   - **규칙 A (정량적 패턴 분석)**: 환자의 식사 로그에서 오늘 가장 심각하게 과다 누적된 빌런 성분(예: 당류, 나트륨, 포화지방 등)이나 위험한 연속 섭취 패턴을 구체적인 음식명과 함께 콕 집어내세요.
   - **규칙 B (병태생리 메커니즘 연계)**: 이 성분들이 왜 환자의 기저질환({diseases})을 악화시키는지 구체적인 의학적 인과관계(예: '혈관벽 탄력 저하', '췌장 인슐린 과부하', '중성지방 합성 및 혈류 장애')를 엮어서 냉정하고 신뢰성 있게 설명하세요.
   - **규칙 C (행동 중심의 교정 처방)**: 가이드라인을 인용하여 "내일 아침 당장 실천할 수 있는 조리법 변경, 국물 남기기, 식이섬유 먼저 먹는 식사 순서 교정" 등 구체적인 실천 솔루션을 제공하세요.
   - **형식**: 반드시 다른 설명 없이 전문가 어조로 3~4문장 이내의 완결된 문장으로 `evaluation_content`에 작성하고, `risk_level`은 반드시 백엔드가 1차 판정한 등급인 "{backend_status}"를 그대로 토스하세요.

2. `day_recom` 작성 원칙:
   - 오늘 식단에서 과다 누적된 영양적 타격을 방어(배출 유도 등)하거나 부족한 미세 영양을 완벽히 채워줄 수 있는 만성질환자용 '안전하고 대중적인 한국 음식 명칭(예: 보리밥, 대구탕, 두부구이 등)'으로 **반드시 서로 다른 3가지 요리**를 선정하세요.
   - 각 추천 음식의 `content` 항목에는 가이드라인(RAG Context)에 언급된 구체적인 의학적 추천 사유(예: "~ 성분이 풍부해 혈당 상승을 완만하게 조절하고 혈관을 보호합니다")를 한 문장으로 명확히 녹여내세요.

{format_instructions}
""")
        ])

        llm = ChatOpenAI(model="gpt-4o", temperature=0.1, openai_api_key=self.openai_client.api_key)
        chain = prompt | llm | parser

        # [Step 4] GPT 가동 및 1차 JSON 결과 수집
        ai_response = chain.invoke({
            "rag_context": rag_context,
            "diseases": diseases_str,
            "backend_status": log_data.daily_risk.status, 
            "food_log_json": json.dumps([f.dict() for f in log_data.food_log], ensure_ascii=False),
            "format_instructions": parser.get_format_instructions()
        })

        # [Step 5] Fuzzy Matching 알고리즘: 3가지 추천 메뉴를 우리 CSV DB 진짜 명칭으로 강제 매핑
        validated_recommendations = []
        for recom_item in ai_response.get("day_recom", []):
            gpt_suggested_name = recom_item["food_name"]
            
            best_match, score = process.extractOne(gpt_suggested_name, nutrition_service.food_list)
            print(f"🔄 [추천 메뉴 DB 매칭] GPT 제안: '{gpt_suggested_name}' ➔ 우리 DB 진짜 명칭 변경: '{best_match}' (매칭 점수: {score})")
            
            if score >= 60:
                recom_item["food_name"] = best_match
            validated_recommendations.append(recom_item)

        ai_response["day_recom"] = validated_recommendations
        ai_response["id"] = 5  
        ai_response["userId"] = log_data.food_log[0].userId if log_data.food_log else "test1"
        
        return ai_response