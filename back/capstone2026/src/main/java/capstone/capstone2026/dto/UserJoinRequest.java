package capstone.capstone2026.dto;

import lombok.Getter;
import lombok.Setter;

@Getter @Setter
public class UserJoinRequest {
    private String id;
    private String email;
    private String password;
    private String nickname;
    private Integer age;
    private String gender;
    private Double height;
    private Double weight;
}
