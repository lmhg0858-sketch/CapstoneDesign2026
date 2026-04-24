package capstone.capstone2026.repository;

import capstone.capstone2026.domain.UserDisease;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserDiseaseRepository extends JpaRepository<UserDisease, Long> {
    // 매핑 테이블은 주로 저장을 위해 사용하므로 기본적인 메서드로 충분합니다.
}