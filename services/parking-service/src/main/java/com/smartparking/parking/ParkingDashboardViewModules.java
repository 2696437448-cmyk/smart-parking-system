package com.smartparking.parking;

import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

record OwnerDashboardQueryResult(
        String location,
        String preferredWindow,
        String userId,
        String regionId,
        String regionLabel,
        Map<String, Object> billingRule,
        Map<String, Object> latestOrder,
        List<Map<String, Object>> recommendations
) {
}

record AdminDashboardQueryResult(
        String date,
        String regionId,
        Map<String, Object> monitor,
        List<Map<String, Object>> revenueSummary,
        List<Map<String, Object>> revenueTrend,
        List<Map<String, Object>> occupancyTrend,
        List<Map<String, Object>> forecastCompare
) {
}

@Service
class DashboardQueryService {
    private final OwnerAdminFacade ownerAdminFacade;
    private final BillingService billingService;
    private final TrendDataService trendDataService;

    DashboardQueryService(
            OwnerAdminFacade ownerAdminFacade,
            BillingService billingService,
            TrendDataService trendDataService
    ) {
        this.ownerAdminFacade = ownerAdminFacade;
        this.billingService = billingService;
        this.trendDataService = trendDataService;
    }

    OwnerDashboardQueryResult ownerDashboard(String location, String preferredWindow, String userId, String orderId) {
        List<Map<String, Object>> recommendations = ownerAdminFacade.recommendations(location, preferredWindow);
        Map<String, Object> latestOrder = resolveLatestOrder(userId, orderId);
        String regionId = regionOf(location, recommendations);
        String regionLabel = recommendations.isEmpty()
                ? regionId + " 社区停车区"
                : String.valueOf(recommendations.get(0).getOrDefault("region_label", regionId + " 社区停车区"));
        return new OwnerDashboardQueryResult(
                location,
                preferredWindow,
                userId,
                regionId,
                regionLabel,
                billingService.billingRuleView(),
                latestOrder,
                recommendations
        );
    }

    AdminDashboardQueryResult adminDashboard(String date, String regionId, int trendDays, int trendLimit) {
        Map<String, Object> monitor = ownerAdminFacade.monitorSummary(date);
        List<Map<String, Object>> revenueSummary = billingService.summarizeRevenue(date, regionId);
        List<Map<String, Object>> revenueTrend = trendDataService.revenueTrend(regionId, Math.max(1, trendDays));
        List<Map<String, Object>> occupancyTrend = trendDataService.occupancyTrend(regionId, Math.max(1, trendLimit));
        List<Map<String, Object>> forecastCompare = trendDataService.forecastCompare(regionId, Math.max(1, trendLimit));
        return new AdminDashboardQueryResult(date, regionId, monitor, revenueSummary, revenueTrend, occupancyTrend, forecastCompare);
    }

    private Map<String, Object> resolveLatestOrder(String userId, String orderId) {
        if (StringUtils.hasText(orderId)) {
            return ownerAdminFacade.orderDetail(orderId);
        }
        if (StringUtils.hasText(userId)) {
            BillingRecordRow latestRow = billingService.getLatestOrderForUser(userId);
            if (latestRow != null) {
                return ownerAdminFacade.orderDetail(latestRow.orderId());
            }
        }
        return null;
    }

    private String regionOf(String location, List<Map<String, Object>> recommendations) {
        if (StringUtils.hasText(location)) {
            return location.split("-")[0].trim().toUpperCase();
        }
        if (!recommendations.isEmpty()) {
            String slotId = String.valueOf(recommendations.get(0).getOrDefault("slot_id", "R1-S001"));
            return slotId.split("-")[0].trim().toUpperCase();
        }
        return "R1";
    }
}

@Service
class OwnerDashboardAssembler {
    Map<String, Object> assemble(OwnerDashboardQueryResult query) {
        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("region_id", query.regionId());
        summary.put("region_label", query.regionLabel());
        summary.put("recommendation_count", query.recommendations().size());
        summary.put("latest_order_id", query.latestOrder() == null ? "" : query.latestOrder().getOrDefault("order_id", ""));
        summary.put("latest_billing_status", query.latestOrder() == null ? "NONE" : query.latestOrder().getOrDefault("billing_status", "ESTIMATED"));
        summary.put("latest_amount", query.latestOrder() == null ? 0.0 : query.latestOrder().getOrDefault("estimated_amount", 0.0));

        Map<String, Object> journey = new LinkedHashMap<>();
        if (query.latestOrder() == null) {
            journey.put("state", "ready_for_reservation");
            journey.put("message", "当前无进行中订单，可直接预约推荐车位。");
        } else {
            journey.put("state", "has_recent_order");
            journey.put("message", "已识别最近订单，可继续查看账单或进入导航。");
        }

        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("location", query.location());
        payload.put("preferred_window", query.preferredWindow());
        payload.put("user_id", query.userId());
        payload.put("summary", summary);
        payload.put("journey", journey);
        payload.put("billing_rule", query.billingRule());
        payload.put("latest_order", query.latestOrder());
        payload.put("recommendations", query.recommendations());
        return payload;
    }
}

@Service
class AdminDashboardAssembler {
    Map<String, Object> assemble(AdminDashboardQueryResult query) {
        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("date", query.date());
        summary.put("region_id", query.regionId());
        summary.put("active_reservations", query.monitor().getOrDefault("active_reservations", 0));
        summary.put("occupancy_rate", query.monitor().getOrDefault("occupancy_rate", 0.0));
        summary.put("revenue_total", query.monitor().getOrDefault("revenue_total", 0.0));
        summary.put("dispatch_strategy", query.monitor().getOrDefault("dispatch_strategy", "hungarian_optimal"));
        summary.put("business_view", true);

        Map<String, Object> highlights = new LinkedHashMap<>();
        highlights.put("region_count", query.revenueSummary().size());
        highlights.put("revenue_points", query.revenueTrend().size());
        highlights.put("forecast_points", query.forecastCompare().size());
        highlights.put("peak_occupancy", peakOccupancy(query.occupancyTrend()));

        Map<String, Object> sections = new LinkedHashMap<>();
        sections.put("revenue_summary", query.revenueSummary());
        sections.put("revenue_trend", query.revenueTrend());
        sections.put("occupancy_trend", query.occupancyTrend());
        sections.put("forecast_compare", query.forecastCompare());

        Map<String, Object> metadata = new LinkedHashMap<>();
        metadata.put("realtime_transport", "websocket_with_polling_fallback");
        metadata.put("chart_mode", "business_dashboard");
        metadata.put("data_sources", List.of("billing_records", "forecast_feature_table", "dispatch_input_table"));

        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("summary", summary);
        payload.put("highlights", highlights);
        payload.put("sections", sections);
        payload.put("diagnostic_links", query.monitor().getOrDefault("diagnostic_links", Map.of()));
        payload.put("degraded_metadata", metadata);
        return payload;
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

@Service
class DashboardViewService {
    private final DashboardQueryService dashboardQueryService;
    private final OwnerDashboardAssembler ownerDashboardAssembler;
    private final AdminDashboardAssembler adminDashboardAssembler;

    DashboardViewService(
            DashboardQueryService dashboardQueryService,
            OwnerDashboardAssembler ownerDashboardAssembler,
            AdminDashboardAssembler adminDashboardAssembler
    ) {
        this.dashboardQueryService = dashboardQueryService;
        this.ownerDashboardAssembler = ownerDashboardAssembler;
        this.adminDashboardAssembler = adminDashboardAssembler;
    }

    Map<String, Object> ownerDashboard(String location, String preferredWindow, String userId, String orderId) {
        return ownerDashboardAssembler.assemble(dashboardQueryService.ownerDashboard(location, preferredWindow, userId, orderId));
    }

    Map<String, Object> adminDashboard(String date, String regionId, int trendDays, int trendLimit) {
        return adminDashboardAssembler.assemble(dashboardQueryService.adminDashboard(date, regionId, trendDays, trendLimit));
    }
}
