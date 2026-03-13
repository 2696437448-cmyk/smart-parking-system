import { defineStore } from "pinia";
import type { ChannelMode, ChannelSource, RealtimeSnapshot } from "../types/realtime";

interface RealtimeState {
  mode: ChannelMode;
  source: ChannelSource;
  connected: boolean;
  occupancyRate: number;
  activeReservations: number;
  updatedAt: number;
  lastError: string;
}

const nowSeconds = () => Math.floor(Date.now() / 1000);

export const useRealtimeStore = defineStore("realtime", {
  state: (): RealtimeState => ({
    mode: "degraded",
    source: "polling",
    connected: false,
    occupancyRate: 0,
    activeReservations: 0,
    updatedAt: nowSeconds(),
    lastError: "",
  }),
  getters: {
    modeLabel: (state): string => (state.mode === "realtime" ? "实时" : "降级"),
    sourceLabel: (state): string => (state.source === "websocket" ? "WebSocket" : "Polling"),
    occupancyRatePercent: (state): string => `${(state.occupancyRate * 100).toFixed(1)}%`,
    updatedAtText: (state): string => new Date(state.updatedAt * 1000).toLocaleTimeString(),
  },
  actions: {
    applySnapshot(payload: Partial<RealtimeSnapshot>, source: ChannelSource, mode: ChannelMode) {
      this.occupancyRate = Number(payload.occupancy_rate ?? 0);
      this.activeReservations = Number(payload.active_reservations ?? 0);
      this.updatedAt = Number(payload.updated_at ?? nowSeconds());
      this.source = source;
      this.mode = mode;
      this.connected = mode === "realtime";
      this.lastError = "";
    },
    markDegraded(reason: string, source: ChannelSource) {
      this.mode = "degraded";
      this.source = source;
      this.connected = false;
      this.lastError = reason;
    },
  },
});
