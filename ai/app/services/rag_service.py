# app/services/rag_service.py 전체를 이 완전 동적 코드로 교체해 주세요.
import os
from app.rag.vector_store import get_or_create_vector_store

class RAGService:
    def __init__(self):
        # 로컬 오픈소스 BAAI/bge-m3 벡터 스토어 로드
        self.vector_store = get_or_create_vector_store()
        
        # 🎯 [동적 제어판] 질환 '하나당' 최종 LLM 프롬프트에 제공할 핵심 청크의 개수 상한선입니다.
        # 질환이 1개면 총 2개, 질환이 3개면 총 6개의 청크가 유연하게 가동됩니다.
        self.CHUNKS_PER_DISEASE = 3
        
        # 질환별 집중 검색 한국어 영양소 매핑 맵
        self.disease_nutrient_map = {
            "고혈압": ["나트륨", "콜레스테롤", "칼로리", "지방"],
            "당뇨": ["당", "탄수화물", "칼로리", "지방", "혈당"],
            "고지혈증": ["콜레스테롤", "지방", "칼로리", "나트륨"],
            "신장질환": ["나트륨", "칼륨", "인", "단백질"]
        }
        
        # 영문 영양소 키값을 한국어로 매핑해주는 변환 가이드 맵
        self.nutrient_eng_to_kor = {
            "sodium": "나트륨",
            "sugar": "당류",
            "cholesterol": "콜레스테롤",
            "fat": "지방",
            "kalium": "칼륨",
            "phos": "인",
            "carbs": "탄수화물",
            "kcal": "칼로리",
            "protein": "단백질"
        }

    def retrieve_meal_evaluation_context(self, user_diseases: list, final_items: list) -> str:
        """
        [Universal Dynamic Matrix RAG] 
        질환 개수(N)와 음식 개수(M)가 몇 개든 상관없이, 모든 차원의 입력을 동적으로 수용하여
        데이터 쏠림 현상을 컴퓨터 과학적으로 완벽히 격리 및 분배합니다.
        """
        if not final_items or not user_diseases:
            return "일반 영양학적 건강 식단 가이드라인을 기준으로 적용하세요."
            
        valid_diseases = [d for d in user_diseases if d not in ["정보 없음", "미등록", "일반"]]
        if not valid_diseases:
            return "일반 영양학적 건강 식단 가이드라인을 기준으로 적용하세요."

        integrated_context_list = []
        
        # ====================================================================
        # 🏥 1. [질환 N개 동적 순회] 입력된 질환 개수가 몇 개든 순서대로 공간을 격리합니다.
        # ====================================================================
        for disease in valid_diseases:
            target_nutrients = self.disease_nutrient_map.get(disease, ["나트륨", "당류"])
            
            # 🎯 음식별로 각각 수집된 청크들을 저장할 2차원 리스트 저장소 빌드
            # 음식 개수가 2개든, 5개든, 10개든 각 음식만의 독립 바구니를 동적으로 생성합니다.
            food_baskets = [] 
            
            # ====================================================================
            # 🍽️ 2. [음식 M개 동적 순회] 입력된 음식 개수만큼 바구니를 열고 개별 검색합니다.
            # ====================================================================
            for item in final_items:
                food_name = item['food_name']
                risk_level = item['risk_level'] 
                raw_nutrients = item['nutrient_name']
                
                # 한국어 영양소 매핑 바인딩
                matched_kor_nutrients = []
                for eng_key, kor_key in self.nutrient_eng_to_kor.items():
                    if kor_key in target_nutrients and raw_nutrients.get(eng_key, 0) > 0:
                        matched_kor_nutrients.append(kor_key)
                
                nutrient_str = ", ".join(matched_kor_nutrients) if matched_kor_nutrients else "영양성분"

                # 위험도 맥락에 맞춘 카테고리 필터 분리
                if risk_level in ["위험", "주의"]:
                    allowed_categories = ["대체식품", "조리팁", "음식궁합", "식사지침"]
                else:
                    allowed_categories = ["음식궁합", "식사지침"]

                # 동적 확장 쿼리 빌드
                clean_query = f"{disease} 환자가 {food_name}을(를) 섭취할 때 {nutrient_str} 관리 가이드라인"
                
                search_filter = {
                    "$and": [
                        {"질환명": disease},
                        {"카테고리": {"$in": allowed_categories}}
                    ]
                }
                
                try:
                    # 각 음식 개별 바구니용 임시 수집 리스트
                    current_food_chunks = []
                    
                    # 이 음식에 대해 가장 관련성이 높은 문서 후보군 추출
                    matched_docs = self.vector_store.similarity_search(
                        query=clean_query,
                        k=self.CHUNKS_PER_DISEASE, 
                        filter=search_filter
                    )
                    
                    for doc in matched_docs:
                        chunk_format = f"• [{doc.metadata['카테고리']}] {doc.page_content}"
                        if chunk_format not in current_food_chunks:
                            current_food_chunks.append(chunk_format)
                    
                    # 🎯 해당 음명의 결과가 존재한다면 마스터 음식 바구니 리스트에 투척
                    if current_food_chunks:
                        food_baskets.append(current_food_chunks)
                                
                except Exception as e:
                    print(f"❌ [RAG 다중 검색 에러] {disease}-{food_name} 필터 검색 실패: {e}")
            
            # ====================================================================
            # 🎯 3. [진짜 엔지니어링: 다차원 라운드 로빈 스케줄링 가동]
            # ====================================================================
            # 음식 개수(M)가 몇 개가 오든 상관없이, 1번 음식의 1등 ➔ 2번 음식의 1등 ➔ 3번 음식의 1등 ➔ 
            # 다시 1번 음식의 2등 순서로 '교차 정렬'하여 한 식단의 소외되는 메뉴가 없도록 만듭니다.
            combined_disease_chunks = []
            
            if food_baskets:
                # 등록된 음식 바구니 중 가장 많이 담긴 바구니의 크기 확인
                max_chunks_in_basket = max(len(basket) for basket in food_baskets)
                
                for step in range(max_chunks_in_basket):
                    for basket in food_baskets:
                        if step < len(basket):
                            chunk = basket[step]
                            if chunk not in combined_disease_chunks:
                                combined_disease_chunks.append(chunk)
            
            # ====================================================================
            # ✂️ 4. [질환별 정량 슬라이싱 및 최종 수집]
            # ====================================================================
            # 균형 있게 섞인 리스트에서 설정해둔 질환당 청크 개수(예: 2개)만큼만 최종 선별
            final_disease_guidelines = combined_disease_chunks[:self.CHUNKS_PER_DISEASE]
            
            if final_disease_guidelines:
                disease_block = f"[{disease} 환자용 맞춤 지침]\n" + "\n".join(final_disease_guidelines)
                integrated_context_list.append(disease_block)
                
        # 5. 모든 질환블록 최종 합병 리턴
        final_rag_context = "\n\n".join(integrated_context_list)
        print(f"🎯 [RAG 쿼리 엔진] 총 {len(valid_diseases)}개 질환 및 {len(final_items)}개 음식 동적 매트릭스 인덱싱 완료!")
        return final_rag_context