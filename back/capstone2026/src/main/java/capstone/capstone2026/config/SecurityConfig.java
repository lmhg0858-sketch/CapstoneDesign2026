package capstone.capstone2026.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable()) // 외부 POST 요청 허용
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/users/**", "/h2-console/**").permitAll() // 누구나 접근 가능하게 허용
                .anyRequest().authenticated() // 그 외 나머지는 인증 필요
            )
            .headers(headers -> headers.frameOptions(frame -> frame.disable())); // H2 콘솔 사용을 위해 설정

        return http.build();
    }
}