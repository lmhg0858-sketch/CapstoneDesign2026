package capstone.capstone2026.service;

import capstone.capstone2026.domain.*;
import capstone.capstone2026.dto.LoginRequest;
import capstone.capstone2026.dto.UserJoinRequest; // DTO 추가
import capstone.capstone2026.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final DiseaseRepository diseaseRepository; // 추가
    private final UserDiseaseRepository userDiseaseRepository; // 추가
    private final PasswordEncoder passwordEncoder;

    public String join(UserJoinRequest request) { // User 대신 UserJoinRequest를 받음
        if (request == null) {
            throw new IllegalArgumentException("저장할 사용자 정보가 없습니다.");
        }

        if (request.getId() == null || request.getId().isEmpty()) {
            throw new IllegalArgumentException("사용자 아이디(ID)는 필수 입력 항목입니다.");
        }

        // 중복 검증 로직 수정 (Request DTO 기반으로 검증)
        validateDuplicateUser(request);

        // 1. 유저 정보 생성 및 저장
        User encodedUser = User.builder()
                .id(request.getId())
                .email(request.getEmail())
                .password(passwordEncoder.encode(request.getPassword()))
                .nickname(request.getNickname())
                .age(request.getAge())
                .gender(request.getGender())
                .height(request.getHeight())
                .weight(request.getWeight())
                .build();

        userRepository.save(encodedUser);

        // 2. 질병 정보 저장 (프론트에서 보낸 'desease' 리스트 처리)
        if (request.getDesease() != null) {
            for (String diseaseValue : request.getDesease()) {
                String korName = mapDiseaseName(diseaseValue); // 영문 value를 한글로 변환

                // 질병 마스터 테이블에서 조회 (없으면 생성)
                Disease disease = diseaseRepository.findByName(korName)
                        .orElseGet(() -> diseaseRepository.save(new Disease(korName)));

                // 매핑 테이블 저장
                UserDisease userDisease = UserDisease.builder()
                        .user(encodedUser)
                        .disease(disease)
                        .build();
                userDiseaseRepository.save(userDisease);
            }
        }

        return encodedUser.getId();
    }

    private void validateDuplicateUser(UserJoinRequest request) {
        userRepository.findById(request.getId())
                .ifPresent(m -> { throw new IllegalStateException("이미 존재하는 아이디입니다."); });

        userRepository.findByEmail(request.getEmail())
                .ifPresent(m -> { throw new IllegalStateException("이미 존재하는 이메일입니다."); });

        userRepository.findByNickname(request.getNickname())
                .ifPresent(m -> { throw new IllegalStateException("이미 존재하는 닉네임입니다."); });
    }

    // 프론트 영문 value를 DB용 한글 명칭으로 변환
    private String mapDiseaseName(String value) {
        return switch (value) {
            case "HYPERTENSION" -> "고혈압";
            case "HYPERLIPIDEMIA" -> "고지혈증";
            case "DIABETES" -> "당뇨";
            case "KIDNEY_DISEASE" -> "신장질환";
            default -> value;
        };
    }

    public User login(LoginRequest request) {
        User user = userRepository.findById(request.getId())
                .orElseThrow(() -> new IllegalArgumentException("아이디가 존재하지 않습니다."));

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new IllegalArgumentException("비밀번호가 틀렸습니다.");
        }

        return user;
    }
}