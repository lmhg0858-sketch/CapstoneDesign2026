# ai/run_rag_build.py 위치에 생성해주세요.
import os
import sys

# 프로젝트 루트 경로를 파이썬 패스에 강제 주입하여 모듈 인식 오류 방지
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag.vector_store import get_or_create_vector_store
from app.rag.config import CHROMA_DB_DIR

def run_pipeline_test():
    print("=" * 60)
    print("🚀 [RAG 엔진 실행] 로컬 오픈소스 벡터 DB 빌드 및 파이프라인 검증")
    print("=" * 60)
    
    try:
        # 1. vector_store 실행 (최초 실행 시 모델 다운로드 및 CSV 인덱싱 자동 가동)
        print("💡 1단계: 임베딩 모델 로드 및 벡터 DB 초기화 중...")
        store = get_or_create_vector_store()
        
        # 2. 물리적 디스크 폴더 생성 여부 검증
        if os.path.exists(CHROMA_DB_DIR):
            print(f"📂 2단계: 로컬 저장소 생성 확인 완료! ➔ {CHROMA_DB_DIR}")
        else:
            print("❌ 오류: 벡터 DB 폴더가 디스크에 생성되지 않았습니다.")
            return

        # 3. 실전 유사도 검색 시뮬레이션 (검색어 쿼리)
        print("\n" + "-"*40)
        print("🔍 3단계: 실전 쿼리 유사도 검색(Similarity Search) 테스트")
        print("-" * 40)
        
        # 가상의 유저 식단 로그 및 기저질환 세팅
        test_disease = "고혈압"
        test_query = "공복 상태인데 배고파서 흰쌀밥 두 공기 먹었어. 괜찮을까?"
        
        print(f"👤 유저 기저질환: {test_disease}")
        print(f"🍽️ 입력된 푸드 로그: '{test_query}'")
        print("👉 메타데이터 필터 바인딩 후 검색 실행...")
        
        # 민혁님이 설계한 메타데이터 필터링 적용 (타 질환 간섭 완벽 차단)
        results = store.similarity_search(
            query=test_query, 
            k=1, 
            filter={"질환명": test_disease}
        )
        
        # 4. 결과 출력 및 정합성 검증
        if results:
            print("\n🎯 [검색 성공] 벡터 DB가 최적의 컨텍스트를 회수했습니다!")
            print("=" * 60)
            print(f"🏷️ 검색된 매칭 질환: {results[0].metadata['질환명']}")
            print(f"🗂️ 매칭 카테고리 : {results[0].metadata['카테고리']}")
            print(f"📄 회수된 지침 청크 내용:\n\n{results[0].page_content}")
            print("=" * 60)
            print("\n✅ RAG 인프라 레이어가 완벽하게 구축되었습니다. 다음 단계(서비스 연동) 진행 가능!")
        else:
            print("⚠️ 경고: 시스템은 정상 작동했으나 일치하는 컨텍스트를 회수하지 못했습니다.")
            print("CSV 파일의 '질환명' 컬럼에 '당뇨병'이 정확히 등록되어 있는지 확인해주세요.")
            
    except Exception as e:
        print(f"\n❌ [RAG 파이프라인 에러] 구동 중 예외가 발생했습니다.")
        print(f"🚨 에러 원인: {e}")
        print("팁: 'pip install sentence-transformers'가 설치되었는지 확인해보세요.")
    
    print("=" * 60)

if __name__ == "__main__":
    run_pipeline_test()