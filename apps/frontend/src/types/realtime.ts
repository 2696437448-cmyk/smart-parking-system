export type ChannelMode = "realtime" | "degraded";
export type ChannelSource = "websocket" | "polling";

export interface RealtimeSnapshot {
  occupancy_rate: number;
  active_reservations: number;
  updated_at: number;
}
