package capstone.capstone2026.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Getter;
import java.util.List;

@Getter
@AllArgsConstructor
public class FoodAnalysisResponse {

    @JsonProperty("user_diseases")
    private List<String> userDiseases;

    @JsonProperty("score")
    private int score;

    @JsonProperty("analysis_results")
    private List<AnalysisResult> analysisResults;

    @Getter
    @AllArgsConstructor
    public static class AnalysisResult {
        @JsonProperty("food_name")
        private String foodName;

        @JsonProperty("risk_level")
        private String riskLevel;
    }
}