package capstone.capstone2026.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;
import java.util.List;

@Getter
@AllArgsConstructor
@Builder
public class MealLogResponse {

    @JsonProperty("user_diseases")
    private List<String> userDiseases;

    @JsonProperty("daily_risk")
    private DailyRisk dailyRisk;

    @JsonProperty("food_log")
    private List<FoodLog> foodLog;

    @Getter
    @AllArgsConstructor
    @Builder
    public static class DailyRisk {

        private String date;

        private String status;

        @JsonProperty("total_count")
        private long totalCount;

        @JsonProperty("danger_count")
        private long dangerCount;

        @JsonProperty("caution_count")
        private long cautionCount;

        @JsonProperty("safe_count")
        private long safeCount;
    }

    @Getter
    @AllArgsConstructor
    @Builder
    public static class FoodLog {
        private Long id;
        private String userId;
        private String foodName;
        private LocalDateTime eatTime;

        private double kcal;
        private double carbs;
        private double protein;
        private double fat;
        private double sugar;
        private double sodium;
        private double cholesterol;
        private double kalium;
        private double phos;

        @JsonProperty("risk_level")
        private String riskLevel;
    }
}