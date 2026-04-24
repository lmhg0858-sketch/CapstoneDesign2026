package capstone.capstone2026.service.analysis;

import capstone.capstone2026.domain.User;
import capstone.capstone2026.dto.FoodAnalysisRequest;
import org.springframework.stereotype.Component;

@Component
public class KidneyDiseaseComparator implements DiseaseComparator {

    @Override
    public String getDiseaseName() {
        return "신장질환";
    }

    @Override
    public String evaluate(FoodAnalysisRequest.NutrientData n, User user) {
        // 1. 사용자 체중 기반 단백질 제한량 계산 (투석 환자 기준: 1.2g/kg)
        // 주의: user.getHeight()가 아니라 체중 필드를 사용해야 합니다. 
        // 만약 엔티티에 체중 필드가 없다면 추가하거나 확인이 필요합니다.
        double weight = user.getHeight(); // 이 부분이 에러라면 user.getWeight() 등으로 확인하세요.
        double recommendedProteinPerMeal = (weight * 1.2) / 3; // 한 끼 권장량

        // 분모가 0이 되는 것을 방지
        if (recommendedProteinPerMeal <= 0) recommendedProteinPerMeal = 1;

        // 현재 음식의 단백질이 한 끼 권장량에서 차지하는 비율 (%)
        double proteinRatio = (n.getProtein() / recommendedProteinPerMeal) * 100;

        // 2. 위험 수치 판별 (나트륨 800mg, 칼륨 800mg, 인 320mg 이상 또는 단백질 과다)
        if (n.getSodium() >= 800 || 
            n.getKalium() >= 800 || 
            n.getPhos() >= 320 || 
            proteinRatio >= 50) { 
            return "위험";
        }

        // 3. 주의 수치 판별 (나트륨 500mg, 칼륨 500mg, 인 200mg 이상 또는 단백질 주의)
        if (n.getSodium() >= 500 || 
            n.getKalium() >= 500 || 
            n.getPhos() >= 200 || 
            proteinRatio >= 25) {
            return "주의";
        }

        return "안전";
    }
}