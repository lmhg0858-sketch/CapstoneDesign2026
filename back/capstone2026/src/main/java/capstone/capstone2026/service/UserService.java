package capstone.capstone2026.service;

import capstone.capstone2026.domain.User;
import capstone.capstone2026.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;

    public String join(User user) {
        // 1. 객체 자체가 null인지 확인 (가장 먼저 수행)
        if (user == null) {
            throw new IllegalArgumentException("저장할 사용자 정보가 없습니다.");
        }

        // 2. 사용자가 입력한 ID가 null인지 확인 (문자열 PK이므로 필수)
        if (user.getId() == null || user.getId().isEmpty()) {
            throw new IllegalArgumentException("사용자 아이디(ID)는 필수 입력 항목입니다.");
        }

        validateDuplicateUser(user); // 중복 검증
        userRepository.save(user);
        return user.getId();
    }

    private void validateDuplicateUser(User user) {
        userRepository.findByEmail(user.getEmail())
                .ifPresent(m -> {
                    throw new IllegalStateException("이미 존재하는 이메일입니다.");
                });
    }

    //로그인 로직 
}
