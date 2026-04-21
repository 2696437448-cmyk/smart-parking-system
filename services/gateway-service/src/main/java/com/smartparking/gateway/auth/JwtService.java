package com.smartparking.gateway.auth;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.security.Keys;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.Clock;
import java.time.Instant;
import java.util.Arrays;
import java.util.Date;

public class JwtService {

    public record AuthClaims(
            String username,
            String userId,
            String role,
            String displayName,
            long issuedAtEpochSecond,
            long expiresAtEpochSecond
    ) {
    }

    private final AuthProperties properties;
    private final Clock clock;

    public JwtService(AuthProperties properties, Clock clock) {
        this.properties = properties;
        this.clock = clock;
    }

    public String issueToken(DemoUserRecord user) {
        Instant now = clock.instant();
        Instant expiresAt = now.plusSeconds(properties.getJwtExpiresSeconds());

        return Jwts.builder()
                .subject(user.username())
                .claim("user_id", user.userId())
                .claim("role", user.role())
                .claim("display_name", user.displayName())
                .issuedAt(Date.from(now))
                .expiration(Date.from(expiresAt))
                .signWith(signingKey())
                .compact();
    }

    public AuthClaims parseToken(String token) {
        try {
            Claims claims = Jwts.parser()
                    .verifyWith(signingKey())
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();

            return new AuthClaims(
                    claims.getSubject(),
                    claims.get("user_id", String.class),
                    claims.get("role", String.class),
                    claims.get("display_name", String.class),
                    claims.getIssuedAt().toInstant().getEpochSecond(),
                    claims.getExpiration().toInstant().getEpochSecond()
            );
        } catch (JwtException | IllegalArgumentException error) {
            throw new IllegalArgumentException("invalid_token", error);
        }
    }

    private SecretKey signingKey() {
        byte[] source = properties.getJwtSecret().getBytes(StandardCharsets.UTF_8);
        return Keys.hmacShaKeyFor(Arrays.copyOf(source, Math.max(32, source.length)));
    }
}
