package capstone.capstone2026.repository;

import capstone.capstone2026.domain.UserRanking;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRankingRepository extends JpaRepository<UserRanking, Long> {
}