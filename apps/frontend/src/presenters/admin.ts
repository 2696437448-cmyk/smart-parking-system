import type { AdminDashboardView } from "../types/dashboard";
import { formatCurrency, formatPercent } from "./format";

export function adminChartCards(dashboard: AdminDashboardView | null) {
  return [
    {
      title: "今日收益",
      value: formatCurrency(dashboard?.summary.revenue_total),
      note: "billing_records 汇总",
      tone: "accent" as const,
    },
    {
      title: "峰值占用率",
      value: formatPercent(dashboard?.highlights.peak_occupancy),
      note: "最近图表采样区间",
      tone: "calm" as const,
    },
  ];
}

export function adminStatusSummary(dashboard: AdminDashboardView | null) {
  return {
    dispatchBadge: dashboard?.summary.dispatch_strategy ?? "hungarian_optimal",
    degradedHint: dashboard?.degraded_metadata?.realtime_transport ?? "websocket_with_polling_fallback",
  };
}
