package capstone.capstone2026.service;

import capstone.capstone2026.domain.Meal;
import capstone.capstone2026.dto.FoodAnalysisRequest;
import capstone.capstone2026.repository.MealRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class MealLogService {

    private final MealRepository mealRepository;

    public void saveMealLogs(String userId, FoodAnalysisRequest request) {
        if (request.getDetectedFoods() == null || request.getDetectedFoods().isEmpty()) {
            return;
        }

        for (FoodAnalysisRequest.FoodData food : request.getDetectedFoods()) {
            FoodAnalysisRequest.NutrientData nutrient = food.getNutrient_name();

            Meal meal = Meal.builder()
                    .userId(userId)
                    .foodName(food.getFood_name())
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
}