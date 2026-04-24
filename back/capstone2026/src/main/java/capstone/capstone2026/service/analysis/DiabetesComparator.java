package capstone.capstone2026.service.analysis;

import capstone.capstone2026.domain.User;
import capstone.capstone2026.dto.FoodAnalysisRequest;
import org.springframework.stereotype.Component;

@Component
public class DiabetesComparator implements DiseaseComparator {
    @Override
    public String getDiseaseName() { return "당뇨"; }

    @Override
    public String evaluate(FoodAnalysisRequest.NutrientData n, User user) {
        double kcal = n.getKcal();
        if (kcal <= 0) return "안전"; // 계산 불가 시 안전

        // 탄단지 비율 계산 (%)
        double carbPct = (n.getCarbs() * 4 / kcal) * 100;
        double fatPct = (n.getFat() * 9 / kcal) * 100;
        double proteinPct = (n.getProtein() * 4 / kcal) * 100;

        // 적정 칼로리 기준 (유저 정보 기반 계산 - 예시로 2100kcal의 1/3인 700kcal 가정)
        // 실제로는 user.getStandardKcal() / 3 등으로 계산하세요.
        double mealLimit = 700.0; 

        // 1. 위험 (하나라도 해당 시)
        if (carbPct < 50 || carbPct > 70 || fatPct < 10 || fatPct > 45 || 
            proteinPct < 5 || proteinPct > 40 || n.getSugar() >= 20 || 
            n.getSodium() >= 800 || kcal > (mealLimit + 100)) return "위험";

        // 2. 주의
        if (carbPct < 55 || carbPct > 65 || fatPct < 20 || fatPct > 35 || 
            proteinPct < 10 || proteinPct > 35 || n.getSugar() >= 16 || 
            n.getSodium() >= 750 || kcal > mealLimit) return "주의";

        return "안전";
    }
}