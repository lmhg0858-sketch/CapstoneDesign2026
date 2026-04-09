package capstone.capstone2026.controller;

import capstone.capstone2026.domain.User;
import capstone.capstone2026.dto.UserJoinRequest;
import capstone.capstone2026.dto.UserJoinResponse; // 변경된 임포트
import capstone.capstone2026.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @PostMapping("/signup")
    // 반환 타입을 UserJoinResponse<String>으로 변경
    public UserJoinResponse<String> join(@RequestBody UserJoinRequest dto) {
        
        User user = User.builder()
                .id(dto.getId())
                .email(dto.getEmail())
                .password(dto.getPassword())
                .nickname(dto.getNickname())
                .age(dto.getAge())
                .gender(dto.getGender())
                .height(dto.getHeight())
                .weight(dto.getWeight())
                .build();

        String savedId = userService.join(user);
        
        // UserJoinResponse의 성공 메서드 호출
        return UserJoinResponse.success("회원가입이 완료되었습니다.", savedId);
    }
}
