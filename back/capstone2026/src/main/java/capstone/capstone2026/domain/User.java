package capstone.capstone2026.domain;
import lombok.Setter;
import jakarta.persistence.*;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;
@Setter
@Entity
@Table(name = "users")
@Getter
@NoArgsConstructor
public class User {
    @Id
    @Column(name = "user_id")
    private String id;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(nullable = false)
    private String password;

    @Column(nullable = false)
    private Integer age;

    @Column(nullable = false, length = 20)
    private String gender;

    @Column(nullable = false, unique = true, length = 50)
    private String nickname;

    @Column(nullable = false)
    private Double height;

    @Column(nullable = false)
    private Double weight;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Builder
    public User(String id, String email, String password, Integer age, String gender, String nickname, Double height, Double weight) {
        this.id = id; // id를 직접 받도록 추가
        this.email = email;
        this.password = password;
        this.age = age;
        this.gender = gender;
        this.nickname = nickname;
        this.height = height;
        this.weight = weight;
    }

    @PrePersist
    public void prePersist() {
        this.createdAt = LocalDateTime.now();
    }
}