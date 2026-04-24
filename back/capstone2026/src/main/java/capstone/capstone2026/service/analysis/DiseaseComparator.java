package capstone.capstone2026.service.analysis;

import capstone.capstone2026.domain.User;
import capstone.capstone2026.dto.FoodAnalysisRequest;

public interface DiseaseComparator {
    String getDiseaseName();
    // Request DTO 내부의 NutrientData를 인자로 받도록 수정
    String evaluate(FoodAnalysisRequest.NutrientData nutrients, User user);
}