package capstone.capstone2026.config;

import capstone.capstone2026.dto.UserJoinResponse;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {

    // 1. 중복 이메일 체크 시 던졌던 IllegalStateException 처리
    @ExceptionHandler(IllegalStateException.class)
    public UserJoinResponse<Void> handleIllegalState(IllegalStateException e) {
        // 성공 여부는 false, 에러 메시지는 예외 객체의 메시지를 그대로 전달
        return UserJoinResponse.error(e.getMessage());
    }

    // 2. 필수 값 누락(ID 등) 시 던졌던 IllegalArgumentException 처리
    @ExceptionHandler(IllegalArgumentException.class)
    public UserJoinResponse<Void> handleIllegalArgument(IllegalArgumentException e) {
        return UserJoinResponse.error(e.getMessage());
    }

    // 3. 그 외 우리가 예상하지 못한 모든 에러(NullPointerException 등) 처리
    @ExceptionHandler(Exception.class)
    public UserJoinResponse<Void> handleAllExceptions(Exception e) {
        // 보안을 위해 실제 에러 내용보다는 정돈된 메시지를 보냅니다.
        return UserJoinResponse.error("서버 내부에서 알 수 없는 오류가 발생했습니다.");
    }
}