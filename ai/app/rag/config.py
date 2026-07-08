import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CSV_PATH = os.path.join(BASE_DIR, "storage", "RAG_20260528.csv")
CHROMA_DB_DIR = os.path.join(BASE_DIR, "storage", "chroma_db")

# 🎯 허깅페이스 오픈소스 임베딩 모델로 변경 (한국어/다국어 성능 최상위권 모델)
EMBEDDING_MODEL = "BAAI/bge-m3"