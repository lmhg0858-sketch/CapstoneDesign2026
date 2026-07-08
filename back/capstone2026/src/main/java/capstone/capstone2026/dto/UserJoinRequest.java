package capstone.capstone2026.dto;

import lombok.Getter;
import lombok.Setter;
import java.util.List;

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
    private List<String> desease; // 프론트의 'desease' 키와 매칭
}
