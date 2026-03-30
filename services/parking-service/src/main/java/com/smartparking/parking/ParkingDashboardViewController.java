package com.smartparking.parking;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
class DashboardViewService {
    private final OwnerAdminFacade ownerAdminFacade;
    private final BillingService billingService;
    private final TrendDataService trendDataService;

    DashboardViewService(
            OwnerAdminFacade ownerAdminFacade,
            BillingService billingService,
            TrendDataService trendDataService
    ) {
        this.ownerAdminFacade = ownerAdminFacade;
        this.billingService = billingService;
        this.trendDataService = trendDataService;
    }

    Map<String, Object> ownerDashboard(String location, String preferredWindow, String userId, String orderId) {
        List<Map<String, Object>> recommendations = ownerAdminFacade.recommendations(location, preferredWindow);
        Map<String, Object> latestOrder = resolveLatestOrder(userId, orderId);
        String regionId = regionOf(location, recommendations);
        String regionLabel = recommendations.isEmpty()
                ? regionId + " 社区停车区"
                : String.valueOf(recommendations.get(0).getOrDefault("region_label", regionId + " 社区停车区"));

        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("region_id", regionId);
        summary.put("region_label", regionLabel);
        summary.put("recommendation_count", recommendations.size());
        summary.put("latest_order_id", latestOrder == null ? "" : latestOrder.getOrDefault("order_id", ""));
        summary.put("latest_billing_status", latestOrder == null ? "NONE" : latestOrder.getOrDefault("billing_status", "ESTIMATED"));
        summary.put("latest_amount", latestOrder == null ? 0.0 : latestOrder.getOrDefault("estimated_amount", 0.0));

        Map<String, Object> journey = new LinkedHashMap<>();
        // The active branch exists to keep the owner journey visible before a reservation is created.
        if (latestOrder == null) {
            journey.put("state", "ready_for_reservation");
            journey.put("message", "当前无进行中订单，可直接预约推荐车位。");
        } else {
            // The order branch exists so the UI can foreground the existing booking/billing state.
            journey.put("state", "has_recent_order");
            journey.put("message", "已识别最近订单，可继续查看账单或进入导航。");
        }

        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("location", location);
        payload.put("preferred_window", preferredWindow);
        payload.put("user_id", userId);
        payload.put("summary", summary);
        payload.put("journey", journey);
        payload.put("billing_rule", billingService.billingRuleView());
        payload.put("latest_order", latestOrder);
        payload.put("recommendations", recommendations);
        return payload;
    }

    Map<String, Object> adminDashboard(String date, String regionId, int trendDays, int trendLimit) {
        Map<String, Object> monitor = ownerAdminFacade.monitorSummary(date);
        List<Map<String, Object>> revenueTrend = trendDataService.revenueTrend(regionId, Math.max(1, trendDays));
        List<Map<String, Object>> occupancyTrend = trendDataService.occupancyTrend(regionId, Math.max(1, trendLimit));
        List<Map<String, Object>> forecastCompare = trendDataService.forecastCompare(regionId, Math.max(1, trendLimit));
        List<Map<String, Object>> revenueSummary = billingService.summarizeRevenue(date, regionId);

        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("date", date);
        summary.put("region_id", regionId);
        summary.put("active_reservations", monitor.getOrDefault("active_reservations", 0));
        summary.put("occupancy_rate", monitor.getOrDefault("occupancy_rate", 0.0));
        summary.put("revenue_total", monitor.getOrDefault("revenue_total", 0.0));
        summary.put("dispatch_strategy", monitor.getOrDefault("dispatch_strategy", "hungarian_optimal"));
        summary.put("business_view", true);

        Map<String, Object> highlights = new LinkedHashMap<>();
        highlights.put("region_count", revenueSummary.size());
        highlights.put("revenue_points", revenueTrend.size());
        highlights.put("forecast_points", forecastCompare.size());
        highlights.put("peak_occupancy", peakOccupancy(occupancyTrend));

        Map<String, Object> sections = new LinkedHashMap<>();
        sections.put("revenue_summary", revenueSummary);
        sections.put("revenue_trend", revenueTrend);
        sections.put("occupancy_trend", occupancyTrend);
        sections.put("forecast_compare", forecastCompare);

        Map<String, Object> metadata = new LinkedHashMap<>();
        metadata.put("realtime_transport", "websocket_with_polling_fallback");
        metadata.put("chart_mode", "business_dashboard");
        metadata.put("data_sources", List.of("billing_records", "forecast_feature_table", "dispatch_input_table"));

        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("summary", summary);
        payload.put("highlights", highlights);
        payload.put("sections", sections);
        payload.put("diagnostic_links", monitor.getOrDefault("diagnostic_links", Map.of()));
        payload.put("degraded_metadata", metadata);
        return payload;
    }

    private Map<String, Object> resolveLatestOrder(String userId, String orderId) {
        // The explicit order branch exists so the UI can request a precise record when one is known.
        if (StringUtils.hasText(orderId)) {
            return ownerAdminFacade.orderDetail(orderId);
        }
        // The user lookup branch exists so the owner dashboard can still surface a recent order from local context.
        if (StringUtils.hasText(userId)) {
            BillingRecordRow latestRow = billingService.getLatestOrderForUser(userId);
            if (latestRow != null) {
                return ownerAdminFacade.orderDetail(latestRow.orderId());
            }
        }
        // The empty branch exists to keep first-visit dashboards renderable without forcing order context.
        return null;
    }

    private String regionOf(String location, List<Map<String, Object>> recommendations) {
        // The location branch exists because owner dashboard requests always start from the requested target area.
        if (StringUtils.hasText(location)) {
            return location.split("-")[0].trim().toUpperCase();
        }
        // The recommendation branch exists as a fallback when the request omits location but recommendations still imply one region.
        if (!recommendations.isEmpty()) {
            String slotId = String.valueOf(recommendations.get(0).getOrDefault("slot_id", "R1-S001"));
            return slotId.split("-")[0].trim().toUpperCase();
        }
        // The default branch exists so the owner dashboard never fails to produce a stable region context.
        return "R1";
    }

    private double peakOccupancy(List<Map<String, Object>> points) {
        double peak = 0.0;
        for (Map<String, Object> point : points) {
            peak = Math.max(peak, doubleValue(point.get("occupancy_rate")));
        }
        return BigDecimal.valueOf(peak).setScale(4, RoundingMode.HALF_UP).doubleValue();
    }

    private double doubleValue(Object raw) {
        if (raw instanceof Number number) {
            return number.doubleValue();
        }
        try {
            return Double.parseDouble(String.valueOf(raw));
        } catch (Exception ex) {
            return 0.0;
        }
    }
}

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
