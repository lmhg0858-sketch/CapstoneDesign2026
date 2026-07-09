# CapstoneDesign2026

## 프로젝트 소개

**CapstoneDesign2026**은 만성질환자를 위한 식단 관리 서비스입니다.

사용자가 음식 사진을 업로드하면 AI가 음식과 영양 정보를 분석하고, 사용자의 질환 정보를 바탕으로 해당 식사의 위험도를 판단합니다.  
이를 통해 당뇨, 고혈압, 고지혈증, 신장질환 등 만성질환을 가진 사용자가 자신의 식습관을 더 쉽게 관리할 수 있도록 돕는 것을 목표로 합니다.
<img width="853" height="485" alt="image" src="https://github.com/user-attachments/assets/e0c2348c-41c1-443a-9514-9413b7040518" />

## 주요 기능

### 1. 음식 사진 기반 영양 정보 분석
- 사용자가 음식 이미지를 업로드하면 AI 서버에서 음식 정보를 분석합니다.
- 분석된 음식의 칼로리, 탄수화물, 단백질, 지방, 당류, 나트륨 등의 영양 정보를 제공합니다.
<img width="454" height="485" alt="image" src="https://github.com/user-attachments/assets/b594b4e5-bdd4-4822-a420-56fa69271a8c" />
<img width="421" height="335" alt="image" src="https://github.com/user-attachments/assets/58dc8451-e857-40ed-b793-171dd3ccb922" />

### 2. 사용자 질환 기반 위험도 판단
- 사용자가 보유한 질환 정보를 기준으로 음식의 위험도를 평가합니다.
- 위험도는 `안전`, `주의`, `위험` 단계로 구분됩니다.
- 복합 질환을 가진 사용자도 고려하여 식단 위험도를 계산합니다.

### 3. 식사 기록 저장 및 조회
- 분석된 식사 결과를 저장할 수 있습니다.
- 날짜별 식사 기록과 전체 식사 기록을 조회할 수 있습니다.

### 4. 하루 위험도 요약
- 오늘 섭취한 음식 기록을 바탕으로 하루 식단의 위험도를 요약합니다.
- 위험 음식과 주의 음식 개수를 기준으로 현재 식단 상태를 확인할 수 있습니다.

### 5. 대시보드 제공
- 사용자의 누적 영양 섭취량을 확인할 수 있습니다.
- 질환별 권장 기준과 비교하여 식단 관리에 도움을 줍니다.

### 6. 랭킹 기능
- 사용자별 식단 점수를 기반으로 랭킹을 제공합니다.
- 건강한 식습관 관리를 위한 동기부여 요소로 활용됩니다.

## 기술 스택

### Frontend
- React
- JavaScript
- CSS

### Backend
- Java
- Spring Boot
- Spring Data JPA
- MySQL

### AI Server
- Python
- FastAPI
- GPT API
- Chroma DB
- BGE-M3 Embedding
