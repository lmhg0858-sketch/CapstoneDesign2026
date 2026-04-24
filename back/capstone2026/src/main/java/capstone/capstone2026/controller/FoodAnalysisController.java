package capstone.capstone2026.controller;

import capstone.capstone2026.domain.User;
import capstone.capstone2026.dto.FoodAnalysisRequest;
import capstone.capstone2026.dto.FoodAnalysisResponse;
import capstone.capstone2026.service.FoodAnalysisService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Arrays;
import java.util.List;

@RestController
@RequestMapping("/api/meals") // Postman에서 호출할 주소: /api/food/analyze
@RequiredArgsConstructor
public class FoodAnalysisController {

    private final FoodAnalysisService foodAnalysisService;

    @PostMapping("/analyze")
    public FoodAnalysisResponse analyze(@RequestBody FoodAnalysisRequest request) {
        // [테스트용] 실제 로그인 기능 연결 전까지 사용할 가짜 유저 데이터
        User mockUser = new User();
        mockUser.setHeight(70.0); // 단백질 계산용 (체중 필드 대신 사용 중인 경우)
        mockUser.setGender("남성");
        
        // [테스트용] 이 유저가 가졌다고 가정할 질병 리스트
        List<String> mockDiseases = Arrays.asList("당뇨", "고혈압", "신장질환"); 

        return foodAnalysisService.analyzeFood(mockUser, mockDiseases, request);
    }
}