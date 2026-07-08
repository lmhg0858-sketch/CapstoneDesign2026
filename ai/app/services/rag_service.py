import os
from app.rag.vector_store import get_or_create_vector_store

class RAGService:
    def __init__(self):
        # 로컬 오픈소스 BAAI/bge-m3 벡터 스토어 로드
        self.vector_store = get_or_create_vector_store()
        
        # 🎯 [동적 제어판] 질환 '하나당' 최종 LLM 프롬프트에 제공할 핵심 청크의 개수 상한선입니다.
        self.CHUNKS_PER_DISEASE = 3
        
        # 질환별 집중 검색 한국어 영양소 매핑 맵
        self.disease_nutrient_map = {
            "고혈압": ["나트륨", "콜레스테롤", "칼로리", "지방"],
            "당뇨병": ["당", "탄수화물", "칼로리", "지방", "혈당"],
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
        단일 식사 사진 분석 시 작동하는 함수입니다.
        """
        if not final_items or not user_diseases:
            return "일반 영양학적 건강 식단 가이드라인을 기준으로 적용하세요."
            
        valid_diseases = [d for d in user_diseases if d not in ["정보 없음", "미등록", "일반"]]
        if not valid_diseases:
            return "일반 영양학적 건강 식단 가이드라인을 기준으로 적용하세요."

        integrated_context_list = []
        
        # ====================================================================
        # 🏥 1. [질환 N개 동적 순회]
        # ====================================================================
        for disease in valid_diseases:
            db_disease = "당뇨병" if disease == "당뇨" else disease
            target_nutrients = self.disease_nutrient_map.get(db_disease, ["나트륨", "당류"])
            food_baskets = [] 
            
            # ====================================================================
            # 🍽️ 2. [음식 M개 동적 순회]
            # ====================================================================
            for item in final_items:
                food_name = item['food_name']
                raw_nutrients = item['nutrient_name']
                
                matched_kor_nutrients = []
                for eng_key, kor_key in self.nutrient_eng_to_kor.items():
                    if kor_key in target_nutrients and raw_nutrients.get(eng_key, 0) > 0:
                        matched_kor_nutrients.append(kor_key)
                
                nutrient_str = ", ".join(matched_kor_nutrients) if matched_kor_nutrients else "영양성분"

                # 🎯 [쿼리 최적화]: 자연스러운 의학용 질의문으로 변경하여 시맨틱 검색 효율 극대화
                clean_query = f"{db_disease} 환자의 {food_name} 섭취 가이드라인 및 {nutrient_str} 식사 지침 관리"
                
                # 🎯 [필터 최적화]: 버그가 잦은 복잡한 $and 복합 필터를 걷어내고, 
                # run_rag_build에서 성공했던 '질환명' 단일 매칭 필터로 원천 교정합니다. (카테고리는 쿼리문 내 자연어로 필터링)
                search_filter = {"질환명": db_disease}
                
                try:
                    current_food_chunks = []
                    matched_docs = self.vector_store.similarity_search(
                        query=clean_query,
                        k=self.CHUNKS_PER_DISEASE, 
                        filter=search_filter
                    )
                    
                    for doc in matched_docs:
                        chunk_format = f"• [{doc.metadata.get('카테고리', '지침')}] {doc.page_content}"
                        if chunk_format not in current_food_chunks:
                            current_food_chunks.append(chunk_format)
                    
                    if current_food_chunks:
                        food_baskets.append(current_food_chunks)
                                
                except Exception as e:
                    print(f"❌ [RAG 다중 검색 에러] {db_disease}-{food_name} 필터 검색 실패: {e}")
            
            # ====================================================================
            # 🎯 3. [다차원 라운드 로빈 스케줄링 가동]
            # ====================================================================
            combined_disease_chunks = []
            if food_baskets:
                max_chunks_in_basket = max(len(basket) for basket in food_baskets)
                for step in range(max_chunks_in_basket):
                    for basket in food_baskets:
                        if step < len(basket):
                            chunk = basket[step]
                            if chunk not in combined_disease_chunks:
                                combined_disease_chunks.append(chunk)
            
            final_disease_guidelines = combined_disease_chunks[:self.CHUNKS_PER_DISEASE]
            
            if final_disease_guidelines:
                disease_block = f"[{db_disease} 환자용 맞춤 지침]\n" + "\n".join(final_disease_guidelines)
                integrated_context_list.append(disease_block)
                
        final_rag_context = "\n\n".join(integrated_context_list)
        print(f"🎯 [RAG 쿼리 엔진] 총 {len(valid_diseases)}개 질환 및 {len(final_items)}개 음식 동적 매트릭스 인덱싱 완료!")
        return final_rag_context
    
    def retrieve_daily_accumulation_context(self, user_diseases: list, food_log: list) -> str:
        """
        📊 [전체 영양소 확장형 누적 식단 RAG 엔진]
        홈 화면 누적 리포트 분석 시 작동하는 함수입니다.
        """
        if not user_diseases or not food_log:
            return "일반 만성질환자를 위한 균형 잡힌 건강 식단 가이드라인을 기준으로 적용하세요."

        valid_diseases = [d for d in user_diseases if d not in ["정보 없음", "미등록", "일반"]]
        if not valid_diseases:
            return "일반 영양학적 건강 식단 가이드라인을 기준으로 적용하세요."

        highest_contribution_foods = set()
        for eng_key in self.nutrient_eng_to_kor.keys():
            try:
                if any(getattr(f, eng_key, 0) > 0 for f in food_log):
                    max_nutrient_food = max(food_log, key=lambda x: getattr(x, eng_key, 0))
                    highest_contribution_foods.add(max_nutrient_food.foodName)
            except AttributeError:
                continue

        bad_status_foods = [f.foodName for f in food_log if f.risk_level in ["위험", "주의"]]
        target_food_names = list(set(bad_status_foods + list(highest_contribution_foods)))
        if not target_food_names:
            target_food_names = [f.foodName for f in food_log]

        integrated_context_list = []
        dynamic_chunk_limit = max(4, min(8, len(target_food_names) * 2))

        # ====================================================================
        # 🏥 1. [질환 N개 동적 순회 및 공간 격리]
        # ====================================================================
        for disease in valid_diseases:
            db_disease = "당뇨병" if disease == "당뇨" else disease
            target_nutrients = self.disease_nutrient_map.get(db_disease, ["나트륨", "당류"])
            food_baskets = [] 
            
            # ====================================================================
            # 🍽️ 2. [선별된 표적 음식 M개 동적 순회 및 정밀 RAG 쿼리 전개]
            # ====================================================================
            for food_name in target_food_names:
                food_obj = next((f for f in food_log if f.foodName == food_name), None)
                
                matched_kor_nutrients = []
                if food_obj:
                    for eng_key, kor_key in self.nutrient_eng_to_kor.items():
                        if kor_key in target_nutrients and getattr(food_obj, eng_key, 0) > 0:
                            if kor_key not in matched_kor_nutrients:
                                matched_kor_nutrients.append(kor_key)
                
                nutrient_str = ", ".join(matched_kor_nutrients) if matched_kor_nutrients else "위험성분"

                # 🎯 [쿼리 최적화]: 인위적인 노이즈 문장을 다 걷어내고, bge-m3 모델이 가장 선호하는 시맨틱 문장 구조로 변형
                clean_query = (
                    f"{db_disease} 환자의 {food_name} 과다 섭취 시 임상 관리 지침 및 조심해야 할 {nutrient_str} 식사요법, 대체 건강식 추천 가이드"
                )
                
                # 🎯 [필터 최적화]: 주 원인이었던 복잡한 카테고리 필터를 생략하고, 직관적인 질환명 고정 필터로 전면 교체
                search_filter = {"질환명": db_disease}
                
                try:
                    current_food_chunks = []
                    matched_docs = self.vector_store.similarity_search(
                        query=clean_query,
                        k=3, 
                        filter=search_filter
                    )
                    
                    for doc in matched_docs:
                        chunk_format = f"• [{doc.metadata.get('카테고리', '지침')}] {doc.page_content}"
                        if chunk_format not in current_food_chunks:
                            current_food_chunks.append(chunk_format)
                    
                    if current_food_chunks:
                        food_baskets.append(current_food_chunks)
                                
                except Exception as e:
                    print(f"❌ [RAG 쿼리 검색 에러] {db_disease}-{food_name} 인덱싱 실패: {e}")
            
            # ====================================================================
            # 🎯 3. [다차원 라운드 로빈 스케줄링 및 최종 동적 슬라이싱]
            # ====================================================================
            combined_disease_chunks = []
            if food_baskets:
                max_chunks_in_basket = max(len(basket) for basket in food_baskets)
                for step in range(max_chunks_in_basket):
                    for basket in food_baskets:
                        if step < len(basket):
                            chunk = basket[step]
                            if chunk not in combined_disease_chunks:
                                combined_disease_chunks.append(chunk)
            
            final_disease_guidelines = combined_disease_chunks[:dynamic_chunk_limit]
            
            if final_disease_guidelines:
                disease_block = f"[{db_disease} 환자용 임상 지침]\n" + "\n".join(final_disease_guidelines)
                integrated_context_list.append(disease_block)
                
        final_rag_context = "\n\n".join(integrated_context_list)
        print(f"🎯 [RAG 완수] 전성분 확장형 4대 기준 동적 쿼리 완료 (확보 청크 수: {dynamic_chunk_limit}개)")
        return final_rag_context