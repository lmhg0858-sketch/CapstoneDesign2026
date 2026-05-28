package capstone.capstone2026.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

import java.util.List;

@Getter
@AllArgsConstructor
@Builder
public class RankingResponse {

    private List<RankingItem> ranking;

    @Getter
    @AllArgsConstructor
    @Builder
    public static class RankingItem {
        private int rank;
        private String userId;
        private String nickname;
        private double averageScore;
        private long mealCount;
    }
}