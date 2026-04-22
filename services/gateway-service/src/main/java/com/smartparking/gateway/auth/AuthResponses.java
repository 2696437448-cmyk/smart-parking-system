package com.smartparking.gateway.auth;

public final class AuthResponses {

    private AuthResponses() {
    }

    public record LoginRequest(String username, String password) {
    }

    public record UserSummary(String user_id, String username, String display_name, String role) {
    }

    public record LoginResponse(String access_token, String token_type, long expires_in, UserSummary user) {
    }

    public record LogoutResponse(String status) {
    }
}
