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
        if (n.getKcal() <= 0) return "안전";

        // 표준체중 기반 한 끼 권장 칼로리 계산
        double heightInMeters = user.getHeight() / 100.0;
        double standardWeight = ("MALE".equalsIgnoreCase(user.getGender()) || "남성".equals(user.getGender())) 
                                ? Math.pow(heightInMeters, 2) * 22 : Math.pow(heightInMeters, 2) * 21;
        double mealLimit = (standardWeight * 30.0) / 3.0;

        double carbPct = (n.getCarbs() * 4 / n.getKcal()) * 100;
        double fatPct = (n.getFat() * 9 / n.getKcal()) * 100;
        double proteinPct = (n.getProtein() * 4 / n.getKcal()) * 100;

        if (carbPct < 50 || carbPct > 70 || fatPct < 10 || fatPct > 45 || proteinPct < 5 || proteinPct > 40 || n.getSugar() >= 20 || n.getSodium() >= 800 || n.getKcal() > (mealLimit + 100)) return "위험";
        if (carbPct < 55 || carbPct > 65 || fatPct < 20 || fatPct > 35 || proteinPct < 10 || proteinPct > 35 || n.getSugar() >= 16 || n.getSodium() >= 750 || n.getKcal() > mealLimit) return "주의";

        return "안전";
    }
}