package com.smartparking.parking;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

record BillingRecordRow(
        String orderId,
        String reservationId,
        String userId,
        String slotId,
        String regionId,
        String startedAt,
        String endedAt,
        int billableMinutes,
        double estimatedAmount,
        double finalAmount,
        String billingStatus,
        String recognizedOn
) {
}

record GeoPoint(double lat, double lng, String displayName) {
}

record RegionRevenueSummaryRow(String date, String regionId, double revenueAmount, int orderCount, double utilizationRate) {
}

@Repository
class BillingRepository {
    private static final Logger log = LoggerFactory.getLogger(BillingRepository.class);

    private final JdbcTemplate jdbcTemplate;

    BillingRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @PostConstruct
    void initSchema() {
        String ddl = """
                CREATE TABLE IF NOT EXISTS billing_records (
                  order_id VARCHAR(64) PRIMARY KEY,
                  reservation_id VARCHAR(64) NOT NULL,
                  user_id VARCHAR(64) NOT NULL,
                  slot_id VARCHAR(64) NOT NULL,
                  region_id VARCHAR(32) NOT NULL,
                  started_at VARCHAR(64) NOT NULL,
                  ended_at VARCHAR(64) NOT NULL,
                  billable_minutes INT NOT NULL,
                  estimated_amount DECIMAL(10,2) NOT NULL,
                  final_amount DECIMAL(10,2) NOT NULL,
                  billing_status VARCHAR(32) NOT NULL,
                  recognized_on VARCHAR(32) NOT NULL,
                  created_at DOUBLE NOT NULL,
                  updated_at DOUBLE NOT NULL
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
                """;

        RuntimeException last = null;
        for (int i = 0; i < 60; i++) {
            try {
                jdbcTemplate.execute(ddl);
                log.info("billing schema ready");
                return;
            } catch (RuntimeException ex) {
                last = ex;
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw new RuntimeException("billing schema init interrupted", ie);
                }
            }
        }

        throw new RuntimeException("billing schema init failed after retry", last);
    }

    void upsertEstimated(
            String orderId,
            String reservationId,
            String userId,
            String slotId,
            String regionId,
            String startedAt,
            String endedAt,
            int billableMinutes,
            double estimatedAmount
    ) {
        String sql = """
                INSERT INTO billing_records (
                  order_id, reservation_id, user_id, slot_id, region_id, started_at, ended_at,
                  billable_minutes, estimated_amount, final_amount, billing_status, recognized_on,
                  created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON DUPLICATE KEY UPDATE
                  started_at = VALUES(started_at),
                  ended_at = VALUES(ended_at),
                  billable_minutes = VALUES(billable_minutes),
                  estimated_amount = VALUES(estimated_amount),
                  final_amount = VALUES(final_amount),
                  billing_status = VALUES(billing_status),
                  updated_at = VALUES(updated_at)
                """;
        double now = Instant.now().toEpochMilli() / 1000.0;
        jdbcTemplate.update(
                sql,
                orderId,
                reservationId,
                userId,
                slotId,
                regionId,
                startedAt,
                endedAt,
                billableMinutes,
                estimatedAmount,
                estimatedAmount,
                "ESTIMATED",
                "",
                now,
                now
        );
    }

    BillingRecordRow findByOrderId(String orderId) {
        String sql = """
                SELECT order_id, reservation_id, user_id, slot_id, region_id, started_at, ended_at,
                       billable_minutes, estimated_amount, final_amount, billing_status, recognized_on
                FROM billing_records
                WHERE order_id = ?
                LIMIT 1
                """;
        try {
            return jdbcTemplate.queryForObject(sql, rowMapper(), orderId);
        } catch (EmptyResultDataAccessException ex) {
            return null;
        }
    }

    BillingRecordRow confirmFinalBill(String orderId, String endedAt, int billableMinutes, double finalAmount, String recognizedOn) {
        String sql = """
                UPDATE billing_records
                SET ended_at = ?,
                    billable_minutes = ?,
                    final_amount = ?,
                    billing_status = 'CONFIRMED',
                    recognized_on = ?,
                    updated_at = ?
                WHERE order_id = ?
                """;
        jdbcTemplate.update(sql, endedAt, billableMinutes, finalAmount, recognizedOn, Instant.now().toEpochMilli() / 1000.0, orderId);
        return findByOrderId(orderId);
    }

    List<RegionRevenueSummaryRow> summarizeByDate(String date, String regionId) {
        String sql = """
                SELECT region_id, COALESCE(SUM(final_amount), 0) AS revenue_amount, COUNT(*) AS order_count
                FROM billing_records
                WHERE billing_status = 'CONFIRMED'
                  AND recognized_on = ?
                  AND (? = '' OR region_id = ?)
                GROUP BY region_id
                ORDER BY region_id
                """;
        return jdbcTemplate.query(sql, (rs, rowNum) -> new RegionRevenueSummaryRow(
                date,
                rs.getString("region_id"),
                rs.getDouble("revenue_amount"),
                rs.getInt("order_count"),
                0.0
        ), date, regionId, regionId);
    }

    private RowMapper<BillingRecordRow> rowMapper() {
        return new RowMapper<>() {
            @Override
            public BillingRecordRow mapRow(ResultSet rs, int rowNum) throws SQLException {
                return new BillingRecordRow(
                        rs.getString("order_id"),
                        rs.getString("reservation_id"),
                        rs.getString("user_id"),
                        rs.getString("slot_id"),
                        rs.getString("region_id"),
                        rs.getString("started_at"),
                        rs.getString("ended_at"),
                        rs.getInt("billable_minutes"),
                        rs.getDouble("estimated_amount"),
                        rs.getDouble("final_amount"),
                        rs.getString("billing_status"),
                        rs.getString("recognized_on")
                );
            }
        };
    }
}

@Service
class BillingService {
    static final ZoneId BUSINESS_ZONE = ZoneId.of("Asia/Shanghai");
    private static final int UNIT_MINUTES = 15;

    private final BillingRepository billingRepository;

    BillingService(BillingRepository billingRepository) {
        this.billingRepository = billingRepository;
    }

    BillingRecordRow createEstimatedOrder(
            String orderId,
            String userId,
            String slotId,
            String location,
            String windowStart,
            String windowEnd
    ) {
        String regionId = regionFrom(location, slotId);
        Instant start = parseWindowStart(windowStart);
        Instant end = parseWindowEnd(windowStart, windowEnd);
        int billableMinutes = billableMinutes(start, end);
        double estimatedAmount = calculateAmount(regionId, start, end);
        billingRepository.upsertEstimated(orderId, orderId, userId, slotId, regionId, start.toString(), end.toString(), billableMinutes, estimatedAmount);
        return billingRepository.findByOrderId(orderId);
    }

    BillingRecordRow completeOrder(String orderId, String endedAt) {
        BillingRecordRow current = billingRepository.findByOrderId(orderId);
        if (current == null) {
            return null;
        }
        Instant start = parseInstantFlexible(current.startedAt());
        Instant actualEnd = StringUtils.hasText(endedAt) ? parseInstantFlexible(endedAt) : parseInstantFlexible(current.endedAt());
        if (actualEnd.isBefore(start)) {
            actualEnd = start.plus(Duration.ofMinutes(UNIT_MINUTES));
        }
        int billableMinutes = billableMinutes(start, actualEnd);
        double finalAmount = calculateAmount(current.regionId(), start, actualEnd);
        String recognizedOn = actualEnd.atZone(BUSINESS_ZONE).toLocalDate().toString();
        return billingRepository.confirmFinalBill(orderId, actualEnd.toString(), billableMinutes, finalAmount, recognizedOn);
    }

    BillingRecordRow getOrder(String orderId) {
        return billingRepository.findByOrderId(orderId);
    }

    List<Map<String, Object>> summarizeRevenue(String date, String regionId) {
        List<Map<String, Object>> rows = new ArrayList<>();
        for (RegionRevenueSummaryRow row : billingRepository.summarizeByDate(date, regionId)) {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("date", row.date());
            item.put("region_id", row.regionId());
            item.put("revenue_amount", round2(row.revenueAmount()));
            item.put("order_count", row.orderCount());
            item.put("utilization_rate", utilizationFor(row.regionId(), row.orderCount()));
            rows.add(item);
        }
        return rows;
    }

    Map<String, Object> billingRuleView() {
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("timezone", BUSINESS_ZONE.getId());
        payload.put("unit_minutes", UNIT_MINUTES);
        payload.put("rounding_mode", "CEIL_TO_UNIT");
        payload.put("effective_window", "region + time_bucket + duration");
        return payload;
    }

    double previewAmount(String location, String slotId, String preferredWindow) {
        String[] window = splitWindow(preferredWindow);
        Instant start = parseWindowStart(window[0]);
        Instant end = parseWindowEnd(window[0], window[1]);
        return calculateAmount(regionFrom(location, slotId), start, end);
    }

    private double calculateAmount(String regionId, Instant start, Instant end) {
        int billableMinutes = billableMinutes(start, end);
        int units = Math.max(1, (int) Math.ceil(billableMinutes / (double) UNIT_MINUTES));
        ZonedDateTime localStart = start.atZone(BUSINESS_ZONE);
        int hour = localStart.getHour();
        double bucketRate;
        if (hour >= 17 && hour < 22) {
            bucketRate = 8.0;
        } else if (hour >= 7 && hour < 17) {
            bucketRate = 6.0;
        } else {
            bucketRate = 4.0;
        }
        double regionFactor = switch (regionId) {
            case "R1" -> 1.15;
            case "R2" -> 1.0;
            case "R3" -> 0.9;
            default -> 1.0;
        };
        return round2(units * bucketRate * regionFactor);
    }

    private int billableMinutes(Instant start, Instant end) {
        long minutes = Math.max(UNIT_MINUTES, Duration.between(start, end).toMinutes());
        return (int) (Math.ceil(minutes / (double) UNIT_MINUTES) * UNIT_MINUTES);
    }

    private Instant parseWindowStart(String windowStart) {
        return parseInstantFlexible(windowStart);
    }

    private Instant parseWindowEnd(String windowStart, String windowEnd) {
        if (!StringUtils.hasText(windowEnd)) {
            return parseWindowStart(windowStart).plus(Duration.ofMinutes(UNIT_MINUTES));
        }
        if (windowEnd.contains("T") || windowEnd.endsWith("Z") || windowEnd.contains("+")) {
            return parseInstantFlexible(windowEnd);
        }
        Instant start = parseWindowStart(windowStart);
        try {
            LocalDate baseDate = start.atZone(BUSINESS_ZONE).toLocalDate();
            LocalDateTime localDateTime = LocalDateTime.parse(baseDate + "T" + windowEnd);
            return localDateTime.atZone(BUSINESS_ZONE).toInstant();
        } catch (Exception ex) {
            return start.plus(Duration.ofMinutes(UNIT_MINUTES));
        }
    }

    private Instant parseInstantFlexible(String raw) {
        if (!StringUtils.hasText(raw)) {
            return Instant.now();
        }
        try {
            return Instant.parse(raw);
        } catch (DateTimeParseException ignored) {
        }
        try {
            return OffsetDateTime.parse(raw).toInstant();
        } catch (DateTimeParseException ignored) {
        }
        try {
            return LocalDateTime.parse(raw).atZone(BUSINESS_ZONE).toInstant();
        } catch (DateTimeParseException ignored) {
        }
        return Instant.now();
    }

    private String[] splitWindow(String preferredWindow) {
        if (preferredWindow != null && preferredWindow.contains("/")) {
            String[] arr = preferredWindow.split("/", 2);
            return new String[]{arr[0].trim(), arr[1].trim()};
        }
        String value = preferredWindow == null ? "" : preferredWindow.trim();
        return new String[]{value, value};
    }

    private String regionFrom(String location, String slotId) {
        if (StringUtils.hasText(slotId) && slotId.contains("-")) {
            return slotId.split("-")[0].trim().toUpperCase();
        }
        if (StringUtils.hasText(location)) {
            return location.split("-")[0].trim().toUpperCase();
        }
        return "R1";
    }

    private double round2(double value) {
        return BigDecimal.valueOf(value).setScale(2, RoundingMode.HALF_UP).doubleValue();
    }

    private double utilizationFor(String regionId, int orderCount) {
        double capacity = switch (regionId) {
            case "R1" -> 24.0;
            case "R2" -> 20.0;
            case "R3" -> 18.0;
            default -> 20.0;
        };
        return BigDecimal.valueOf(Math.min(1.0, orderCount / capacity)).setScale(4, RoundingMode.HALF_UP).doubleValue();
    }
}

@Service
class OwnerAdminFacade {
    private final BillingService billingService;
    private final ReservationRepository reservationRepository;
    private final GeoCatalogService geoCatalogService;

    OwnerAdminFacade(BillingService billingService, ReservationRepository reservationRepository, GeoCatalogService geoCatalogService) {
        this.billingService = billingService;
        this.reservationRepository = reservationRepository;
        this.geoCatalogService = geoCatalogService;
    }

    List<Map<String, Object>> recommendations(String location, String preferredWindow) {
        String region = regionOf(location);
        List<Map<String, Object>> items = new ArrayList<>();
        for (int i = 1; i <= 3; i++) {
            String slotId = String.format("%s-S%03d", region, i);
            GeoPoint point = geoCatalogService.resolveGeoPoint(slotId, region);
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("slot_id", slotId);
            item.put("estimated_amount", billingService.previewAmount(region, slotId, preferredWindow));
            item.put("eta_minutes", etaMinutes(region, slotId));
            item.put("destination", geoPayload(point));
            item.put("map_url", mapUrl(point));
            item.put("slot_display_name", point.displayName());
            item.put("region_label", geoCatalogService.regionLabel(region));
            items.add(item);
        }
        return items;
    }

    Map<String, Object> orderDetail(String orderId) {
        BillingRecordRow row = billingService.getOrder(orderId);
        if (row == null) {
            return null;
        }
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("order_id", row.orderId());
        payload.put("reservation_id", row.reservationId());
        payload.put("user_id", row.userId());
        payload.put("slot_id", row.slotId());
        payload.put("region_id", row.regionId());
        payload.put("started_at", row.startedAt());
        payload.put("ended_at", row.endedAt());
        payload.put("billable_minutes", row.billableMinutes());
        payload.put("estimated_amount", row.estimatedAmount());
        payload.put("final_amount", row.finalAmount());
        payload.put("billing_status", row.billingStatus());
        payload.put("recognized_on", row.recognizedOn());
        payload.put("billing_rule", billingService.billingRuleView());
        return payload;
    }

    Map<String, Object> navigation(String orderId) {
        BillingRecordRow row = billingService.getOrder(orderId);
        if (row == null) {
            return null;
        }
        GeoPoint point = geoCatalogService.resolveGeoPoint(row.slotId(), row.regionId());
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("order_id", row.orderId());
        payload.put("slot_id", row.slotId());
        int etaMinutes = etaMinutes(row.regionId(), row.slotId());
        payload.put("eta_minutes", etaMinutes);
        payload.put("map_url", mapUrl(point));
        payload.put("destination", geoPayload(point));
        payload.put("region_label", geoCatalogService.regionLabel(row.regionId()));
        payload.put("slot_display_name", point.displayName());
        Map<String, Object> routeSummary = new LinkedHashMap<>();
        routeSummary.put("distance_km", geoCatalogService.distanceKm(row.regionId(), row.slotId()));
        routeSummary.put("route_mode", "walk_drive_mix");
        routeSummary.put("summary", "进入社区后按路侧引导到达目标车位");
        routeSummary.put("eta_minutes", etaMinutes);
        payload.put("route_summary", routeSummary);
        return payload;
    }

    Map<String, Object> monitorSummary(String date) {
        int active = reservationRepository.countActiveReservations();
        List<Map<String, Object>> revenue = billingService.summarizeRevenue(date, "");
        double totalRevenue = 0.0;
        for (Map<String, Object> item : revenue) {
            totalRevenue += ((Number) item.get("revenue_amount")).doubleValue();
        }
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("date", date);
        payload.put("active_reservations", active);
        payload.put("occupancy_rate", BigDecimal.valueOf(Math.min(0.98, Math.max(0.05, active / 60.0))).setScale(4, RoundingMode.HALF_UP).doubleValue());
        payload.put("revenue_total", BigDecimal.valueOf(totalRevenue).setScale(2, RoundingMode.HALF_UP).doubleValue());
        payload.put("region_summaries", revenue);
        payload.put("dispatch_strategy", "hungarian_optimal");
        payload.put("business_view", true);
        Map<String, Object> diagnostics = new LinkedHashMap<>();
        diagnostics.put("grafana", "http://localhost:13000");
        diagnostics.put("rabbitmq", "http://localhost:15672");
        payload.put("diagnostic_links", diagnostics);
        return payload;
    }

    private String regionOf(String location) {
        if (StringUtils.hasText(location)) {
            return location.split("-")[0].trim().toUpperCase();
        }
        return "R1";
    }

    private int etaMinutes(String region, String slotId) {
        int slotIndex = 1;
        try {
            slotIndex = Integer.parseInt(slotId.split("-S", 2)[1]);
        } catch (Exception ignored) {
        }
        return Math.max(2, 3 + (slotIndex % 4) + ("R1".equals(region) ? 0 : 1));
    }

    private Map<String, Object> geoPayload(GeoPoint point) {
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("lat", point.lat());
        payload.put("lng", point.lng());
        payload.put("display_name", point.displayName());
        return payload;
    }

    private String mapUrl(GeoPoint point) {
        return "https://www.openstreetmap.org/?mlat=" + point.lat() + "&mlon=" + point.lng() + "#map=18/" + point.lat() + "/" + point.lng();
    }
}

@RestController
@RequestMapping
class ParkingBusinessController {
    private final OwnerAdminFacade ownerAdminFacade;
    private final BillingService billingService;
    private final IdempotencyStore idempotencyStore;
    private final ObjectMapper objectMapper;

    @Value("${SERVICE_NAME:parking-service}")
    private String serviceName;

    ParkingBusinessController(
            OwnerAdminFacade ownerAdminFacade,
            BillingService billingService,
            IdempotencyStore idempotencyStore,
            ObjectMapper objectMapper
    ) {
        this.ownerAdminFacade = ownerAdminFacade;
        this.billingService = billingService;
        this.idempotencyStore = idempotencyStore;
        this.objectMapper = objectMapper;
    }

    @GetMapping("/api/v1/owner/recommendations")
    public ResponseEntity<Map<String, Object>> recommendations(
            @RequestParam(name = "location", defaultValue = "R1") String location,
            @RequestParam(name = "preferred_window", defaultValue = "") String preferredWindow,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("location", location);
        payload.put("preferred_window", preferredWindow);
        payload.put("billing_rule", billingService.billingRuleView());
        payload.put("results", ownerAdminFacade.recommendations(location, preferredWindow));
        return withTrace(traceId, 200, payload);
    }

    @GetMapping("/api/v1/owner/orders/{orderId}")
    public ResponseEntity<Map<String, Object>> orderDetail(
            @PathVariable("orderId") String orderId,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        Map<String, Object> payload = ownerAdminFacade.orderDetail(orderId);
        if (payload == null) {
            return withTrace(traceId, 404, Map.of("error", "order_not_found", "order_id", orderId));
        }
        return withTrace(traceId, 200, payload);
    }

    @PostMapping("/api/v1/owner/orders/{orderId}/complete")
    public ResponseEntity<Map<String, Object>> completeOrder(
            @PathVariable("orderId") String orderId,
            @RequestBody(required = false) Map<String, Object> body,
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        Map<String, Object> payload = body == null ? Map.of() : body;
        String cacheKey = StringUtils.hasText(idempotencyKey) ? "complete:" + idempotencyKey : "";
        String payloadHash = hash(orderId, payload);

        if (StringUtils.hasText(cacheKey)) {
            IdempotencyRecord cached = idempotencyStore.get(cacheKey);
            if (cached != null) {
                if (!payloadHash.equals(cached.payloadHash())) {
                    return withTrace(traceId, 409, Map.of("error", "idempotency_key_conflict", "order_id", orderId));
                }
                Map<String, Object> replay = new LinkedHashMap<>(cached.responseBody());
                replay.put("replayed", true);
                return withTrace(traceId, cached.statusCode(), replay);
            }
        }

        BillingRecordRow row = billingService.completeOrder(orderId, String.valueOf(payload.getOrDefault("ended_at", "")));
        if (row == null) {
            return withTrace(traceId, 404, Map.of("error", "order_not_found", "order_id", orderId));
        }

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("order_id", row.orderId());
        response.put("reservation_id", row.reservationId());
        response.put("billing_status", row.billingStatus());
        response.put("estimated_amount", row.estimatedAmount());
        response.put("final_amount", row.finalAmount());
        response.put("billable_minutes", row.billableMinutes());
        response.put("recognized_on", row.recognizedOn());
        response.put("currency", "CNY");

        if (StringUtils.hasText(cacheKey)) {
            idempotencyStore.save(cacheKey, new IdempotencyRecord(payloadHash, 200, response, Instant.now().getEpochSecond()));
        }

        return withTrace(traceId, 200, response);
    }

    @GetMapping("/api/v1/owner/navigation/{orderId}")
    public ResponseEntity<Map<String, Object>> navigation(
            @PathVariable("orderId") String orderId,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        Map<String, Object> payload = ownerAdminFacade.navigation(orderId);
        if (payload == null) {
            return withTrace(traceId, 404, Map.of("error", "order_not_found", "order_id", orderId));
        }
        return withTrace(traceId, 200, payload);
    }

    @GetMapping("/api/v1/admin/revenue/summary")
    public ResponseEntity<Map<String, Object>> revenueSummary(
            @RequestParam(name = "date", defaultValue = "") String date,
            @RequestParam(name = "region_id", defaultValue = "") String regionId,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        String effectiveDate = StringUtils.hasText(date) ? date : LocalDate.now(BillingService.BUSINESS_ZONE).toString();
        List<Map<String, Object>> summaries = billingService.summarizeRevenue(effectiveDate, regionId);
        double total = 0.0;
        for (Map<String, Object> item : summaries) {
            total += ((Number) item.get("revenue_amount")).doubleValue();
        }
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("date", effectiveDate);
        payload.put("region_id", regionId);
        payload.put("summaries", summaries);
        payload.put("revenue_total", BigDecimal.valueOf(total).setScale(2, RoundingMode.HALF_UP).doubleValue());
        return withTrace(traceId, 200, payload);
    }

    @GetMapping("/api/v1/admin/monitor/summary")
    public ResponseEntity<Map<String, Object>> monitorSummary(
            @RequestParam(name = "date", defaultValue = "") String date,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        String effectiveDate = StringUtils.hasText(date) ? date : LocalDate.now(BillingService.BUSINESS_ZONE).toString();
        return withTrace(traceId, 200, ownerAdminFacade.monitorSummary(effectiveDate));
    }

    private ResponseEntity<Map<String, Object>> withTrace(String traceId, int status, Map<String, Object> payload) {
        Map<String, Object> body = new LinkedHashMap<>(payload);
        body.putIfAbsent("trace_id", traceId);
        body.putIfAbsent("service", serviceName);
        return ResponseEntity.status(status).header("X-Trace-Id", traceId).body(body);
    }

    private String trace(String fromHeader) {
        if (StringUtils.hasText(fromHeader)) {
            return fromHeader;
        }
        return UUID.randomUUID().toString();
    }

    private String hash(String orderId, Map<String, Object> payload) {
        try {
            return Integer.toHexString((orderId + objectMapper.writeValueAsString(payload)).hashCode());
        } catch (Exception ex) {
            return orderId;
        }
    }
}
