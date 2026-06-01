function detectBrowserHost() {
  if (typeof window === "undefined") {
    return "localhost";
  }
  return window.location.hostname || "localhost";
}

function detectHttpProtocol() {
  if (typeof window === "undefined") {
    return "http";
  }
  return window.location.protocol === "https:" ? "https" : "http";
}

function detectWsProtocol() {
  if (typeof window === "undefined") {
    return "ws";
  }
  return window.location.protocol === "https:" ? "wss" : "ws";
}

const browserHost = detectBrowserHost();
const httpProtocol = detectHttpProtocol();
const wsProtocol = detectWsProtocol();

export const runtimeConfig = {
  gatewayBaseUrl: import.meta.env.VITE_GATEWAY_BASE_URL ?? `${httpProtocol}://${browserHost}:8080`,
  realtimeWsUrl: import.meta.env.VITE_REALTIME_WS_URL ?? `${wsProtocol}://${browserHost}:8090/ws/status`,
  realtimePollUrl:
    import.meta.env.VITE_GATEWAY_POLL_URL ?? `${httpProtocol}://${browserHost}:8080/api/v1/admin/realtime/status`,
};

export function buildTraceHeaders(scope: string, headers: HeadersInit = {}) {
  return {
    "X-Trace-Id": `frontend-${scope}-${Date.now()}`,
    ...headers,
  };
}
