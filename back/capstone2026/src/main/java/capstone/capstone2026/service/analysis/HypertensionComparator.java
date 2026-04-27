package capstone.capstone2026.service.analysis;

import capstone.capstone2026.domain.User;
import capstone.capstone2026.dto.FoodAnalysisRequest;
import org.springframework.stereotype.Component;

@Component
public class HypertensionComparator implements DiseaseComparator {
    @Override
    public String getDiseaseName() { return "고혈압"; }

    @Override
    public String evaluate(FoodAnalysisRequest.NutrientData n, User user) {
        boolean isMale = "MALE".equalsIgnoreCase(user.getGender()) || "남성".equals(user.getGender());
        double kcalDanger = isMale ? 1200.0 : 900.0;
        double kcalCaution = isMale ? 800.0 : 600.0;

        if (n.getSodium() >= 1000 || n.getCholesterol() >= 150 || n.getKcal() >= kcalDanger) return "위험";
        if (n.getSodium() >= 666 || n.getCholesterol() >= 100 || n.getKcal() >= kcalCaution) return "주의";

        return "안전";
    }
}