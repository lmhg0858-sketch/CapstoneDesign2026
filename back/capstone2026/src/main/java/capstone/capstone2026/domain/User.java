package capstone.capstone2026.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "users")
@Getter
@NoArgsConstructor
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "user_id")
    private Long id;

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
}
