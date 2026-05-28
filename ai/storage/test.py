import base64

# 이미지 파일 경로 (storage 폴더 안의 테스트 이미지 활용) [cite: 6]
file_path = "test_food_2.jpg"

try:
    with open(file_path, "rb") as image_file:
        # 파일을 읽어서 base64로 인코딩 [cite: 29]
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        full_base64 = f"data:image/jpg;base64,{encoded_string}"
        
        # 결과를 텍스트 파일로 저장 (CMD에서 안 잘리게!)
        with open("base64_result_2.txt", "w") as f:
            f.write(full_base64)
            
    print("✅ 변환 성공! 'base64_result_2.txt' 파일을 열어서 전체 복사하세요.")
except FileNotFoundError:
    print("❌ 파일을 찾을 수 없습니다. 경로를 확인해주세요.")