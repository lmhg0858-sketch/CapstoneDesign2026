package capstone.capstone2026.controller;

import capstone.capstone2026.dto.RankingResponse;
import capstone.capstone2026.service.RankingService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/rankings")
public class RankingController {

    private final RankingService rankingService;

    @GetMapping
    public RankingResponse getRankings() {
        return rankingService.getRankings();
    }
}