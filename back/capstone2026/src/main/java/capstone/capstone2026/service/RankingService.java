package capstone.capstone2026.service;

import capstone.capstone2026.domain.User;
import capstone.capstone2026.domain.UserRanking;
import capstone.capstone2026.dto.RankingResponse;
import capstone.capstone2026.repository.UserRankingRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class RankingService {

    private final UserRankingRepository userRankingRepository;

    public void saveScore(User user, int score) {
        UserRanking userRanking = UserRanking.builder()
                .userId(user.getId())
                .nickname(user.getNickname())
                .score(score)
                .build();

        userRankingRepository.save(userRanking);
    }

    public RankingResponse getRankings() {
        List<UserRanking> rankings = userRankingRepository.findAll();

        Map<String, List<UserRanking>> groupedByUser = rankings.stream()
                .collect(Collectors.groupingBy(UserRanking::getUserId));

        List<RankingResponse.RankingItem> rankingItems = groupedByUser.entrySet().stream()
                .map(entry -> {
                    String userId = entry.getKey();
                    List<UserRanking> userScores = entry.getValue();

                    String nickname = userScores.get(0).getNickname();

                    double averageScore = userScores.stream()
                            .mapToInt(UserRanking::getScore)
                            .average()
                            .orElse(0.0);

                    long mealCount = userScores.size();

                    return RankingResponse.RankingItem.builder()
                            .rank(0)
                            .userId(userId)
                            .nickname(nickname)
                            .averageScore(averageScore)
                            .mealCount(mealCount)
                            .build();
                })
                .sorted(Comparator.comparingDouble(RankingResponse.RankingItem::getAverageScore).reversed())
                .toList();

        List<RankingResponse.RankingItem> result = new java.util.ArrayList<>();

        for (int i = 0; i < rankingItems.size(); i++) {
            RankingResponse.RankingItem item = rankingItems.get(i);

            result.add(RankingResponse.RankingItem.builder()
                    .rank(i + 1)
                    .userId(item.getUserId())
                    .nickname(item.getNickname())
                    .averageScore(item.getAverageScore())
                    .mealCount(item.getMealCount())
                    .build());
        }

        return RankingResponse.builder()
                .ranking(result)
                .build();
    }
}