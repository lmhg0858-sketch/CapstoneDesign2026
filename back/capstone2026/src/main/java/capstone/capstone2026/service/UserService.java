package capstone.capstone2026.service;

import capstone.capstone2026.domain.User;
import capstone.capstone2026.dto.LoginRequest;
import capstone.capstone2026.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public String join(User user) {
        // 1. 객체 자체가 null인지 확인 (가장 먼저 수행)
        if (user == null) {
            throw new IllegalArgumentException("저장할 사용자 정보가 없습니다.");
        }

        // 2. 사용자가 입력한 ID가 null인지 확인 (문자열 PK이므로 필수)
        if (user.getId() == null || user.getId().isEmpty()) {
            throw new IllegalArgumentException("사용자 아이디(ID)는 필수 입력 항목입니다.");
        }

        validateDuplicateUser(user);
        // 중복 검증
        User encodedUser = User.builder()
                .id(user.getId())
                .email(user.getEmail())
                .password(passwordEncoder.encode(user.getPassword())) // ⭐ 핵심
                .nickname(user.getNickname())
                .age(user.getAge())
                .gender(user.getGender())
                .height(user.getHeight())
                .weight(user.getWeight())
                .build();

        userRepository.save(encodedUser);
        return encodedUser.getId();
    }

    private void validateDuplicateUser(User user) {
        userRepository.findByEmail(user.getEmail())
                .ifPresent(m -> {
                    throw new IllegalStateException("이미 존재하는 이메일입니다.");
                });
    }

    //로그인 로직
    public User login(LoginRequest request) {
        // 1. 사용자 조회
        User user = userRepository.findById(request.getId())
                .orElseThrow(() -> new IllegalArgumentException("아이디가 존재하지 않습니다."));

        // 2. 비밀번호 비교 (핵심🔥)
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new IllegalArgumentException("비밀번호가 틀렸습니다.");
        }

        return user;
    }
}
