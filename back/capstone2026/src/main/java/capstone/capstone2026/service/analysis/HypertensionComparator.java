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
        double sodium = n.getSodium();
        double chol = n.getCholesterol();
        double kcal = n.getKcal();
        String gender = user.getGender();

        double kcalDanger = gender.equals("남성") ? 1200 : 900;
        double kcalCaution = gender.equals("남성") ? 800 : 600;

        if (sodium >= 1000 || chol >= 150 || kcal >= kcalDanger) return "위험";
        if (sodium >= 666 || chol >= 100 || kcal >= kcalCaution) return "주의";

        return "안전";
    }
}