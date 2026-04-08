package capstone.capstone2026.repository;

import capstone.capstone2026.domain.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, String> {
    Optional<User> findByEmail(String email); //이메일 중복 체크
    Optional<User> findByNickname(String nickname); //닉네임 중복 체크
}
