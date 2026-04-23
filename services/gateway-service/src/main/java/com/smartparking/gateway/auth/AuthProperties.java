package com.smartparking.gateway.auth;

import org.springframework.boot.context.properties.ConfigurationProperties;

import java.util.ArrayList;
import java.util.List;

@ConfigurationProperties(prefix = "auth")
public class AuthProperties {

    private String jwtSecret = "";
    private long jwtExpiresSeconds = 28_800;
    private List<DemoUserRecord> users = new ArrayList<>();

    public String getJwtSecret() {
        return jwtSecret;
    }

    public void setJwtSecret(String jwtSecret) {
        this.jwtSecret = jwtSecret;
    }

    public long getJwtExpiresSeconds() {
        return jwtExpiresSeconds;
    }

    public void setJwtExpiresSeconds(long jwtExpiresSeconds) {
        this.jwtExpiresSeconds = jwtExpiresSeconds;
    }

    public List<DemoUserRecord> getUsers() {
        return users;
    }

    public void setUsers(List<DemoUserRecord> users) {
        this.users = users;
    }
}
