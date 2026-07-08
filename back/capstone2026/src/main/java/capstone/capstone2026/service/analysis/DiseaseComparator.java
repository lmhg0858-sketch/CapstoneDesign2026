package capstone.capstone2026.service.analysis;

import capstone.capstone2026.domain.User;
import capstone.capstone2026.dto.FoodAnalysisRequest;
import capstone.capstone2026.dto.AnalysisResult;

public interface DiseaseComparator {
    String getDiseaseName();
    AnalysisResult evaluate(FoodAnalysisRequest.NutrientData n, User user);
}