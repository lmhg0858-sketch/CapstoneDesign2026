package capstone.capstone2026.controller;

import capstone.capstone2026.config.JwtUtil;
import capstone.capstone2026.domain.User;
import capstone.capstone2026.dto.UserJoinResponse;
import capstone.capstone2026.dto.LoginRequest;
import capstone.capstone2026.dto.LoginResponse;
import capstone.capstone2026.dto.UserJoinRequest;
import capstone.capstone2026.dto.UserJoinResponse;
import capstone.capstone2026.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;
    private final JwtUtil jwtUtil;

    @PostMapping("/signup")
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

        userService.join(user);

        // UserJoinResponse의 성공 메서드 호출
        return UserJoinResponse.success("회원가입이 완료되었습니다.", user.getNickname());
    }

    // 로그인 컨트롤러 구현
    @PostMapping("/login")
    public LoginResponse login(@RequestBody LoginRequest request) {
        User user = userService.login(request);

        // JWT 생성
        String token = jwtUtil.createToken(user.getId());

        return new LoginResponse(
                "로그인 성공",
                user.getId(),
                token
        );
    }
}
