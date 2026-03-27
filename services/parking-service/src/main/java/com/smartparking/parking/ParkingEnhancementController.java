package com.smartparking.parking;

import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
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

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;

record SensorEventRawRow(
        String eventId,
        String slotId,
        String regionId,
        String eventTs,
        int occupied,
        String sensorSource,
        String qualityFlag,
        String businessDate,
        int hourBucket
) {
}

record LprEventRawRow(
        String eventId,
        String plateHash,
        String regionId,
        String eventType,
        String eventTs,
        String businessDate,
        int hourBucket
) {
}

record ResidentTripRawRow(
        String rawId,
        String residentId,
        String homeRegion,
        int weekday,
        int hourBucket,
        double tripProbability
) {
}

record GeoCatalogRow(
        String regionId,
        String slotId,
        double lat,
        double lng,
        String displayName,
        String mapLabel
) {
}

@Repository
class EnhancementRepository {
    private static final Logger log = LoggerFactory.getLogger(EnhancementRepository.class);

    private final JdbcTemplate jdbcTemplate;

    EnhancementRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @PostConstruct
    void initSchema() {
        List<String> ddls = List.of(
                """
                CREATE TABLE IF NOT EXISTS sensor_event_raw (
                  event_id VARCHAR(64) PRIMARY KEY,
                  slot_id VARCHAR(64) NOT NULL,
                  region_id VARCHAR(32) NOT NULL,
                  event_ts VARCHAR(64) NOT NULL,
                  occupied TINYINT NOT NULL,
                  sensor_source VARCHAR(64) NOT NULL,
                  quality_flag VARCHAR(32) NOT NULL,
                  business_date VARCHAR(16) NOT NULL,
                  hour_bucket INT NOT NULL,
                  created_at DOUBLE NOT NULL
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
                """,
                """
                CREATE TABLE IF NOT EXISTS lpr_event_raw (
                  event_id VARCHAR(64) PRIMARY KEY,
                  plate_hash VARCHAR(128) NOT NULL,
                  region_id VARCHAR(32) NOT NULL,
                  event_type VARCHAR(16) NOT NULL,
                  event_ts VARCHAR(64) NOT NULL,
                  business_date VARCHAR(16) NOT NULL,
                  hour_bucket INT NOT NULL,
                  created_at DOUBLE NOT NULL
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
                """,
                """
                CREATE TABLE IF NOT EXISTS resident_trip_raw (
                  raw_id VARCHAR(64) PRIMARY KEY,
                  resident_id VARCHAR(64) NOT NULL,
                  home_region VARCHAR(32) NOT NULL,
                  weekday INT NOT NULL,
                  hour_bucket INT NOT NULL,
                  trip_probability DOUBLE NOT NULL,
                  created_at DOUBLE NOT NULL
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
                """,
                """
                CREATE TABLE IF NOT EXISTS geo_catalog (
                  slot_id VARCHAR(64) PRIMARY KEY,
                  region_id VARCHAR(32) NOT NULL,
                  lat DOUBLE NOT NULL,
                  lng DOUBLE NOT NULL,
                  display_name VARCHAR(128) NOT NULL,
                  map_label VARCHAR(128) NOT NULL,
                  created_at DOUBLE NOT NULL
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
                """
        );
        RuntimeException last = null;
        for (int i = 0; i < 60; i++) {
            try {
                for (String ddl : ddls) {
                    jdbcTemplate.execute(ddl);
                }
                seedGeoCatalog();
                log.info("enhancement schema ready");
                return;
            } catch (RuntimeException ex) {
                last = ex;
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw new RuntimeException("enhancement schema init interrupted", ie);
                }
            }
        }
        throw new RuntimeException("enhancement schema init failed after retry", last);
    }

    private void seedGeoCatalog() {
        Integer count = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM geo_catalog", Integer.class);
        if (count != null && count > 0) {
            return;
        }
        double now = Instant.now().toEpochMilli() / 1000.0;
        for (String region : List.of("R1", "R2", "R3")) {
            for (int i = 1; i <= 12; i++) {
                double[] point = basePoint(region, i);
                String slotId = String.format(Locale.ROOT, "%s-S%03d", region, i);
                jdbcTemplate.update(
                        "INSERT INTO geo_catalog (slot_id, region_id, lat, lng, display_name, map_label, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        slotId,
                        region,
                        point[0],
                        point[1],
                        region + " 区车位 " + slotId,
                        region + " 社区停车区",
                        now
                );
            }
        }
    }

    private double[] basePoint(String region, int index) {
        double baseLat;
        double baseLng;
        switch (region) {
            case "R1" -> {
                baseLat = 31.2304;
                baseLng = 121.4737;
            }
            case "R2" -> {
                baseLat = 31.2243;
                baseLng = 121.4768;
            }
            case "R3" -> {
                baseLat = 31.2187;
                baseLng = 121.4810;
            }
            default -> {
                baseLat = 31.2304;
                baseLng = 121.4737;
            }
        }
        return new double[]{
                baseLat + ((index % 5) - 2) * 0.0009,
                baseLng + (((index / 5) % 5) - 2) * 0.0011
        };
    }

    int insertSensorEvents(List<SensorEventRawRow> rows) {
        String sql = """
                INSERT INTO sensor_event_raw (
                  event_id, slot_id, region_id, event_ts, occupied, sensor_source, quality_flag, business_date, hour_bucket, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON DUPLICATE KEY UPDATE
                  occupied = VALUES(occupied),
                  sensor_source = VALUES(sensor_source),
                  quality_flag = VALUES(quality_flag),
                  business_date = VALUES(business_date),
                  hour_bucket = VALUES(hour_bucket)
                """;
        int inserted = 0;
        double now = Instant.now().toEpochMilli() / 1000.0;
        for (SensorEventRawRow row : rows) {
            inserted += jdbcTemplate.update(sql, row.eventId(), row.slotId(), row.regionId(), row.eventTs(), row.occupied(), row.sensorSource(), row.qualityFlag(), row.businessDate(), row.hourBucket(), now);
        }
        return inserted;
    }

    int insertLprEvents(List<LprEventRawRow> rows) {
        String sql = """
                INSERT INTO lpr_event_raw (
                  event_id, plate_hash, region_id, event_type, event_ts, business_date, hour_bucket, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON DUPLICATE KEY UPDATE
                  plate_hash = VALUES(plate_hash),
                  event_type = VALUES(event_type),
                  business_date = VALUES(business_date),
                  hour_bucket = VALUES(hour_bucket)
                """;
        int inserted = 0;
        double now = Instant.now().toEpochMilli() / 1000.0;
        for (LprEventRawRow row : rows) {
            inserted += jdbcTemplate.update(sql, row.eventId(), row.plateHash(), row.regionId(), row.eventType(), row.eventTs(), row.businessDate(), row.hourBucket(), now);
        }
        return inserted;
    }

    int insertResidentPatterns(List<ResidentTripRawRow> rows) {
        String sql = """
                INSERT INTO resident_trip_raw (
                  raw_id, resident_id, home_region, weekday, hour_bucket, trip_probability, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON DUPLICATE KEY UPDATE
                  weekday = VALUES(weekday),
                  hour_bucket = VALUES(hour_bucket),
                  trip_probability = VALUES(trip_probability)
                """;
        int inserted = 0;
        double now = Instant.now().toEpochMilli() / 1000.0;
        for (ResidentTripRawRow row : rows) {
            inserted += jdbcTemplate.update(sql, row.rawId(), row.residentId(), row.homeRegion(), row.weekday(), row.hourBucket(), row.tripProbability(), now);
        }
        return inserted;
    }

    GeoCatalogRow findGeoCatalog(String slotId, String regionId) {
        List<GeoCatalogRow> rows = jdbcTemplate.query(
                "SELECT region_id, slot_id, lat, lng, display_name, map_label FROM geo_catalog WHERE slot_id = ? LIMIT 1",
                this::mapGeo,
                slotId
        );
        if (!rows.isEmpty()) {
            return rows.get(0);
        }
        List<GeoCatalogRow> regionalRows = jdbcTemplate.query(
                "SELECT region_id, slot_id, lat, lng, display_name, map_label FROM geo_catalog WHERE region_id = ? ORDER BY slot_id LIMIT 1",
                this::mapGeo,
                regionId
        );
        return regionalRows.isEmpty() ? null : regionalRows.get(0);
    }

    List<Map<String, Object>> revenueTrend(String regionId, int days) {
        String sql = """
                SELECT recognized_on AS point_date, SUM(final_amount) AS revenue_amount, COUNT(*) AS order_count
                FROM billing_records
                WHERE billing_status = 'CONFIRMED'
                  AND recognized_on >= ?
                  AND (? = '' OR region_id = ?)
                GROUP BY recognized_on
                ORDER BY recognized_on
                """;
        LocalDate from = LocalDate.now(BillingService.BUSINESS_ZONE).minusDays(Math.max(days - 1, 0));
        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("date", rs.getString("point_date"));
            item.put("revenue_amount", rs.getDouble("revenue_amount"));
            item.put("order_count", rs.getInt("order_count"));
            return item;
        }, from.toString(), regionId, regionId);
    }

    private GeoCatalogRow mapGeo(ResultSet rs, int rowNum) throws SQLException {
        return new GeoCatalogRow(
                rs.getString("region_id"),
                rs.getString("slot_id"),
                rs.getDouble("lat"),
                rs.getDouble("lng"),
                rs.getString("display_name"),
                rs.getString("map_label")
        );
    }
}

@Service
class GeoCatalogService {
    private final EnhancementRepository repository;

    GeoCatalogService(EnhancementRepository repository) {
        this.repository = repository;
    }

    GeoPoint resolveGeoPoint(String slotId, String regionId) {
        GeoCatalogRow row = repository.findGeoCatalog(slotId, regionId);
        if (row == null) {
            return new GeoPoint(31.2304, 121.4737, regionId + " 区车位 " + slotId);
        }
        return new GeoPoint(row.lat(), row.lng(), row.displayName());
    }

    String regionLabel(String regionId) {
        GeoCatalogRow row = repository.findGeoCatalog(regionId + "-S001", regionId);
        if (row != null && StringUtils.hasText(row.mapLabel())) {
            return row.mapLabel();
        }
        return regionId + " 社区停车区";
    }

    double distanceKm(String regionId, String slotId) {
        GeoPoint point = resolveGeoPoint(slotId, regionId);
        double centerLat = 31.2304;
        double centerLng = 121.4737;
        double dLat = point.lat() - centerLat;
        double dLng = point.lng() - centerLng;
        return Math.round(Math.sqrt(dLat * dLat + dLng * dLng) * 1110.0) / 100.0;
    }
}

@Service
class TrendDataService {
    private static final Logger log = LoggerFactory.getLogger(TrendDataService.class);

    private final EnhancementRepository repository;

    @Value("${SMART_PARKING_DATA_ROOT:/workspace/data}")
    private String dataRoot;

    TrendDataService(EnhancementRepository repository) {
        this.repository = repository;
    }

    List<Map<String, Object>> revenueTrend(String regionId, int days) {
        return repository.revenueTrend(regionId, days);
    }

    List<Map<String, Object>> occupancyTrend(String regionId, int limit) {
        List<Map<String, String>> rows = readCsvRows(Path.of(dataRoot, "processed", "forecast_feature_table.csv"));
        List<Map<String, Object>> points = new ArrayList<>();
        for (Map<String, String> row : rows) {
            String rowRegion = row.getOrDefault("region_id", "");
            if (StringUtils.hasText(regionId) && !regionId.equalsIgnoreCase(rowRegion)) {
                continue;
            }
            Map<String, Object> point = new LinkedHashMap<>();
            point.put("ts", row.getOrDefault("ts", ""));
            point.put("region_id", rowRegion);
            point.put("occupancy_rate", parseDouble(row.getOrDefault("occupancy_rate", "0")));
            point.put("active_supply", parseDouble(row.getOrDefault("supply_proxy", "0")));
            points.add(point);
        }
        return tail(points, limit);
    }

    List<Map<String, Object>> forecastCompare(String regionId, int limit) {
        List<Map<String, String>> rows = readCsvRows(Path.of(dataRoot, "processed", "forecast_feature_table.csv"));
        List<Map<String, Object>> points = new ArrayList<>();
        for (Map<String, String> row : rows) {
            String rowRegion = row.getOrDefault("region_id", "");
            if (StringUtils.hasText(regionId) && !regionId.equalsIgnoreCase(rowRegion)) {
                continue;
            }
            double predictedGap = parseDouble(row.getOrDefault("gap_proxy", "0"));
            double actualGap = parseDouble(row.getOrDefault("vehicle_in_count", "0")) - parseDouble(row.getOrDefault("vehicle_out_count", "0"));
            Map<String, Object> point = new LinkedHashMap<>();
            point.put("ts", row.getOrDefault("ts", ""));
            point.put("region_id", rowRegion);
            point.put("predicted_gap", predictedGap);
            point.put("actual_gap", actualGap);
            points.add(point);
        }
        return tail(points, limit);
    }

    private List<Map<String, Object>> tail(List<Map<String, Object>> rows, int limit) {
        if (rows.isEmpty()) {
            return fallbackRows(limit);
        }
        int effectiveLimit = Math.max(1, limit);
        int start = Math.max(0, rows.size() - effectiveLimit);
        return new ArrayList<>(rows.subList(start, rows.size()));
    }

    private List<Map<String, Object>> fallbackRows(int limit) {
        List<Map<String, Object>> rows = new ArrayList<>();
        int count = Math.max(3, limit);
        for (int i = count - 1; i >= 0; i--) {
            ZonedDateTime point = ZonedDateTime.now(ZoneOffset.UTC).minusHours(i);
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("ts", point.toString());
            row.put("region_id", "R1");
            row.put("occupancy_rate", 0.42 + ((count - i) * 0.03));
            row.put("active_supply", 8.0);
            row.put("predicted_gap", -1.2 + ((count - i) * 0.2));
            row.put("actual_gap", -1.0 + ((count - i) * 0.18));
            rows.add(row);
        }
        return rows;
    }

    private List<Map<String, String>> readCsvRows(Path path) {
        try {
            if (!Files.exists(path)) {
                return List.of();
            }
            List<String> lines = Files.readAllLines(path, StandardCharsets.UTF_8);
            if (lines.size() < 2) {
                return List.of();
            }
            String[] headers = lines.get(0).split(",");
            List<Map<String, String>> rows = new ArrayList<>();
            for (int i = 1; i < lines.size(); i++) {
                String line = lines.get(i).trim();
                if (!StringUtils.hasText(line)) {
                    continue;
                }
                String[] values = line.split(",", -1);
                Map<String, String> row = new HashMap<>();
                for (int j = 0; j < headers.length && j < values.length; j++) {
                    row.put(headers[j], values[j]);
                }
                rows.add(row);
            }
            return rows;
        } catch (Exception ex) {
            log.warn("failed to read trend csv {} due to {}", path, ex.getMessage());
            return List.of();
        }
    }

    private double parseDouble(String raw) {
        try {
            return Double.parseDouble(raw);
        } catch (Exception ex) {
            return 0.0;
        }
    }
}

@RestController
@RequestMapping
class ParkingEnhancementController {
    private final EnhancementRepository enhancementRepository;
    private final TrendDataService trendDataService;

    @Value("${SERVICE_NAME:parking-service}")
    private String serviceName;

    ParkingEnhancementController(EnhancementRepository enhancementRepository, TrendDataService trendDataService) {
        this.enhancementRepository = enhancementRepository;
        this.trendDataService = trendDataService;
    }

    @PostMapping("/internal/v1/ingest/sensor-events")
    public ResponseEntity<Map<String, Object>> ingestSensorEvents(
            @RequestBody Map<String, Object> body,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        List<SensorEventRawRow> rows = new ArrayList<>();
        for (Map<String, Object> item : itemsOf(body)) {
            String slotId = text(item.getOrDefault("slot_id", "R1-S001"));
            String regionId = regionFrom(text(item.get("region_id")), slotId);
            Instant eventTs = parseInstant(text(item.get("event_ts")));
            ZonedDateTime business = eventTs.atZone(BillingService.BUSINESS_ZONE);
            rows.add(new SensorEventRawRow(
                    textOrId(item.get("event_id"), "sensor"),
                    slotId,
                    regionId,
                    eventTs.toString(),
                    parseInt(item.getOrDefault("occupied", 0), 0) > 0 ? 1 : 0,
                    text(item.getOrDefault("sensor_source", "iot-sim")),
                    text(item.getOrDefault("quality_flag", "normal")),
                    business.toLocalDate().toString(),
                    business.getHour()
            ));
        }
        return withTrace(traceId, Map.of(
                "accepted", true,
                "table", "sensor_event_raw",
                "inserted_count", enhancementRepository.insertSensorEvents(rows)
        ));
    }

    @PostMapping("/internal/v1/ingest/lpr-events")
    public ResponseEntity<Map<String, Object>> ingestLprEvents(
            @RequestBody Map<String, Object> body,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        List<LprEventRawRow> rows = new ArrayList<>();
        for (Map<String, Object> item : itemsOf(body)) {
            String regionId = regionFrom(text(item.get("region_id")), "");
            Instant eventTs = parseInstant(text(item.get("event_ts")));
            ZonedDateTime business = eventTs.atZone(BillingService.BUSINESS_ZONE);
            rows.add(new LprEventRawRow(
                    textOrId(item.get("event_id"), "lpr"),
                    hashPlate(item),
                    regionId,
                    normalizeEventType(text(item.getOrDefault("event_type", "in"))),
                    eventTs.toString(),
                    business.toLocalDate().toString(),
                    business.getHour()
            ));
        }
        return withTrace(traceId, Map.of(
                "accepted", true,
                "table", "lpr_event_raw",
                "inserted_count", enhancementRepository.insertLprEvents(rows)
        ));
    }

    @PostMapping("/internal/v1/ingest/resident-patterns")
    public ResponseEntity<Map<String, Object>> ingestResidentPatterns(
            @RequestBody Map<String, Object> body,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        List<ResidentTripRawRow> rows = new ArrayList<>();
        for (Map<String, Object> item : itemsOf(body)) {
            rows.add(new ResidentTripRawRow(
                    textOrId(item.get("raw_id"), "resident"),
                    text(item.getOrDefault("resident_id", "resident-demo-001")),
                    regionFrom(text(item.getOrDefault("home_region", item.get("region_id"))), ""),
                    Math.max(1, Math.min(7, parseInt(item.getOrDefault("weekday", 1), 1))),
                    Math.max(0, Math.min(23, parseInt(item.getOrDefault("hour_bucket", 8), 8))),
                    Math.max(0.0, Math.min(1.0, parseDouble(item.getOrDefault("trip_probability", 0.35), 0.35)))
            ));
        }
        return withTrace(traceId, Map.of(
                "accepted", true,
                "table", "resident_trip_raw",
                "inserted_count", enhancementRepository.insertResidentPatterns(rows)
        ));
    }

    @GetMapping("/api/v1/admin/revenue/trend")
    public ResponseEntity<Map<String, Object>> revenueTrend(
            @RequestParam(name = "region_id", defaultValue = "") String regionId,
            @RequestParam(name = "days", defaultValue = "7") int days,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        return withTrace(traceId, Map.of(
                "region_id", regionId,
                "days", days,
                "points", trendDataService.revenueTrend(regionId, Math.max(1, days))
        ));
    }

    @GetMapping("/api/v1/admin/occupancy/trend")
    public ResponseEntity<Map<String, Object>> occupancyTrend(
            @RequestParam(name = "region_id", defaultValue = "") String regionId,
            @RequestParam(name = "limit", defaultValue = "12") int limit,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        return withTrace(traceId, Map.of(
                "region_id", regionId,
                "points", trendDataService.occupancyTrend(regionId, Math.max(1, limit))
        ));
    }

    @GetMapping("/api/v1/admin/forecast/compare")
    public ResponseEntity<Map<String, Object>> forecastCompare(
            @RequestParam(name = "region_id", defaultValue = "") String regionId,
            @RequestParam(name = "limit", defaultValue = "12") int limit,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        return withTrace(traceId, Map.of(
                "region_id", regionId,
                "points", trendDataService.forecastCompare(regionId, Math.max(1, limit))
        ));
    }

    private ResponseEntity<Map<String, Object>> withTrace(String traceId, Map<String, Object> payload) {
        Map<String, Object> body = new LinkedHashMap<>(payload);
        body.put("trace_id", traceId);
        body.put("service", serviceName);
        return ResponseEntity.ok().header("X-Trace-Id", traceId).body(body);
    }

    private String trace(String fromHeader) {
        if (StringUtils.hasText(fromHeader)) {
            return fromHeader;
        }
        return UUID.randomUUID().toString();
    }

    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> itemsOf(Map<String, Object> body) {
        Object raw = body.get("events");
        if (raw == null) {
            raw = body.get("items");
        }
        if (raw == null && body.containsKey("data")) {
            raw = body.get("data");
        }
        if (raw instanceof List<?> list) {
            List<Map<String, Object>> rows = new ArrayList<>();
            for (Object item : list) {
                if (item instanceof Map<?, ?> map) {
                    rows.add((Map<String, Object>) map);
                }
            }
            return rows;
        }
        return List.of(body);
    }

    private String text(Object value) {
        return value == null ? "" : String.valueOf(value).trim();
    }

    private String textOrId(Object value, String prefix) {
        String text = text(value);
        return StringUtils.hasText(text) ? text : prefix + "-" + UUID.randomUUID().toString().replace("-", "").substring(0, 12);
    }

    private String regionFrom(String preferredRegion, String slotId) {
        if (StringUtils.hasText(preferredRegion)) {
            return preferredRegion.trim().toUpperCase(Locale.ROOT);
        }
        if (StringUtils.hasText(slotId) && slotId.contains("-")) {
            return slotId.split("-", 2)[0].trim().toUpperCase(Locale.ROOT);
        }
        return "R1";
    }

    private Instant parseInstant(String raw) {
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
        return Instant.now();
    }

    private int parseInt(Object value, int defaultValue) {
        try {
            return Integer.parseInt(String.valueOf(value));
        } catch (Exception ex) {
            return defaultValue;
        }
    }

    private double parseDouble(Object value, double defaultValue) {
        try {
            return Double.parseDouble(String.valueOf(value));
        } catch (Exception ex) {
            return defaultValue;
        }
    }

    private String normalizeEventType(String eventType) {
        return "out".equalsIgnoreCase(eventType) ? "out" : "in";
    }

    private String hashPlate(Map<String, Object> item) {
        String plateHash = text(item.get("plate_hash"));
        if (StringUtils.hasText(plateHash)) {
            return plateHash;
        }
        String rawPlate = text(item.get("plate"));
        if (!StringUtils.hasText(rawPlate)) {
            rawPlate = "PLATE-UNKNOWN";
        }
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(rawPlate.toUpperCase(Locale.ROOT).getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte value : hash) {
                sb.append(String.format(Locale.ROOT, "%02x", value));
            }
            return sb.toString();
        } catch (Exception ex) {
            return Integer.toHexString(rawPlate.hashCode());
        }
    }
}
