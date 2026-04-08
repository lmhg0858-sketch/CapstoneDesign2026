package capstone.capstone2026.controller;

import capstone.capstone2026.domain.User;
import capstone.capstone2026.dto.UserJoinRequest;
import capstone.capstone2026.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @PostMapping("/join")
    public String join(@RequestBody UserJoinRequest dto) {
        // DTO를 엔티티로 변환 (아까 User.java에 만든 Builder 사용)
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

        userService.join(user);
        return "회원가입이 완료되었습니다.";
    }

    // 로그인 컨트롤러 구현 
}
