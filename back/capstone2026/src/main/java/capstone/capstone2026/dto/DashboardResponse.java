package capstone.capstone2026.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import java.util.List;

@Getter
@AllArgsConstructor
@Builder
public class DashboardResponse {

    private String date;

    @JsonProperty("user_diseases")
    private List<String> userDiseases;

    @JsonProperty("cumulative_risk_nutrients")
    private List<CumulativeNutrient> cumulativeRiskNutrients;

    @Getter
    @AllArgsConstructor
    @Builder
    public static class CumulativeNutrient {
        @JsonProperty("nutrient_key")
        private String nutrientKey;

        @JsonProperty("nutrient_name")
        private String nutrientName;

        @JsonProperty("cumulative_value")
        private double cumulativeValue;

        // 일일 적정 섭취량 필드 추가
        @JsonProperty("recommended_daily_limit")
        private double recommendedDailyLimit;

        private String unit;
    }
}