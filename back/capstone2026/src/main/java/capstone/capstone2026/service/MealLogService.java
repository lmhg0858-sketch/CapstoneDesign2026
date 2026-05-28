package capstone.capstone2026.service;

import capstone.capstone2026.domain.Meal;
import capstone.capstone2026.dto.FoodAnalysisRequest;
import capstone.capstone2026.dto.FoodAnalysisResponse;
import capstone.capstone2026.dto.MealLogResponse;
import capstone.capstone2026.repository.MealRepository;
import capstone.capstone2026.repository.UserDiseaseRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.ZoneId;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class MealLogService {

    private final MealRepository mealRepository;
    private final UserDiseaseRepository userDiseaseRepository;

    public void saveMealLogs(String userId, FoodAnalysisRequest request, FoodAnalysisResponse response) {
        if (request.getDetectedFoods() == null || request.getDetectedFoods().isEmpty()) {
            return;
        }

        Map<String, String> riskLevelMap = new HashMap<>();

        if (response.getAnalysisResults() != null) {
            for (FoodAnalysisResponse.AnalysisResult result : response.getAnalysisResults()) {
                riskLevelMap.put(result.getFoodName(), result.getRiskLevel());
            }
        }

        for (FoodAnalysisRequest.FoodData food : request.getDetectedFoods()) {
            FoodAnalysisRequest.NutrientData nutrient = food.getNutrient_name();

            String riskLevel = riskLevelMap.getOrDefault(food.getFood_name(), "안전");

            Meal meal = Meal.builder()
                    .userId(userId)
                    .foodName(food.getFood_name())
                    .riskLevel(riskLevel)
                    .eatTime(LocalDateTime.now())
                    .kcal(nutrient.getKcal())
                    .carbs(nutrient.getCarbs())
                    .protein(nutrient.getProtein())
                    .fat(nutrient.getFat())
                    .sugar(nutrient.getSugar())
                    .sodium(nutrient.getSodium())
                    .cholesterol(nutrient.getCholesterol())
                    .kalium(nutrient.getKalium())
                    .phos(nutrient.getPhos())
                    .build();

            mealRepository.save(meal);
        }
    }

    public List<Meal> getMealLogsByDate(String userId, LocalDate date) {
        LocalDateTime start = date.atStartOfDay();
        LocalDateTime end = date.atTime(LocalTime.MAX);

        return mealRepository.findByUserIdAndEatTimeBetween(userId, start, end);
    }

    public MealLogResponse getAllMealLogs(String userId) {
        List<String> userDiseases = userDiseaseRepository.findByUser_Id(userId)
                .stream()
                .map(userDisease -> userDisease.getDisease().getName())
                .toList();

        List<Meal> meals = mealRepository.findByUserIdOrderByEatTimeDesc(userId);

        MealLogResponse.DailyRisk dailyRisk = calculateDailyRisk(meals);

        List<MealLogResponse.FoodLog> foodLogs = meals.stream()
                .map(meal -> MealLogResponse.FoodLog.builder()
                        .id(meal.getId())
                        .userId(meal.getUserId())
                        .foodName(meal.getFoodName())
                        .eatTime(meal.getEatTime())
                        .kcal(meal.getKcal())
                        .carbs(meal.getCarbs())
                        .protein(meal.getProtein())
                        .fat(meal.getFat())
                        .sugar(meal.getSugar())
                        .sodium(meal.getSodium())
                        .cholesterol(meal.getCholesterol())
                        .kalium(meal.getKalium())
                        .phos(meal.getPhos())
                        .riskLevel(meal.getRiskLevel())
                        .build())
                .toList();

        return MealLogResponse.builder()
                .userDiseases(userDiseases)
                .dailyRisk(dailyRisk)
                .foodLog(foodLogs)
                .build();
    }

    private MealLogResponse.DailyRisk calculateDailyRisk(List<Meal> meals) {
        LocalDate today = LocalDate.now(ZoneId.of("Asia/Seoul"));

        List<Meal> todayMeals = meals.stream()
                .filter(meal -> meal.getEatTime() != null)
                .filter(meal -> meal.getEatTime().toLocalDate().equals(today))
                .toList();

        long totalCount = todayMeals.size();

        long dangerCount = todayMeals.stream()
                .filter(meal -> "위험".equals(meal.getRiskLevel()))
                .count();

        long cautionCount = todayMeals.stream()
                .filter(meal -> "주의".equals(meal.getRiskLevel()))
                .count();

        long safeCount = todayMeals.stream()
                .filter(meal -> "안전".equals(meal.getRiskLevel()))
                .count();

        String status;

        if (totalCount == 0) {
            status = "기록 없음";
        } else if (dangerCount >= 2) {
            status = "위험";
        } else if (dangerCount == 1 || cautionCount >= 2) {
            status = "주의";
        } else {
            status = "안전";
        }

        return MealLogResponse.DailyRisk.builder()
                .date(today.toString())
                .status(status)
                .totalCount(totalCount)
                .dangerCount(dangerCount)
                .cautionCount(cautionCount)
                .safeCount(safeCount)
                .build();
    }
}