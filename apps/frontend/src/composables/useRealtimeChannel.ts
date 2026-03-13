import { onBeforeUnmount, onMounted, ref } from "vue";
import { useRealtimeStore } from "../stores/realtime";
import type { RealtimeSnapshot } from "../types/realtime";

const DEFAULT_WS = "ws://localhost:8090/ws/status";
const DEFAULT_POLL = "http://localhost:8080/api/v1/admin/realtime/status";

function parseSnapshot(input: unknown): Partial<RealtimeSnapshot> {
  if (!input || typeof input !== "object") {
    return {};
  }
  return input as Partial<RealtimeSnapshot>;
}

export function useRealtimeChannel() {
  const store = useRealtimeStore();
  const wsRef = ref<WebSocket | null>(null);
  const pollTimer = ref<number | null>(null);
  const reconnectTimer = ref<number | null>(null);

  const wsUrl = import.meta.env.VITE_REALTIME_WS_URL ?? DEFAULT_WS;
  const pollUrl = import.meta.env.VITE_GATEWAY_POLL_URL ?? DEFAULT_POLL;

  async function fetchPolling() {
    try {
      const resp = await fetch(pollUrl, {
        headers: {
          "X-Trace-Id": `frontend-poll-${Date.now()}`,
        },
      });
      if (!resp.ok) {
        store.markDegraded(`polling_http_${resp.status}`, "polling");
        return;
      }
      const data = parseSnapshot(await resp.json());
      store.applySnapshot(data, "polling", "degraded");
    } catch (err) {
      store.markDegraded(`polling_error_${String(err)}`, "polling");
    }
  }

  function stopPolling() {
    if (pollTimer.value !== null) {
      window.clearInterval(pollTimer.value);
      pollTimer.value = null;
    }
  }

  function startPolling() {
    if (pollTimer.value !== null) {
      return;
    }
    void fetchPolling();
    pollTimer.value = window.setInterval(() => {
      void fetchPolling();
    }, 2000);
  }

  function scheduleReconnect() {
    if (reconnectTimer.value !== null) {
      return;
    }
    reconnectTimer.value = window.setTimeout(() => {
      reconnectTimer.value = null;
      connectWebSocket();
    }, 4000);
  }

  function closeWebSocket() {
    if (wsRef.value) {
      wsRef.value.close();
      wsRef.value = null;
    }
  }

  function connectWebSocket() {
    closeWebSocket();
    try {
      wsRef.value = new WebSocket(wsUrl);
    } catch (err) {
      store.markDegraded(`ws_init_error_${String(err)}`, "polling");
      startPolling();
      scheduleReconnect();
      return;
    }

    wsRef.value.onopen = () => {
      stopPolling();
      store.connected = true;
      store.mode = "realtime";
      store.source = "websocket";
      store.lastError = "";
    };

    wsRef.value.onmessage = (event) => {
      try {
        const payload = parseSnapshot(JSON.parse(event.data));
        store.applySnapshot(payload, "websocket", "realtime");
      } catch (err) {
        store.markDegraded(`ws_message_error_${String(err)}`, "polling");
        startPolling();
      }
    };

    wsRef.value.onerror = () => {
      store.markDegraded("ws_transport_error", "polling");
      startPolling();
    };

    wsRef.value.onclose = () => {
      store.markDegraded("ws_closed", "polling");
      startPolling();
      scheduleReconnect();
    };
  }

  function stop() {
    stopPolling();
    if (reconnectTimer.value !== null) {
      window.clearTimeout(reconnectTimer.value);
      reconnectTimer.value = null;
    }
    closeWebSocket();
  }

  function start() {
    connectWebSocket();
  }

  onMounted(start);
  onBeforeUnmount(stop);

  return {
    start,
    stop,
    reconnect: connectWebSocket,
  };
}
