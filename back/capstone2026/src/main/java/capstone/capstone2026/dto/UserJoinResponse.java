package capstone.capstone2026.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class UserJoinResponse<T> {
    private boolean success;
    private String message;
    private T data;

    // 성공 응답 정적 팩토리 메서드
    public static <T> UserJoinResponse<T> success(String message, T data) {
        return new UserJoinResponse<>(true, message, data);
    }

    // 실패 응답 정적 팩토리 메서드
    public static <T> UserJoinResponse<Void> error(String message) {
        return new UserJoinResponse<>(false, message, null);
    } 
}