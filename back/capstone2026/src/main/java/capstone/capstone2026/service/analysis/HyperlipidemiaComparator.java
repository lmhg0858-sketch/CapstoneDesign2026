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
        double fat = n.getFat();
        double cholesterol = n.getCholesterol();
        double sodium = n.getSodium();
        String gender = user.getGender(); // "남성" 또는 "여성" 가정

        // 1. 지방 기준 (남성: 25/50, 여성: 20/40)
        double fatDanger = gender.equals("남성") ? 50.0 : 40.0;
        double fatCaution = gender.equals("남성") ? 25.0 : 20.0;

        if (fat >= fatDanger || cholesterol >= 120 || sodium >= 1200) return "위험";
        if (fat >= fatCaution || cholesterol >= 60 || sodium >= 600) return "주의";
        
        return "안전";
    }
}