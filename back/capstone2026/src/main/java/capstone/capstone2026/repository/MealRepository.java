package capstone.capstone2026.repository;

import capstone.capstone2026.domain.Meal;
import org.springframework.data.jpa.repository.JpaRepository;
import java.time.LocalDateTime;
import java.util.List;

public interface MealRepository extends JpaRepository<Meal, Long> {
    // 특정 사용자의 특정 기간(오늘 00시 ~ 23시 59분) 데이터를 가져오는 메서드
    List<Meal> findByUserIdAndEatTimeBetween(String userId, LocalDateTime start, LocalDateTime end);
}