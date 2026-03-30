export const runtimeConfig = {
  gatewayBaseUrl: import.meta.env.VITE_GATEWAY_BASE_URL ?? "http://localhost:8080",
  realtimeWsUrl: import.meta.env.VITE_REALTIME_WS_URL ?? "ws://localhost:8090/ws/status",
  realtimePollUrl: import.meta.env.VITE_GATEWAY_POLL_URL ?? "http://localhost:8080/api/v1/admin/realtime/status",
};

export function buildTraceHeaders(scope: string, headers: HeadersInit = {}) {
  return {
    "X-Trace-Id": `frontend-${scope}-${Date.now()}`,
    ...headers,
  };
}
