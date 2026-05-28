package capstone.capstone2026.domain;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Meal {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String userId; // 또는 User 엔티티와의 연관관계

    private String foodName; // 음식 이름

    private String riskLevel;

    private LocalDateTime eatTime; // 섭취 시간

    // 영양소 데이터
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

//철원이가 수정해야하는부분