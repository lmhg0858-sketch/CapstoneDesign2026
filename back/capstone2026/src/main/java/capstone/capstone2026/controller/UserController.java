package capstone.capstone2026.controller;

import capstone.capstone2026.config.JwtUtil;
import capstone.capstone2026.domain.User;
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
        // 컨트롤러에서 User 객체를 빌더로 만들지 않고, DTO를 서비스에 그대로 넘깁니다.
        // 서비스 내부에서 비밀번호 암호화 및 질병 매핑 처리를 모두 수행합니다.
        userService.join(dto);

        // 성공 응답 반환 (dto.getNickname()으로 닉네임 활용)
        return UserJoinResponse.success("회원가입이 완료되었습니다.", dto.getNickname());
    }

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