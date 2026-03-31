export interface ServiceEnvelope {
  trace_id: string;
  service: string;
}

export interface BillingRuleView {
  timezone: string;
  unit_minutes: number;
  rounding_mode: string;
  effective_window: string;
}

export interface DestinationPoint {
  lat: number;
  lng: number;
  display_name: string;
}

export interface RouteSummaryView {
  distance_km: number;
  route_mode: string;
  summary: string;
  eta_minutes: number;
}

export interface RecommendationItem {
  slot_id: string;
  slot_display_name?: string;
  estimated_amount: number;
  eta_minutes: number;
  region_label?: string;
  destination?: DestinationPoint;
  map_url: string;
}

export interface OrderDetail extends ServiceEnvelope {
  order_id: string;
  reservation_id: string;
  user_id: string;
  slot_id: string;
  region_id: string;
  started_at: string;
  ended_at: string;
  billable_minutes: number;
  estimated_amount: number;
  final_amount: number;
  billing_status: string;
  recognized_on: string;
  billing_rule?: BillingRuleView;
}

export interface NavigationView extends ServiceEnvelope {
  order_id: string;
  slot_id: string;
  eta_minutes: number;
  map_url: string;
  region_label: string;
  slot_display_name?: string;
  destination?: DestinationPoint;
  route_summary?: RouteSummaryView;
}

export interface OwnerDashboardView extends ServiceEnvelope {
  location: string;
  preferred_window: string;
  user_id: string;
  summary: {
    region_id: string;
    region_label: string;
    recommendation_count: number;
    latest_order_id: string;
    latest_billing_status: string;
    latest_amount: number;
  };
  journey: {
    state: string;
    message: string;
  };
  billing_rule: BillingRuleView;
  latest_order: OrderDetail | null;
  recommendations: RecommendationItem[];
}

export interface RevenueSummaryItem {
  date: string;
  region_id: string;
  revenue_amount: number;
  order_count: number;
  utilization_rate: number;
}

export interface RevenueTrendPoint {
  date: string;
  revenue_amount: number;
  order_count: number;
}

export interface OccupancyTrendPoint {
  ts: string;
  region_id: string;
  occupancy_rate: number;
  active_supply: number;
}

export interface ForecastComparePoint {
  ts: string;
  region_id: string;
  predicted_gap: number;
  actual_gap: number;
}

export interface AdminDashboardView extends ServiceEnvelope {
  summary: {
    date: string;
    region_id: string;
    active_reservations: number;
    occupancy_rate: number;
    revenue_total: number;
    dispatch_strategy: string;
    business_view: boolean;
  };
  highlights: {
    region_count: number;
    revenue_points: number;
    forecast_points: number;
    peak_occupancy: number;
  };
  sections: {
    revenue_summary: RevenueSummaryItem[];
    revenue_trend: RevenueTrendPoint[];
    occupancy_trend: OccupancyTrendPoint[];
    forecast_compare: ForecastComparePoint[];
  };
  diagnostic_links: Record<string, string>;
  degraded_metadata: {
    realtime_transport: string;
    chart_mode: string;
    data_sources: string[];
  };
}
