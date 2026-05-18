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
        List<FoodAnalysisResponse.AnalysisResult> analysisResults = new ArrayList<>();
        double totalSumScore = 0;

        if (request.getDetectedFoods() == null || request.getDetectedFoods().isEmpty()) {
            return new FoodAnalysisResponse(userDiseases, 0, analysisResults);
        }

        for (FoodAnalysisRequest.FoodData food : request.getDetectedFoods()) {
            double weightedSumScore = 0; // 모든 질환의 가중치 점수 합
            int diseaseCount = 0;
            String finalRisk = "안전";

            if (userDiseases != null && !userDiseases.isEmpty()) {
                for (String diseaseName : userDiseases) {
                    capstone.capstone2026.dto.AnalysisResult result = comparators.stream()
                            .filter(c -> c.getDiseaseName().equals(diseaseName))
                            .map(c -> c.evaluate(food.getNutrient_name(), user))
                            .findFirst().orElse(null);

                    if (result != null) {
                        // 각 질환별 결과 점수(가중치가 적용된 상태)를 단순 합산
                        weightedSumScore += result.getFinalScore();
                        finalRisk = getStrictRisk(finalRisk, result.getFinalStatus());
                        diseaseCount++;
                    }
                }
            }

            // 질환이 여러 개일 때 각 질환의 가중치 비율을 통합한 평균 점수 산출
            // 예: (당뇨점수 + 고지혈증점수) / 2 -> 전체 가중치 비율에 따른 평점과 수학적으로 동일
            double avgScore = (diseaseCount == 0) ? 100 : weightedSumScore / diseaseCount;
            totalSumScore += avgScore;

            analysisResults.add(new FoodAnalysisResponse.AnalysisResult(
                    food.getFood_name(),
                    finalRisk
            ));
        }

        int finalTotalScore = (int) (totalSumScore / request.getDetectedFoods().size());

        return new FoodAnalysisResponse(userDiseases, finalTotalScore, analysisResults);
    }

    private String getStrictRisk(String existingRisk, String newRisk) {
        if ("위험".equals(existingRisk) || "위험".equals(newRisk)) return "위험";
        if ("주의".equals(existingRisk) || "주의".equals(newRisk)) return "주의";
        return "안전";
    }
}