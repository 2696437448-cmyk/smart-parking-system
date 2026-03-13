package com.smartparking.gateway;

import java.net.URI;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import org.springframework.cloud.gateway.support.ServerWebExchangeUtils;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

@RestController
public class ModelFallbackController {

    @RequestMapping("/fallback/model")
    public Mono<ResponseEntity<Map<String, Object>>> modelFallback(ServerWebExchange exchange) {
        String traceId = resolveTraceId(exchange);
        String originalPath = resolveOriginalPath(exchange);

        Map<String, Object> payload = new LinkedHashMap<>();
        if (originalPath.startsWith("/internal/v1/model/predict")) {
            payload.put("records", java.util.List.of());
        } else if (originalPath.startsWith("/internal/v1/dispatch/optimize")) {
            payload.put("results", java.util.List.of());
        } else if (originalPath.startsWith("/internal/v1/model/activate")) {
            payload.put("model_version", "fallback");
            payload.put("status", "degraded");
        } else {
            payload.put("error", "gateway_proxy_error");
        }

        payload.put("fallback_reason", "model_service_unavailable");
        payload.put("fallback_strategy", "default_rule");
        payload.put("trace_id", traceId);

        return Mono.just(ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_JSON)
                .header(TraceIdGlobalFilter.TRACE_HEADER, traceId)
                .body(payload));
    }

    private String resolveOriginalPath(ServerWebExchange exchange) {
        @SuppressWarnings("unchecked")
        Set<URI> originalUris = exchange.getAttribute(ServerWebExchangeUtils.GATEWAY_ORIGINAL_REQUEST_URL_ATTR);
        if (originalUris != null && !originalUris.isEmpty()) {
            return originalUris.iterator().next().getPath();
        }
        return "";
    }

    private String resolveTraceId(ServerWebExchange exchange) {
        Object attr = exchange.getAttribute(TraceIdGlobalFilter.TRACE_ATTR);
        if (attr instanceof String val && !val.isBlank()) {
            return val;
        }

        String header = exchange.getRequest().getHeaders().getFirst(TraceIdGlobalFilter.TRACE_HEADER);
        if (header != null && !header.isBlank()) {
            return header;
        }

        return UUID.randomUUID().toString();
    }
}
