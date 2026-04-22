package com.smartparking.gateway.auth;

import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.factory.AbstractGatewayFilterFactory;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.nio.charset.StandardCharsets;

@Component
public class AuthGatewayFilterFactory extends AbstractGatewayFilterFactory<AuthGatewayFilterFactory.Config> {

    public static class Config {
    }

    private final JwtService jwtService;
    private final AuthRouteValidator routeValidator;

    public AuthGatewayFilterFactory(JwtService jwtService, AuthRouteValidator routeValidator) {
        super(Config.class);
        this.jwtService = jwtService;
        this.routeValidator = routeValidator;
    }

    @Override
    public GatewayFilter apply(Config config) {
        return (exchange, chain) -> {
            String path = exchange.getRequest().getURI().getPath();
            if (!routeValidator.requiresAuthentication(path)) {
                return chain.filter(exchange);
            }

            String authorization = exchange.getRequest().getHeaders().getFirst(HttpHeaders.AUTHORIZATION);
            if (authorization == null || !authorization.startsWith("Bearer ")) {
                return fail(exchange, HttpStatus.UNAUTHORIZED, "missing_bearer_token");
            }

            JwtService.AuthClaims claims;
            try {
                claims = jwtService.parseToken(authorization.substring("Bearer ".length()).trim());
            } catch (IllegalArgumentException error) {
                return fail(exchange, HttpStatus.UNAUTHORIZED, "invalid_token");
            }

            if (!routeValidator.isRoleAllowed(path, claims.role())) {
                return fail(exchange, HttpStatus.FORBIDDEN, "forbidden");
            }

            ServerWebExchange mutatedExchange = exchange.mutate().request(request -> request.headers(headers -> {
                headers.set("X-Auth-User-Id", claims.userId());
                headers.set("X-Auth-Role", claims.role());
                headers.set("X-Auth-Username", claims.username());
            })).build();
            return chain.filter(mutatedExchange);
        };
    }

    private Mono<Void> fail(ServerWebExchange exchange, HttpStatus status, String message) {
        exchange.getResponse().setStatusCode(status);
        exchange.getResponse().getHeaders().setContentType(MediaType.APPLICATION_JSON);
        byte[] body = ("{\"error\":\"" + message + "\"}").getBytes(StandardCharsets.UTF_8);
        return exchange.getResponse().writeWith(Mono.just(exchange.getResponse().bufferFactory().wrap(body)));
    }
}
