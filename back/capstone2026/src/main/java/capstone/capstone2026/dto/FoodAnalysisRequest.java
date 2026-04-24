package capstone.capstone2026.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;
import java.util.List;

@Getter
@NoArgsConstructor
public class FoodAnalysisRequest {
    private List<FoodData> detectedFoods;

    @Getter
    @NoArgsConstructor
    public static class FoodData {
        private String food_name;
        private NutrientData nutrient_name; // JSON의 객체 구조와 매핑
    }

    @Getter
    @NoArgsConstructor
    public static class NutrientData {
        private double kcal;
        private double carbs;
        private double protein;
        private double fat;
        private double sugar;
        private double sodium;
        private double cholesterol;
        private double kalium;
        private double phos;
    }
}