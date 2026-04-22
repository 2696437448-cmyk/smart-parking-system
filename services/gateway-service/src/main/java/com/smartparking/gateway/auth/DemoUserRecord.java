package com.smartparking.gateway.auth;

public record DemoUserRecord(
        String username,
        String password,
        String role,
        String userId,
        String displayName,
        boolean enabled
) {
}
