# ai/test_api_call.py 위치의 코드를 아래 내용으로 수정해주세요.
import base64
import httpx
import json
import os

# 🎯 [변경 포인트] 이미지 파일이 스토리지 폴더 안에 있으므로 경로를 결합합니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(BASE_DIR, "storage")

# 📸 스토리지 폴더 안에 넣어둔 실제 테스트용 파일명으로 적어주세요! (예: "chigen.jpg", "test_food.png" 등)
IMAGE_NAME = "test_food_2.jpg" 
FULL_IMAGE_PATH = os.path.join(IMAGE_FOLDER, IMAGE_NAME)

SERVER_URL = "http://127.0.0.1:8000/api/meals/analyze"

def run_api_integration_test():
    print("=" * 60)
    print("📡 [API 통합 테스트] 스토리지 내 이미지 ➔ 백엔드 모크 ➔ RAG ➔ 최종 검증")
    print("=" * 60)
    
    # 물리적 경로 유효성 검사
    if not os.path.exists(FULL_IMAGE_PATH):
        print(f"❌ 에러: '{FULL_IMAGE_PATH}' 경로에 파일이 존재하지 않습니다.")
        print(f"💡 해결책: 'ai/storage/' 폴더 안에 '{IMAGE_NAME}' 파일이 실제로 있는지 확인해주세요!")
        return

    # 1. storage/ 폴더 내 이미지 로드 및 Base64 인코딩
    print(f"📸 1. [storage/]에서 이미지 로드 중...: {IMAGE_NAME}")
    with open(FULL_IMAGE_PATH, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    
    payload = {
        "image_base64": encoded_string
    }
    
    # 2. FastAPI 로컬 서버로 분석 요청 송신
    print(f"🚀 2. AI 서버 엔드포인트({SERVER_URL})로 HTTP POST 요청 발사...")
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(SERVER_URL, json=payload)
            
        # 3. 반환된 최종 JSON 결과 분석
        if response.status_code == 200:
            result = response.json()
            print("\n🎯 [통신 성공] 프론트엔드가 수신할 최종 데이터 구조 확인:")
            print("-" * 60)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("-" * 60)
            
            # score 명세 검증 체크
            data_scope = result.get("data", {})
            if "score" in data_scope:
                print(f"✅ 명세 검증 성공: 'data.score' ({data_scope['score']}점)가 정확하게 탑재되었습니다.")
            else:
                print("❌ 명세 오류: 응답 구조 내에 'score' 필드가 누락되었습니다.")
                
        else:
            print(f"❌ 서버 응답 실패 (HTTP 상태 코드: {response.status_code})")
            print(f"🚨 에러 내용: {response.text}")
            
    except httpx.ConnectError:
        print("❌ 연결 에러: FastAPI AI 서버가 켜져 있지 않습니다!")
        print("💡 해결책: 새 터미널을 열고 'python main.py'를 실행해 서버를 먼저 켜주세요.")
    except Exception as e:
        print(f"❌ 테스트 중 예외 발생: {e}")
        
    print("=" * 60)

if __name__ == "__main__":
    run_api_integration_test()