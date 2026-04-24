package capstone.capstone2026.domain;

import jakarta.persistence.*;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Entity
@Table(name = "user_diseases")
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserDisease {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id") // User 테이블의 PK와 연결
    private User user;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "disease_id") // Disease 테이블의 PK와 연결
    private Disease disease;

    // 생성자 (빌더를 사용하지 않을 경우를 대비)
    public UserDisease(User user, Disease disease) {
        this.user = user;
        this.disease = disease;
    }
}