import type { AdminDashboardView } from "../types/dashboard";
import { gatewayUrl, requestJson } from "./http";

export interface AdminDashboardParams {
  date: string;
  regionId?: string;
  trendDays?: number;
  trendLimit?: number;
}

export async function fetchAdminDashboard(params: AdminDashboardParams) {
  return requestJson<AdminDashboardView>(
    "admin-dashboard",
    gatewayUrl("/api/v1/admin/dashboard", {
      date: params.date,
      region_id: params.regionId ?? "",
      trend_days: params.trendDays ?? 7,
      trend_limit: params.trendLimit ?? 12,
    }),
  );
}
