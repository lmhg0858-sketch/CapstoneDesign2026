package capstone.capstone2026.service.analysis;

import capstone.capstone2026.domain.User;
import capstone.capstone2026.dto.FoodAnalysisRequest;
import org.springframework.stereotype.Component;

@Component
public class HyperlipidemiaComparator implements DiseaseComparator {
    @Override
    public String getDiseaseName() { return "고지혈증"; }

    @Override
    public String evaluate(FoodAnalysisRequest.NutrientData n, User user) {
        boolean isMale = "MALE".equalsIgnoreCase(user.getGender()) || "남성".equals(user.getGender());
        double fatDanger = isMale ? 50.0 : 40.0;
        double fatCaution = isMale ? 25.0 : 20.0;

        if (n.getFat() >= fatDanger || n.getCholesterol() >= 120 || n.getSodium() >= 1200) return "위험";
        if (n.getFat() >= fatCaution || n.getCholesterol() >= 60 || n.getSodium() >= 600) return "주의";

        return "안전";
    }
}