package com.smartparking.gateway.auth;

import org.junit.jupiter.api.Test;

import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class JwtServiceTest {

    @Test
    void issueAndParseTokenRoundTrip() {
        AuthProperties properties = new AuthProperties();
        properties.setJwtSecret("smart-parking-demo-secret-1234567890");
        properties.setJwtExpiresSeconds(28800);

        Clock fixedClock = Clock.fixed(Instant.parse("2026-04-21T08:00:00Z"), ZoneOffset.UTC);
        JwtService service = new JwtService(properties, fixedClock);

        DemoUserRecord user = new DemoUserRecord("owner_demo", "demo123", "OWNER", "owner-app-001", "业主演示账号", true);
        String token = service.issueToken(user);
        JwtService.AuthClaims claims = service.parseToken(token);

        assertEquals("owner_demo", claims.username());
        assertEquals("OWNER", claims.role());
        assertEquals("owner-app-001", claims.userId());
        assertEquals("业主演示账号", claims.displayName());
        assertTrue(claims.expiresAtEpochSecond() > claims.issuedAtEpochSecond());
    }

    @Test
    void rejectTamperedToken() {
        AuthProperties properties = new AuthProperties();
        properties.setJwtSecret("smart-parking-demo-secret-1234567890");
        properties.setJwtExpiresSeconds(28800);

        JwtService service = new JwtService(properties, Clock.systemUTC());

        assertThrows(IllegalArgumentException.class, () -> service.parseToken("broken.token.value"));
    }
}
