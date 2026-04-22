import type { NavigationView, OwnerDashboardView, OrderDetail } from "../types/dashboard";
import { formatCurrency, formatDatetimeLabel } from "./format";

export function ownerDashboardHero(summary: OwnerDashboardView["summary"] | null | undefined) {
  return {
    eyebrow: "Owner Journey",
    badge: summary?.region_label ?? "智慧停车",
    helper: `当前共整理 ${summary?.recommendation_count ?? 0} 个候选车位，最近账单状态为 ${summary?.latest_billing_status ?? "NONE"}。`,
  };
}

export function ownerOrderMetaItems(orderDetail: OrderDetail | null | undefined) {
  if (!orderDetail) {
    return [];
  }
  return [
    { label: "开始时间", value: formatDatetimeLabel(orderDetail.started_at) },
    { label: "结束时间", value: formatDatetimeLabel(orderDetail.ended_at) },
    { label: "结算日期", value: orderDetail.recognized_on || "未结算" },
    {
      label: "计费规则",
      value: `${orderDetail.billing_rule?.timezone ?? "Asia/Shanghai"} / ${orderDetail.billing_rule?.unit_minutes ?? 15} 分钟`,
    },
  ];
}

export function ownerOrderAmounts(orderDetail: OrderDetail | null | undefined) {
  if (!orderDetail) {
    return [];
  }
  return [
    { label: "预估金额", value: formatCurrency(orderDetail.estimated_amount) },
    { label: "最终金额", value: formatCurrency(orderDetail.final_amount) },
  ];
}

export function routeSummaryLines(input: NavigationView | null | undefined) {
  return [
    `预计到达：${input?.eta_minutes ?? 0} 分钟`,
    `路线摘要：${input?.route_summary?.summary ?? "社区内部推荐路线"}`,
    `距离：${input?.route_summary?.distance_km ?? 0} km`,
  ];
}

export function ownerNavigationMetaItems(navigation: NavigationView | null | undefined) {
  if (!navigation) {
    return [];
  }
  return [
    { label: "订单号", value: navigation.order_id },
    { label: "目标车位", value: navigation.slot_display_name ?? navigation.slot_id },
    { label: "区域", value: navigation.region_label },
    { label: "预计到达", value: `${navigation.eta_minutes} 分钟` },
    { label: "路线摘要", value: navigation.route_summary?.summary ?? "社区内部推荐路线" },
    { label: "距离", value: `${navigation.route_summary?.distance_km ?? 0} km` },
  ];
}
