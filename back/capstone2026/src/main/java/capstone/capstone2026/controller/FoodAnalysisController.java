package capstone.capstone2026.controller;

import capstone.capstone2026.domain.Meal;
import capstone.capstone2026.domain.User;
import capstone.capstone2026.dto.DashboardResponse;
import capstone.capstone2026.dto.FoodAnalysisRequest;
import capstone.capstone2026.dto.FoodAnalysisResponse;
import capstone.capstone2026.repository.UserDiseaseRepository;
import capstone.capstone2026.repository.UserRepository;
import capstone.capstone2026.service.DashboardService;
import capstone.capstone2026.service.FoodAnalysisService;
import capstone.capstone2026.service.MealLogService;
import lombok.RequiredArgsConstructor;

import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;

@RestController
@RequestMapping("/api/meals") // Postman에서 호출할 주소: /api/food/analyze
@RequiredArgsConstructor
public class FoodAnalysisController {

    private final FoodAnalysisService foodAnalysisService;
    private final UserRepository userRepository;
    private final UserDiseaseRepository userDiseaseRepository;
    private final DashboardService dashboardService;
    private final MealLogService mealLogService;

    @PostMapping("/analyze")
    public FoodAnalysisResponse analyze(
            @RequestParam String userId,
            @RequestBody FoodAnalysisRequest request
    ) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 사용자입니다."));

        List<String> userDiseases = userDiseaseRepository.findByUser_Id(userId)
                .stream()
                .map(userDisease -> userDisease.getDisease().getName())
                .toList();

        mealLogService.saveMealLogs(userId, request);

        return foodAnalysisService.analyzeFood(user, userDiseases, request);
    }
    
    @GetMapping("/dashboard")
    public DashboardResponse getDashboard(
            @RequestParam String userId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date
    ) {
        return dashboardService.getDailyDashboard(userId, date);
    }

    @GetMapping("/logs")
    public List<Meal> getMealLogs(
            @RequestParam String userId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date
    ) {
        return mealLogService.getMealLogsByDate(userId, date);
    }
}