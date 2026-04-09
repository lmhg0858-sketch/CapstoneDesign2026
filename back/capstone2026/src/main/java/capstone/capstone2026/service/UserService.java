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
        // 1. 객체 자체가 null인지 확인
        if (user == null) {
            throw new IllegalArgumentException("저장할 사용자 정보가 없습니다.");
        }

        // 2. 사용자가 입력한 ID가 null인지 확인
        if (user.getId() == null || user.getId().isEmpty()) {
            throw new IllegalArgumentException("사용자 아이디(ID)는 필수 입력 항목입니다.");
        }

        validateDuplicateUser(user); // 중복 검증 호출
        userRepository.save(user);
        return user.getId();
    }

    private void validateDuplicateUser(User user) {
    // 1. 아이디 중복 확인 (경고 발생 지점)
    // user.getId()를 변수에 담아서 null이 아님을 확실히 하거나, Optional을 더 안전하게 씁니다.
    String userId = user.getId();
    if (userId != null) {
        userRepository.findById(userId)
                .ifPresent(m -> {
                    throw new IllegalStateException("이미 존재하는 아이디입니다.");
                });
    }

    // 2. 이메일 중복 확인
    userRepository.findByEmail(user.getEmail())
            .ifPresent(m -> {
                throw new IllegalStateException("이미 존재하는 이메일입니다.");
            });

    // 3. 닉네임 중복 확인
    userRepository.findByNickname(user.getNickname())
            .ifPresent(m -> {
                throw new IllegalStateException("이미 존재하는 닉네임입니다.");
            });
    }

    // 로그인 로직
}