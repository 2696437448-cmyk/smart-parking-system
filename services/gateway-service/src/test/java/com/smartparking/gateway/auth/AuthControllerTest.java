package com.smartparking.gateway.auth;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.reactive.AutoConfigureWebTestClient;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.reactive.server.WebTestClient;

@SpringBootTest(
        webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
        properties = {
                "PARKING_BASE_URL=http://127.0.0.1:65535",
                "MODEL_BASE_URL=http://127.0.0.1:65534"
        }
)
@AutoConfigureWebTestClient
class AuthControllerTest {

    @Autowired
    private WebTestClient client;

    @Test
    void loginReturnsTokenAndCurrentUser() {
        client.post()
                .uri("/api/v1/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue("""
                        {"username":"owner_demo","password":"demo123"}
                        """)
                .exchange()
                .expectStatus().isOk()
                .expectBody()
                .jsonPath("$.access_token").isNotEmpty()
                .jsonPath("$.token_type").isEqualTo("Bearer")
                .jsonPath("$.user.username").isEqualTo("owner_demo")
                .jsonPath("$.user.role").isEqualTo("OWNER");
    }

    @Test
    void protectedAdminRouteRejectsMissingToken() {
        client.get()
                .uri("/api/v1/admin/dashboard?date=2026-04-21")
                .exchange()
                .expectStatus().isUnauthorized();
    }
}
