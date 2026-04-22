package com.smartparking.gateway.auth;

import org.springframework.stereotype.Component;

@Component
public class AuthRouteValidator {

    public boolean requiresAuthentication(String path) {
        return path.startsWith("/api/v1/owner/") || path.startsWith("/api/v1/admin/");
    }

    public boolean isRoleAllowed(String path, String role) {
        if (path.startsWith("/api/v1/owner/")) {
            return "OWNER".equals(role);
        }
        if (path.startsWith("/api/v1/admin/")) {
            return "ADMIN".equals(role);
        }
        return true;
    }
}
