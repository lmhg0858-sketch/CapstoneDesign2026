import httpx
import json

# AI 서버 주소
SERVER_URL = "http://127.0.0.1:8000/api/meals/recom?userId=test1"

def run_daily_recom_test():
    print("=" * 60)
    print("📡 [홈화면 누적 식단 & 3가지 추천 API 통합 테스트]")
    print("=" * 60)
    
    print("🚀 AI 서버 엔드포인트로 GET 요청을 발사합니다...")
    
    try:
        with httpx.Client(timeout=30.0) as client:
            # 🎯 주소창에 치는 것처럼 GET 요청을 날립니다.
            response = client.get(SERVER_URL)
            
        if response.status_code == 200:
            result = response.json()
            print("\n🎯 [통신 성공] 프론트엔드가 홈 화면에서 수신할 최종 JSON 데이터 구조:")
            print("-" * 60)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("-" * 60)
            
            # 추천 개수 검증 체크
            recom_list = result.get("day_recom", [])
            print(f"✅ 명세 검증: 추천된 음식 개수 ➔ {len(recom_list)}개")
            if len(recom_list) == 3:
                print("🎉 성공: 정확히 3가지 음식을 우리 DB 명칭 기반으로 추천했습니다!")
            else:
                print("❌ 에러: 추천된 음식 개수가 3개가 아닙니다.")
                
        else:
            print(f"❌ AI 서버 응답 실패 (HTTP 상태 코드: {response.status_code})")
            print(f"🚨 에러 내용: {response.text}")
            
    except httpx.ConnectError:
        print("❌ 연결 에러: FastAPI AI 서버가 켜져 있지 않습니다!")
        print("💡 해결책: 새 터미널을 열고 'python main.py'를 실행해 서버를 먼저 켜주세요.")
    except Exception as e:
        print(f"❌ 테스트 중 예외 발생: {e}")
        
    print("=" * 60)

if __name__ == "__main__":
    run_daily_recom_test()