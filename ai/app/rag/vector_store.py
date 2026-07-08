import os
import pandas as pd
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from app.rag.config import CSV_PATH, CHROMA_DB_DIR, EMBEDDING_MODEL

def get_or_create_vector_store():
    """
    허깅페이스 오픈소스 모델을 활용하여 로컬 디스크 기반의 가볍고 성능 좋은 벡터 저장소를 빌드합니다.
    """
    # 🎯 오픈소스 허깅페이스 임베딩 모델 초기화 (로컬 CPU/GPU 환경에서 작동)
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'}, # GPU가 없다면 cpu, cuda가 있다면 'cuda'로 설정
        encode_kwargs={'normalize_embeddings': True} # 유사도 정밀 비교를 위해 정규화 활성화
    )
    
    # 1. 로컬 디스크 캐시 검사
    if os.path.exists(CHROMA_DB_DIR) and os.listdir(CHROMA_DB_DIR):
        print(f"📦 [RAG 인프라] 로컬 오픈소스 벡터 DB({EMBEDDING_MODEL})를 성공적으로 로드했습니다. (비용 0원)")
        return Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)
    
    # 2. 물리 데이터 유효성 검사
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"❌ RAG 빌드 실패: 원천 데이터 소스 '{CSV_PATH}' 파일이 존재하지 않습니다.")
        
    print(f"⚙️ [RAG 인프라] 최초 구동: 오픈소스 {EMBEDDING_MODEL} 기반 벡터 인덱싱을 가동합니다...")
    df = pd.read_csv(CSV_PATH)
    documents = []
    
    # 3. 문서 파싱 및 Document 객체화
    for index, row in df.iterrows():
        doc = Document(
            page_content=str(row["텍스트"]).strip(),
            metadata={
                "질환명": str(row["질환명"]).strip(), 
                "카테고리": str(row["카테고리"]).strip()
            }
        )
        documents.append(doc)
        
    # 4. Chroma 로컬 디스크 빌드 및 저장
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR
    )
    
    print(f"🎯 [RAG 인프라] 총 {len(documents)}개 청크가 오픈소스 모델을 통해 로컬 벡터로 임베딩되었습니다.")
    return vector_store