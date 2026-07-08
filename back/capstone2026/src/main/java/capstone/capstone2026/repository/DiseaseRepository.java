package capstone.capstone2026.repository;

import capstone.capstone2026.domain.Disease;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface DiseaseRepository extends JpaRepository<Disease, Long> {
    // 질병 이름(예: "당뇨")으로 질병 정보를 조회하기 위한 메서드
    Optional<Disease> findByName(String name);
}