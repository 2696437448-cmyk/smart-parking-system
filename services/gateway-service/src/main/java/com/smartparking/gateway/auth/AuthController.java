package com.smartparking.gateway.auth;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/v1/auth")
public class AuthController {

    private final AuthProperties properties;
    private final JwtService jwtService;

    public AuthController(AuthProperties properties, JwtService jwtService) {
        this.properties = properties;
        this.jwtService = jwtService;
    }

    @PostMapping("/login")
    public AuthResponses.LoginResponse login(@RequestBody AuthResponses.LoginRequest request) {
        DemoUserRecord user = properties.getUsers().stream()
                .filter(DemoUserRecord::enabled)
                .filter(candidate -> candidate.username().equals(request.username()) && candidate.password().equals(request.password()))
                .findFirst()
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "invalid_credentials"));

        return new AuthResponses.LoginResponse(
                jwtService.issueToken(user),
                "Bearer",
                properties.getJwtExpiresSeconds(),
                toUserSummary(user)
        );
    }

    @GetMapping("/me")
    public AuthResponses.UserSummary me(@RequestHeader(value = "Authorization", required = false) String authorization) {
        JwtService.AuthClaims claims = jwtService.parseToken(extractBearerToken(authorization));
        return new AuthResponses.UserSummary(claims.userId(), claims.username(), claims.displayName(), claims.role());
    }

    @PostMapping("/logout")
    @ResponseStatus(HttpStatus.OK)
    public AuthResponses.LogoutResponse logout() {
        return new AuthResponses.LogoutResponse("logged_out");
    }

    private AuthResponses.UserSummary toUserSummary(DemoUserRecord user) {
        return new AuthResponses.UserSummary(user.userId(), user.username(), user.displayName(), user.role());
    }

    private String extractBearerToken(String authorization) {
        if (authorization == null || !authorization.startsWith("Bearer ")) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "missing_bearer_token");
        }
        return authorization.substring("Bearer ".length()).trim();
    }
}
