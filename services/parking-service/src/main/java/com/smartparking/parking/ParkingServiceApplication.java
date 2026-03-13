package com.smartparking.parking;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import jakarta.annotation.PostConstruct;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.redisson.Redisson;
import org.redisson.api.RLock;
import org.redisson.api.RedissonClient;
import org.redisson.config.Config;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Repository;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.filter.OncePerRequestFilter;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;
import java.util.Base64;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;

@SpringBootApplication
public class ParkingServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(ParkingServiceApplication.class, args);
    }

    @Bean
    public ObjectMapper objectMapper() {
        ObjectMapper mapper = new ObjectMapper();
        mapper.configure(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS, true);
        return mapper;
    }

    @Bean(destroyMethod = "shutdown")
    public RedissonClient redissonClient(
            @Value("${REDIS_HOST:redis}") String redisHost,
            @Value("${REDIS_PORT:6379}") int redisPort
    ) {
        Config cfg = new Config();
        cfg.useSingleServer()
                .setAddress("redis://" + redisHost + ":" + redisPort)
                .setConnectTimeout(3000)
                .setTimeout(3000)
                .setRetryAttempts(8)
                .setRetryInterval(500);
        return Redisson.create(cfg);
    }

    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
                .setConnectTimeout(Duration.ofSeconds(5))
                .setReadTimeout(Duration.ofSeconds(5))
                .build();
    }
}

@Component
class ParkingMetrics {
    private final AtomicLong httpRequestsTotal = new AtomicLong(0);
    private final AtomicLong httpErrorsTotal = new AtomicLong(0);

    void recordStatus(int statusCode) {
        httpRequestsTotal.incrementAndGet();
        if (statusCode >= 400) {
            httpErrorsTotal.incrementAndGet();
        }
    }

    long requests() {
        return httpRequestsTotal.get();
    }

    long errors() {
        return httpErrorsTotal.get();
    }
}

@Component
class ParkingMetricsFilter extends OncePerRequestFilter {
    private final ParkingMetrics metrics;

    ParkingMetricsFilter(ParkingMetrics metrics) {
        this.metrics = metrics;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, java.io.IOException {
        filterChain.doFilter(request, response);
        metrics.recordStatus(response.getStatus());
    }
}

record ReservationRow(
        String reservationId,
        String userId,
        String slotId,
        String windowStart,
        String windowEnd,
        String location,
        String status
) {
}

@Repository
class ReservationRepository {
    private static final Logger log = LoggerFactory.getLogger(ReservationRepository.class);
    private final JdbcTemplate jdbcTemplate;

    ReservationRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @PostConstruct
    void initSchema() {
        String ddl = """
                CREATE TABLE IF NOT EXISTS reservations (
                  reservation_id VARCHAR(64) PRIMARY KEY,
                  user_id VARCHAR(64) NOT NULL,
                  slot_id VARCHAR(64) NOT NULL,
                  window_start VARCHAR(64) NOT NULL,
                  window_end VARCHAR(64) NOT NULL,
                  location VARCHAR(64) NOT NULL,
                  status VARCHAR(32) NOT NULL,
                  status_active TINYINT NOT NULL DEFAULT 1,
                  created_at DOUBLE NOT NULL,
                  UNIQUE KEY uk_slot_window_active (slot_id, window_start, window_end, status_active)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
                """;

        RuntimeException last = null;
        for (int i = 0; i < 60; i++) {
            try {
                jdbcTemplate.execute(ddl);
                log.info("mysql schema ready");
                return;
            } catch (RuntimeException ex) {
                last = ex;
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw new RuntimeException("schema init interrupted", ie);
                }
            }
        }

        throw new RuntimeException("mysql schema init failed after retry", last);
    }

    ReservationRow findActive(String slotId, String windowStart, String windowEnd) {
        String sql = """
                SELECT reservation_id, user_id, slot_id, window_start, window_end, location, status
                FROM reservations
                WHERE slot_id = ? AND window_start = ? AND window_end = ? AND status_active = 1
                LIMIT 1
                """;

        List<ReservationRow> rows = jdbcTemplate.query(sql, rowMapper(), slotId, windowStart, windowEnd);
        return rows.isEmpty() ? null : rows.get(0);
    }

    void insert(ReservationRow row) {
        String sql = """
                INSERT INTO reservations (
                  reservation_id, user_id, slot_id, window_start, window_end, location, status, status_active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """;

        jdbcTemplate.update(
                sql,
                row.reservationId(),
                row.userId(),
                row.slotId(),
                row.windowStart(),
                row.windowEnd(),
                row.location(),
                row.status(),
                1,
                Instant.now().toEpochMilli() / 1000.0
        );
    }

    int countActiveReservations() {
        Integer count = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM reservations WHERE status = 'RESERVED' AND status_active = 1",
                Integer.class
        );
        return count == null ? 0 : count;
    }

    List<ReservationRow> queryDebug(String slotId, String windowStart, String windowEnd) {
        String sql = """
                SELECT reservation_id, user_id, slot_id, window_start, window_end, location, status
                FROM reservations
                WHERE (? = '' OR slot_id = ?)
                  AND (? = '' OR window_start = ?)
                  AND (? = '' OR window_end = ?)
                ORDER BY reservation_id
                """;

        return jdbcTemplate.query(
                sql,
                rowMapper(),
                slotId,
                slotId,
                windowStart,
                windowStart,
                windowEnd,
                windowEnd
        );
    }

    private RowMapper<ReservationRow> rowMapper() {
        return new RowMapper<>() {
            @Override
            public ReservationRow mapRow(ResultSet rs, int rowNum) throws SQLException {
                return new ReservationRow(
                        rs.getString("reservation_id"),
                        rs.getString("user_id"),
                        rs.getString("slot_id"),
                        rs.getString("window_start"),
                        rs.getString("window_end"),
                        rs.getString("location"),
                        rs.getString("status")
                );
            }
        };
    }
}

record IdempotencyRecord(String payloadHash, int statusCode, Map<String, Object> responseBody, long createdAt) {
}

@Service
class IdempotencyStore {
    private static final Logger log = LoggerFactory.getLogger(IdempotencyStore.class);

    private final org.springframework.data.redis.core.StringRedisTemplate redisTemplate;
    private final ObjectMapper objectMapper;

    @Value("${IDEMPOTENCY_TTL_SECONDS:7200}")
    private long idempotencyTtlSeconds;

    IdempotencyStore(org.springframework.data.redis.core.StringRedisTemplate redisTemplate, ObjectMapper objectMapper) {
        this.redisTemplate = redisTemplate;
        this.objectMapper = objectMapper;
    }

    IdempotencyRecord get(String key) {
        String raw = redisTemplate.opsForValue().get(redisKey(key));
        if (raw == null) {
            return null;
        }
        try {
            return objectMapper.readValue(raw, IdempotencyRecord.class);
        } catch (JsonProcessingException ex) {
            log.warn("failed to decode idempotency record key={}", key, ex);
            return null;
        }
    }

    void save(String key, IdempotencyRecord record) {
        try {
            String raw = objectMapper.writeValueAsString(record);
            redisTemplate.opsForValue().set(redisKey(key), raw, Duration.ofSeconds(idempotencyTtlSeconds));
        } catch (Exception ex) {
            log.warn("failed to save idempotency key={} due to {}", key, ex.getMessage());
        }
    }

    Map<String, Object> debug(String key) {
        String rk = redisKey(key);
        String raw = redisTemplate.opsForValue().get(rk);
        Long ttl = redisTemplate.getExpire(rk, TimeUnit.SECONDS);
        if (raw == null) {
            return Map.of(
                    "key", key,
                    "exists", false,
                    "ttl_seconds", ttl == null ? -2 : ttl
            );
        }

        Map<String, Object> out = new LinkedHashMap<>();
        out.put("key", key);
        out.put("exists", true);
        out.put("ttl_seconds", ttl == null ? -2 : ttl);
        try {
            IdempotencyRecord rec = objectMapper.readValue(raw, IdempotencyRecord.class);
            out.put("payload_hash", rec.payloadHash());
            out.put("status_code", rec.statusCode());
            out.put("created_at", rec.createdAt());
        } catch (Exception ex) {
            out.put("decode_error", ex.getMessage());
        }
        return out;
    }

    private String redisKey(String key) {
        return "idem:" + key;
    }
}

@Service
class DispatchPublisher {
    private static final Logger log = LoggerFactory.getLogger(DispatchPublisher.class);

    @Value("${ENABLE_MQ:true}")
    private boolean enableMq;

    @Value("${RABBIT_API_URL:http://rabbitmq:15672/api}")
    private String rabbitApiUrl;

    @Value("${RABBIT_USER:guest}")
    private String rabbitUser;

    @Value("${RABBIT_PASS:guest}")
    private String rabbitPass;

    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;

    DispatchPublisher(RestTemplate restTemplate, ObjectMapper objectMapper) {
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(5))
                .version(HttpClient.Version.HTTP_1_1)
                .build();
        this.objectMapper = objectMapper;
    }

    boolean publishDispatchEvent(Map<String, Object> eventPayload) {
        if (!enableMq) {
            return true;
        }

        String url = rabbitApiUrl.replaceAll("/$", "") + "/exchanges/%2F/dispatch.events/publish";

        Map<String, Object> properties = new LinkedHashMap<>();
        properties.put("delivery_mode", 2);
        properties.put("headers", Map.of(
                "event_id", String.valueOf(eventPayload.getOrDefault("event_id", "")),
                "retry_count", 0
        ));

        Map<String, Object> body = new LinkedHashMap<>();
        body.put("properties", properties);
        body.put("routing_key", "dispatch.run");
        try {
            body.put("payload", objectMapper.writeValueAsString(eventPayload));
        } catch (JsonProcessingException ex) {
            log.warn("failed to serialize dispatch payload", ex);
            return false;
        }
        body.put("payload_encoding", "string");

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        String token = Base64.getEncoder().encodeToString((rabbitUser + ":" + rabbitPass).getBytes(StandardCharsets.UTF_8));
        String authorization = "Basic " + token;

        for (int attempt = 1; attempt <= 3; attempt++) {
            try {
                String bodyJson = objectMapper.writeValueAsString(body);
                HttpRequest req = HttpRequest.newBuilder()
                        .uri(URI.create(url))
                        .timeout(Duration.ofSeconds(5))
                        .header("Content-Type", "application/json")
                        .header("Authorization", authorization)
                        .POST(HttpRequest.BodyPublishers.ofString(bodyJson))
                        .build();

                HttpResponse<String> resp = httpClient.send(req, HttpResponse.BodyHandlers.ofString());
                if (resp.statusCode() < 200 || resp.statusCode() >= 300) {
                    throw new RuntimeException("rabbit_api_status=" + resp.statusCode() + ", body=" + resp.body());
                }
                String respBody = resp.body() == null ? "" : resp.body().trim();
                if (respBody.isEmpty()) {
                    return true;
                }
                Map<?, ?> payload = objectMapper.readValue(respBody, Map.class);
                Object routed = payload == null ? null : payload.get("routed");
                if (!(routed instanceof Boolean)) {
                    return true;
                }
                if (Boolean.TRUE.equals(routed)) {
                    return true;
                }
            } catch (Exception ex) {
                if (attempt == 3) {
                    log.warn("publish dispatch event failed: {}", ex.getMessage());
                }
            }

            try {
                Thread.sleep(150L * attempt);
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
                return false;
            }
        }
        return false;
    }
}

@Service
class ReservationService {
    private static final Logger log = LoggerFactory.getLogger(ReservationService.class);

    private final ReservationRepository repository;
    private final IdempotencyStore idempotencyStore;
    private final RedissonClient redissonClient;
    private final ObjectMapper objectMapper;

    @Value("${SERVICE_NAME:parking-service}")
    private String serviceName;

    @Value("${LOCK_WAIT_SECONDS:0.1}")
    private double lockWaitSeconds;

    @Value("${LOCK_LEASE_SECONDS:3.0}")
    private double lockLeaseSeconds;

    ReservationService(
            ReservationRepository repository,
            IdempotencyStore idempotencyStore,
            RedissonClient redissonClient,
            ObjectMapper objectMapper
    ) {
        this.repository = repository;
        this.idempotencyStore = idempotencyStore;
        this.redissonClient = redissonClient;
        this.objectMapper = objectMapper;
    }

    ApiResponse reserve(Map<String, Object> payload, String idempotencyKey, String traceId) {
        for (String field : List.of("user_id", "preferred_window", "location")) {
            if (!StringUtils.hasText(stringValue(payload.get(field)))) {
                return ApiResponse.of(400, Map.of(
                        "error", "missing_field",
                        "field", field,
                        "trace_id", traceId,
                        "service", serviceName
                ));
            }
        }

        String payloadHash = payloadHash(payload);
        if (StringUtils.hasText(idempotencyKey)) {
            IdempotencyRecord cached = idempotencyStore.get(idempotencyKey);
            if (cached != null) {
                if (payloadHash.equals(cached.payloadHash())) {
                    Map<String, Object> replay = new LinkedHashMap<>(cached.responseBody());
                    replay.put("replayed", true);
                    replay.put("trace_id", traceId);
                    replay.put("service", serviceName);
                    return ApiResponse.of(cached.statusCode(), replay);
                }
                return ApiResponse.of(409, Map.of(
                        "error", "idempotency_key_conflict",
                        "message", "same Idempotency-Key used with different payload",
                        "trace_id", traceId,
                        "service", serviceName
                ));
            }
        }

        String userId = stringValue(payload.get("user_id"));
        String location = stringValue(payload.get("location"));
        String preferredWindow = stringValue(payload.get("preferred_window"));
        String slotId = StringUtils.hasText(stringValue(payload.get("slot_id")))
                ? stringValue(payload.get("slot_id"))
                : location + "-S001";

        String[] window = splitWindow(preferredWindow);
        String windowStart = window[0];
        String windowEnd = window[1];

        String lockKey = "lock:slot:" + slotId + ":window:" + windowStart + "|" + windowEnd;
        RLock lock = redissonClient.getLock(lockKey);
        boolean acquired;

        try {
            acquired = lock.tryLock(
                    Math.max(1, (long) (lockWaitSeconds * 1000)),
                    Math.max(1, (long) (lockLeaseSeconds * 1000)),
                    TimeUnit.MILLISECONDS
            );
        } catch (InterruptedException ex) {
            Thread.currentThread().interrupt();
            return ApiResponse.of(503, Map.of(
                    "error", "lock_interrupted",
                    "trace_id", traceId,
                    "service", serviceName
            ));
        }

        if (!acquired) {
            return ApiResponse.of(429, Map.of(
                    "error", "lock_acquire_timeout",
                    "message", "reservation busy, retry later",
                    "slot_id", slotId,
                    "window_start", windowStart,
                    "window_end", windowEnd,
                    "trace_id", traceId,
                    "service", serviceName
            ));
        }

        ApiResponse response;
        try {
            ReservationRow existing = repository.findActive(slotId, windowStart, windowEnd);
            if (existing != null) {
                response = ApiResponse.of(409, Map.of(
                        "error", "oversell_prevented",
                        "reservation_id", existing.reservationId(),
                        "existing_user_id", existing.userId(),
                        "slot_id", slotId,
                        "window_start", windowStart,
                        "window_end", windowEnd,
                        "trace_id", traceId,
                        "service", serviceName
                ));
            } else {
                String reservationId = "res-" + UUID.randomUUID().toString().replace("-", "").substring(0, 16);
                ReservationRow row = new ReservationRow(
                        reservationId,
                        userId,
                        slotId,
                        windowStart,
                        windowEnd,
                        location,
                        "RESERVED"
                );
                repository.insert(row);
                response = ApiResponse.of(200, Map.of(
                        "reservation_id", reservationId,
                        "status", "RESERVED",
                        "slot_id", slotId,
                        "window_start", windowStart,
                        "window_end", windowEnd,
                        "trace_id", traceId,
                        "service", serviceName
                ));
            }
        } catch (DuplicateKeyException ex) {
            log.info("mysql unique constraint prevented oversell slot={} window={}~{}", slotId, windowStart, windowEnd);
            response = ApiResponse.of(409, Map.of(
                    "error", "oversell_prevented",
                    "message", "db uniqueness guard triggered",
                    "slot_id", slotId,
                    "window_start", windowStart,
                    "window_end", windowEnd,
                    "trace_id", traceId,
                    "service", serviceName
            ));
        } finally {
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }

        if (StringUtils.hasText(idempotencyKey)) {
            idempotencyStore.save(
                    idempotencyKey,
                    new IdempotencyRecord(
                            payloadHash,
                            response.statusCode(),
                            response.body(),
                            Instant.now().getEpochSecond()
                    )
            );
        }

        return response;
    }

    private String[] splitWindow(String preferredWindow) {
        if (preferredWindow != null && preferredWindow.contains("/")) {
            String[] arr = preferredWindow.split("/", 2);
            return new String[]{arr[0].trim(), arr[1].trim()};
        }
        String v = preferredWindow == null ? "" : preferredWindow.trim();
        return new String[]{v, v};
    }

    private String payloadHash(Map<String, Object> payload) {
        try {
            String canonical = objectMapper.writeValueAsString(new TreeMap<>(payload));
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] hash = md.digest(canonical.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : hash) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception ex) {
            throw new RuntimeException("payload hash failed", ex);
        }
    }

    private String stringValue(Object raw) {
        return raw == null ? "" : String.valueOf(raw).trim();
    }
}

record ApiResponse(int statusCode, Map<String, Object> body) {
    static ApiResponse of(int statusCode, Map<String, Object> body) {
        return new ApiResponse(statusCode, body);
    }
}

@RestController
@RequestMapping
class ParkingController {
    private final ReservationService reservationService;
    private final ReservationRepository reservationRepository;
    private final IdempotencyStore idempotencyStore;
    private final DispatchPublisher dispatchPublisher;
    private final ParkingMetrics metrics;

    @Value("${SERVICE_NAME:parking-service}")
    private String serviceName;

    @Value("${IDEMPOTENCY_TTL_SECONDS:7200}")
    private long idempotencyTtl;

    ParkingController(
            ReservationService reservationService,
            ReservationRepository reservationRepository,
            IdempotencyStore idempotencyStore,
            DispatchPublisher dispatchPublisher,
            ParkingMetrics metrics
    ) {
        this.reservationService = reservationService;
        this.reservationRepository = reservationRepository;
        this.idempotencyStore = idempotencyStore;
        this.dispatchPublisher = dispatchPublisher;
        this.metrics = metrics;
    }

    @PostMapping("/api/v1/owner/reservations")
    public ResponseEntity<Map<String, Object>> createReservation(
            @RequestBody Map<String, Object> payload,
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        ApiResponse response = reservationService.reserve(payload, idempotencyKey, traceId);
        return withTrace(traceId, response.statusCode(), response.body());
    }

    @PostMapping("/api/v1/admin/dispatch/run")
    public ResponseEntity<Map<String, Object>> runDispatch(
            @RequestBody(required = false) Map<String, Object> payload,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        Map<String, Object> body = payload == null ? Map.of() : payload;

        String triggerReason = String.valueOf(body.getOrDefault("trigger_reason", "manual"));
        boolean forceFail = Boolean.parseBoolean(String.valueOf(body.getOrDefault("force_fail", "false")));

        Map<String, Object> event = new LinkedHashMap<>();
        event.put("event_id", "evt-" + UUID.randomUUID().toString().replace("-", "").substring(0, 16));
        event.put("trigger_reason", triggerReason);
        event.put("force_fail", forceFail);
        event.put("created_at", Instant.now().toEpochMilli() / 1000.0);

        boolean routed = dispatchPublisher.publishDispatchEvent(event);

        Map<String, Object> resp = new LinkedHashMap<>();
        resp.put("job_id", "job-" + UUID.randomUUID().toString().replace("-", "").substring(0, 12));
        resp.put("accepted", routed);
        resp.put("trace_id", traceId);
        resp.put("trigger_reason", triggerReason);
        resp.put("event_id", event.get("event_id"));
        resp.put("mq_routed", routed);
        resp.put("service", serviceName);

        return withTrace(traceId, 200, resp);
    }

    @GetMapping("/api/v1/admin/realtime/status")
    public ResponseEntity<Map<String, Object>> realtimeStatus(
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        int active = reservationRepository.countActiveReservations();
        double estimatedCapacity = 60.0;
        double occupancy = Math.min(0.98, Math.max(0.05, active / estimatedCapacity));

        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("channel", "polling");
        payload.put("mode", "degraded");
        payload.put("occupancy_rate", Math.round(occupancy * 10000.0) / 10000.0);
        payload.put("active_reservations", active);
        payload.put("updated_at", Instant.now().toEpochMilli() / 1000.0);
        payload.put("trace_id", traceId);
        payload.put("service", serviceName);

        return withTrace(traceId, 200, payload);
    }

    @GetMapping("/internal/debug/reservations")
    public ResponseEntity<Map<String, Object>> debugReservations(
            @RequestParam(name = "slot_id", defaultValue = "") String slotId,
            @RequestParam(name = "window_start", defaultValue = "") String windowStart,
            @RequestParam(name = "window_end", defaultValue = "") String windowEnd,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        List<ReservationRow> rows = reservationRepository.queryDebug(slotId, windowStart, windowEnd);

        List<Map<String, Object>> items = new ArrayList<>();
        for (ReservationRow r : rows) {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("reservation_id", r.reservationId());
            item.put("user_id", r.userId());
            item.put("slot_id", r.slotId());
            item.put("window_start", r.windowStart());
            item.put("window_end", r.windowEnd());
            item.put("status", r.status());
            items.add(item);
        }

        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("count", items.size());
        payload.put("items", items);
        payload.put("service", serviceName);

        return withTrace(traceId, 200, payload);
    }

    @GetMapping("/internal/debug/idempotency")
    public ResponseEntity<Map<String, Object>> debugIdempotency(
            @RequestParam(name = "key", defaultValue = "") String key,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        if (!StringUtils.hasText(key)) {
            return withTrace(traceId, 400, Map.of("error", "missing_key", "service", serviceName));
        }

        Map<String, Object> payload = new LinkedHashMap<>(idempotencyStore.debug(key));
        payload.put("service", serviceName);
        return withTrace(traceId, 200, payload);
    }

    @GetMapping("/internal/debug/consistency/components")
    public ResponseEntity<Map<String, Object>> debugComponents(
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("service", serviceName);
        payload.put("idempotency_store", "redis");
        payload.put("lock_provider", "redisson");
        payload.put("database", "mysql");
        payload.put("idempotency_ttl_seconds", idempotencyTtl);
        payload.put("unique_constraint", "slot_id+window_start+window_end+status_active");
        return withTrace(traceId, 200, payload);
    }

    @GetMapping(value = "/metrics", produces = MediaType.TEXT_PLAIN_VALUE)
    public ResponseEntity<String> metricsText(
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        int active = reservationRepository.countActiveReservations();
        String body = String.join(
                "\n",
                "# HELP smart_parking_http_requests_total Total HTTP requests.",
                "# TYPE smart_parking_http_requests_total counter",
                String.format("smart_parking_http_requests_total{service=\"%s\"} %d", serviceName, metrics.requests()),
                "# HELP smart_parking_http_errors_total Total HTTP error responses.",
                "# TYPE smart_parking_http_errors_total counter",
                String.format("smart_parking_http_errors_total{service=\"%s\"} %d", serviceName, metrics.errors()),
                "# HELP smart_parking_active_reservations Active reservation count.",
                "# TYPE smart_parking_active_reservations gauge",
                String.format("smart_parking_active_reservations{service=\"%s\"} %d", serviceName, active)
        ) + "\n";

        return ResponseEntity.ok()
                .header("X-Trace-Id", traceId)
                .body(body);
    }

    private ResponseEntity<Map<String, Object>> withTrace(String traceId, int status, Map<String, Object> payload) {
        Map<String, Object> body = new LinkedHashMap<>(payload);
        body.putIfAbsent("trace_id", traceId);
        body.putIfAbsent("service", serviceName);

        return ResponseEntity.status(status)
                .header("X-Trace-Id", traceId)
                .body(body);
    }

    private String trace(String fromHeader) {
        if (StringUtils.hasText(fromHeader)) {
            return fromHeader;
        }
        return UUID.randomUUID().toString();
    }
}
