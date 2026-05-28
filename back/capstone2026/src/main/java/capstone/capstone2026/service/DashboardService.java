package capstone.capstone2026.service;

import capstone.capstone2026.domain.Meal;
import capstone.capstone2026.domain.User;
import capstone.capstone2026.dto.DashboardResponse;
import capstone.capstone2026.repository.MealRepository;
import capstone.capstone2026.repository.UserRepository;
import capstone.capstone2026.repository.UserDiseaseRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class DashboardService {

    private final MealRepository mealRepository;
    private final UserDiseaseRepository userDiseaseRepository;
    private final UserRepository userRepository;

    public DashboardResponse getDailyDashboard(String userId, LocalDate date) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 사용자입니다."));

        List<String> diseases = userDiseaseRepository.findByUser_Id(userId)
                .stream()
                .map(ud -> ud.getDisease().getName())
                .toList();

        LocalDateTime start = date.atStartOfDay();
        LocalDateTime end = date.atTime(LocalTime.MAX);
        List<Meal> dayMeals = mealRepository.findByUserIdAndEatTimeBetween(userId, start, end);

        // 영양소별 일일 권장량(Limit) 계산을 위한 맵
        Map<String, Double> recommendedLimits = calculateDailyLimits(user, diseases);

        List<DashboardResponse.CumulativeNutrient> resultList = new ArrayList<>();
        for (String key : recommendedLimits.keySet()) {
            double sum = dayMeals.stream()
                    .mapToDouble(meal -> getNutrientValueByKey(meal, key))
                    .sum();
            
            resultList.add(DashboardResponse.CumulativeNutrient.builder()
                    .nutrientKey(key)
                    .nutrientName(getKoreanName(key))
                    .cumulativeValue(sum)
                    .recommendedDailyLimit(recommendedLimits.get(key))
                    .unit(getUnit(key))
                    .build());
        }

        return DashboardResponse.builder()
                .date(date.toString())
                .userDiseases(diseases)
                .cumulativeRiskNutrients(resultList)
                .build();
    }

    // 질환별 Comparator의 기준치에 3을 곱하여 최저값(가장 엄격한 기준)을 선정
    private Map<String, Double> calculateDailyLimits(User user, List<String> diseases) {
        Map<String, Double> limits = new HashMap<>();

        for (String disease : diseases) {
            Map<String, Double> diseaseThresholds = new HashMap<>();
            
            // 각 질환별 한 끼 기준 임계치 설정 (Comparator 로직과 동일)
            switch (disease) {
                case "당뇨" -> {
                    double h = user.getHeight() / 100.0;
                    double sw = ("MALE".equalsIgnoreCase(user.getGender()) || "남성".equals(user.getGender())) ? Math.pow(h, 2) * 22 : Math.pow(h, 2) * 21;
                    diseaseThresholds.put("carbs", 1000.0); // 탄수화물/지방은 비율 기반이므로 절대 임계값은 기획에 따라 설정
                    diseaseThresholds.put("sugar", 16.0);
                    diseaseThresholds.put("kcal", (sw * 30.0) / 3.0);
                    diseaseThresholds.put("fat", 1000.0);
                }
                case "고지혈증" -> {
                    boolean isM = "MALE".equalsIgnoreCase(user.getGender()) || "남성".equals(user.getGender());
                    diseaseThresholds.put("cholesterol", 60.0);
                    diseaseThresholds.put("fat", isM ? 25.0 : 20.0);
                    diseaseThresholds.put("sodium", 600.0);
                }
                case "고혈압" -> {
                    boolean isM = "MALE".equalsIgnoreCase(user.getGender()) || "남성".equals(user.getGender());
                    diseaseThresholds.put("sodium", 666.0);
                    diseaseThresholds.put("cholesterol", 100.0);
                    diseaseThresholds.put("kcal", isM ? 800.0 : 600.0);
                }
                case "신장 질환" -> {
                    diseaseThresholds.put("sodium", 500.0); // 25 * 20
                    diseaseThresholds.put("kalium", 500.0);
                    diseaseThresholds.put("phos", 200.0); // 25 * 8
                    diseaseThresholds.put("protein", (user.getWeight() * 1.2) * 0.25);
                }
            }

            // 질환별 한 끼 임계치에 3을 곱하여 일일 권장량 산출 및 최소값(보수적) 적용
            diseaseThresholds.forEach((key, val) -> {
                double dailyVal = val * 3.0;
                limits.merge(key, dailyVal, Math::min);
            });
        }
        return limits;
    }

    private double getNutrientValueByKey(Meal meal, String key) {
        return switch (key) {
            case "kcal" -> meal.getKcal();
            case "carbs" -> meal.getCarbs();
            case "protein" -> meal.getProtein();
            case "fat" -> meal.getFat();
            case "sugar" -> meal.getSugar();
            case "sodium" -> meal.getSodium();
            case "cholesterol" -> meal.getCholesterol();
            case "kalium" -> meal.getKalium();
            case "phos" -> meal.getPhos();
            default -> 0.0;
        };
    }

    private String getKoreanName(String key) {
        return Map.of(
            "kcal", "칼로리", "carbs", "탄수화물", "protein", "단백질",
            "fat", "지방", "sugar", "당류", "sodium", "나트륨",
            "cholesterol", "콜레스테롤", "kalium", "칼륨", "phos", "인"
        ).getOrDefault(key, key);
    }

    private String getUnit(String key) {
        return switch (key) {
            case "sodium", "cholesterol", "kalium", "phos" -> "mg";
            case "kcal" -> "kcal";
            default -> "g";
        };
    }
}