import com.sun.net.httpserver.Headers;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.Executors;

public class GatewayMain {
    private static final String TRACE_HEADER = "X-Trace-Id";

    public static void main(String[] args) throws Exception {
        String parkingBase = env("PARKING_BASE_URL", "http://parking-service:8081");
        String modelBase = env("MODEL_BASE_URL", "http://model-service:8000");
        int port = Integer.parseInt(env("PORT", "8080"));
        int upstreamTimeoutMs = Integer.parseInt(env("UPSTREAM_TIMEOUT_MS", "2500"));
        int upstreamConnectTimeoutMs = Integer.parseInt(env("UPSTREAM_CONNECT_TIMEOUT_MS", "10000"));

        HttpClient client = HttpClient.newBuilder()
                .connectTimeout(Duration.ofMillis(upstreamConnectTimeoutMs))
                .build();

        HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);
        server.setExecutor(Executors.newCachedThreadPool());

        server.createContext("/actuator/health", new HealthHandler());
        server.createContext("/", new ProxyHandler(client, parkingBase, modelBase, upstreamTimeoutMs));

        System.out.println("gateway-service started on port " + port);
        System.out.println("parkingBase=" + parkingBase + ", modelBase=" + modelBase);
        server.start();
    }

    private static String env(String key, String fallback) {
        String val = System.getenv(key);
        return (val == null || val.isBlank()) ? fallback : val;
    }

    private static class HealthHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String body = "{\"status\":\"UP\",\"service\":\"gateway-service\"}";
            Headers resp = exchange.getResponseHeaders();
            resp.add("Content-Type", "application/json");
            exchange.sendResponseHeaders(200, body.getBytes(StandardCharsets.UTF_8).length);
            try (OutputStream os = exchange.getResponseBody()) {
                os.write(body.getBytes(StandardCharsets.UTF_8));
            }
        }
    }

    private static class ProxyHandler implements HttpHandler {
        private final HttpClient client;
        private final String parkingBase;
        private final String modelBase;
        private final int upstreamTimeoutMs;

        ProxyHandler(HttpClient client, String parkingBase, String modelBase, int upstreamTimeoutMs) {
            this.client = client;
            this.parkingBase = parkingBase;
            this.modelBase = modelBase;
            this.upstreamTimeoutMs = upstreamTimeoutMs;
        }

        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String path = exchange.getRequestURI().getPath();
            String query = exchange.getRequestURI().getRawQuery();
            String targetBase;

            if (path.startsWith("/api/v1/owner") || path.startsWith("/api/v1/admin")) {
                targetBase = parkingBase;
            } else if (path.startsWith("/internal/v1/model") || path.startsWith("/internal/v1/dispatch")) {
                targetBase = modelBase;
            } else {
                byte[] notFound = "{\"error\":\"route_not_found\"}".getBytes(StandardCharsets.UTF_8);
                exchange.getResponseHeaders().add("Content-Type", "application/json");
                exchange.sendResponseHeaders(404, notFound.length);
                try (OutputStream os = exchange.getResponseBody()) {
                    os.write(notFound);
                }
                return;
            }

            String target = targetBase + path + (query == null || query.isBlank() ? "" : ("?" + query));
            String traceId = ensureTraceId(exchange.getRequestHeaders());
            byte[] requestBody = new byte[0];

            try {
                requestBody = readAll(exchange.getRequestBody());
                HttpRequest.Builder builder = HttpRequest.newBuilder()
                        .uri(URI.create(target))
                        .timeout(Duration.ofMillis(upstreamTimeoutMs));

                if (requestBody.length == 0) {
                    builder.method(exchange.getRequestMethod(), HttpRequest.BodyPublishers.noBody());
                } else {
                    builder.method(exchange.getRequestMethod(), HttpRequest.BodyPublishers.ofByteArray(requestBody));
                }

                for (Map.Entry<String, List<String>> e : exchange.getRequestHeaders().entrySet()) {
                    String key = e.getKey();
                    if (isRestrictedForwardHeader(key)) {
                        continue;
                    }
                    for (String val : e.getValue()) {
                        builder.header(key, val);
                    }
                }
                builder.header(TRACE_HEADER, traceId);

                HttpResponse<byte[]> resp = client.send(builder.build(), HttpResponse.BodyHandlers.ofByteArray());
                Headers outHeaders = exchange.getResponseHeaders();
                for (Map.Entry<String, List<String>> e : resp.headers().map().entrySet()) {
                    String key = e.getKey();
                    if (key == null || key.equalsIgnoreCase("content-length") || key.equalsIgnoreCase("transfer-encoding")) {
                        continue;
                    }
                    for (String val : e.getValue()) {
                        outHeaders.add(key, val);
                    }
                }
                outHeaders.set(TRACE_HEADER, traceId);
                exchange.sendResponseHeaders(resp.statusCode(), resp.body().length);
                try (OutputStream os = exchange.getResponseBody()) {
                    os.write(resp.body());
                }
            } catch (Exception ex) {
                byte[] fallback = fallbackForModelPath(path, requestBody, traceId);
                if (fallback != null) {
                    exchange.getResponseHeaders().set("Content-Type", "application/json");
                    exchange.getResponseHeaders().set(TRACE_HEADER, traceId);
                    exchange.sendResponseHeaders(200, fallback.length);
                    try (OutputStream os = exchange.getResponseBody()) {
                        os.write(fallback);
                    }
                    return;
                }

                byte[] body = ("{\"error\":\"gateway_proxy_error\",\"message\":\"" + safeMessage(ex) + "\",\"trace_id\":\"" + traceId + "\"}")
                        .getBytes(StandardCharsets.UTF_8);
                exchange.getResponseHeaders().set("Content-Type", "application/json");
                exchange.getResponseHeaders().set(TRACE_HEADER, traceId);
                exchange.sendResponseHeaders(502, body.length);
                try (OutputStream os = exchange.getResponseBody()) {
                    os.write(body);
                }
            }
        }

        private boolean isRestrictedForwardHeader(String key) {
            return key == null
                    || key.equalsIgnoreCase("Host")
                    || key.equalsIgnoreCase("Content-Length")
                    || key.equalsIgnoreCase("Connection")
                    || key.equalsIgnoreCase("Keep-Alive")
                    || key.equalsIgnoreCase("Proxy-Connection")
                    || key.equalsIgnoreCase("Transfer-Encoding")
                    || key.equalsIgnoreCase("Upgrade")
                    || key.equalsIgnoreCase("Trailer")
                    || key.equalsIgnoreCase("TE");
        }

        private byte[] fallbackForModelPath(String path, byte[] requestBody, String traceId) {
            if (path.startsWith("/internal/v1/model/predict")) {
                String json = "{\"records\":[],\"fallback_reason\":\"model_service_unavailable\",\"fallback_strategy\":\"default_rule\",\"trace_id\":\""
                        + traceId + "\"}";
                return json.getBytes(StandardCharsets.UTF_8);
            }

            if (path.startsWith("/internal/v1/dispatch/optimize")) {
                String json = "{\"results\":[],\"fallback_reason\":\"model_service_unavailable\",\"fallback_strategy\":\"default_rule\",\"trace_id\":\""
                        + traceId + "\"}";
                return json.getBytes(StandardCharsets.UTF_8);
            }

            if (path.startsWith("/internal/v1/model/activate")) {
                String json = "{\"model_version\":\"fallback\",\"status\":\"degraded\",\"fallback_reason\":\"model_service_unavailable\",\"fallback_strategy\":\"default_rule\",\"trace_id\":\""
                        + traceId + "\"}";
                return json.getBytes(StandardCharsets.UTF_8);
            }

            return null;
        }

        private String safeMessage(Exception ex) {
            String m = ex.getMessage();
            return m == null ? "proxy_failed" : m.replace("\"", "'");
        }

        private String ensureTraceId(Headers headers) {
            List<String> vals = headers.get(TRACE_HEADER);
            if (vals != null && !vals.isEmpty() && vals.get(0) != null && !vals.get(0).isBlank()) {
                return vals.get(0);
            }
            return UUID.randomUUID().toString();
        }

        private byte[] readAll(InputStream in) throws IOException {
            return in.readAllBytes();
        }
    }
}
