package com.smartparking.parking;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping
class ParkingDashboardViewController {
    private final DashboardViewService dashboardViewService;

    @Value("${SERVICE_NAME:parking-service}")
    private String serviceName;

    ParkingDashboardViewController(DashboardViewService dashboardViewService) {
        this.dashboardViewService = dashboardViewService;
    }

    @GetMapping("/api/v1/owner/dashboard")
    public ResponseEntity<Map<String, Object>> ownerDashboard(
            @RequestParam(name = "location", defaultValue = "R1") String location,
            @RequestParam(name = "preferred_window", defaultValue = "") String preferredWindow,
            @RequestParam(name = "user_id", defaultValue = "") String userId,
            @RequestParam(name = "order_id", defaultValue = "") String orderId,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        return withTrace(traceId, dashboardViewService.ownerDashboard(location, preferredWindow, userId, orderId));
    }

    @GetMapping("/api/v1/admin/dashboard")
    public ResponseEntity<Map<String, Object>> adminDashboard(
            @RequestParam(name = "date", defaultValue = "") String date,
            @RequestParam(name = "region_id", defaultValue = "") String regionId,
            @RequestParam(name = "trend_days", defaultValue = "7") int trendDays,
            @RequestParam(name = "trend_limit", defaultValue = "12") int trendLimit,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceHeader
    ) {
        String traceId = trace(traceHeader);
        String effectiveDate = StringUtils.hasText(date) ? date : LocalDate.now(BillingService.BUSINESS_ZONE).toString();
        return withTrace(traceId, dashboardViewService.adminDashboard(effectiveDate, regionId, trendDays, trendLimit));
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
}
