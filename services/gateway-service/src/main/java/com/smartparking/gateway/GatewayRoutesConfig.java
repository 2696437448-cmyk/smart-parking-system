package com.smartparking.gateway;

import com.smartparking.gateway.auth.AuthGatewayFilterFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class GatewayRoutesConfig {

    private final String parkingBaseUrl;
    private final String modelBaseUrl;

    public GatewayRoutesConfig(
            @Value("${PARKING_BASE_URL:http://parking-service:8081}") String parkingBaseUrl,
            @Value("${MODEL_BASE_URL:http://model-service:8000}") String modelBaseUrl
    ) {
        this.parkingBaseUrl = parkingBaseUrl;
        this.modelBaseUrl = modelBaseUrl;
    }

    @Bean
    public RouteLocator routeLocator(RouteLocatorBuilder builder, AuthGatewayFilterFactory authGatewayFilterFactory) {
        return builder.routes()
                .route("parking-route", r -> r
                        .path("/api/v1/owner/**", "/api/v1/admin/**", "/internal/v1/ingest/**")
                        .filters(f -> f.filter(authGatewayFilterFactory.apply(new AuthGatewayFilterFactory.Config())))
                        .uri(parkingBaseUrl))
                .route("model-route", r -> r
                        .path("/internal/v1/model/**", "/internal/v1/dispatch/**")
                        .filters(f -> f
                                .circuitBreaker(c -> c
                                        .setName("modelServiceCb")
                                        .setFallbackUri("forward:/fallback/model")))
                        .uri(modelBaseUrl))
                .build();
    }
}
