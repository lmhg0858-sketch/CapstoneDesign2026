package capstone.capstone2026.service;

import capstone.capstone2026.domain.User;
import capstone.capstone2026.dto.*;
import capstone.capstone2026.service.analysis.DiseaseComparator;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.*;

@Service
@RequiredArgsConstructor
public class FoodAnalysisService {

    private final List<DiseaseComparator> comparators;

    public FoodAnalysisResponse analyzeFood(User user, List<String> userDiseases, FoodAnalysisRequest request) {
        // 1. DTO 이름 변경에 따른 리스트 변수명 수정
        List<FoodAnalysisResponse.AnalysisResult> analysisResults = new ArrayList<>();

        if (request.getDetectedFoods() == null) {
            return new FoodAnalysisResponse(userDiseases, analysisResults);
        }

        for (FoodAnalysisRequest.FoodData food : request.getDetectedFoods()) {
            String finalRisk = "안전";

            if (userDiseases != null && !userDiseases.isEmpty()) {
                for (String diseaseName : userDiseases) {
                    String currentDiseaseRisk = comparators.stream()
                            .filter(c -> c.getDiseaseName().equals(diseaseName))
                            .map(c -> c.evaluate(food.getNutrient_name(), user)) // 객체 전달
                            .findFirst()
                            .orElse("안전");

                    finalRisk = getStrictRisk(finalRisk, currentDiseaseRisk);
                }
            }

            // 2. 내부 클래스 생성자 호출 시 필드 확인
            analysisResults.add(new FoodAnalysisResponse.AnalysisResult(food.getFood_name(), finalRisk));
        }

        // 3. 최종 응답 객체 생성
        return new FoodAnalysisResponse(userDiseases, analysisResults);
    }

    private String getStrictRisk(String existingRisk, String newRisk) {
        if (existingRisk.equals("위험") || newRisk.equals("위험")) return "위험";
        if (existingRisk.equals("주의") || newRisk.equals("주의")) return "주의";
        return "안전";
    }
}

