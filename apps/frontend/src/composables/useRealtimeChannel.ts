import { onBeforeUnmount, onMounted, ref } from "vue";
import { buildTraceHeaders, runtimeConfig } from "../services/runtime";
import { useRealtimeStore } from "../stores/realtime";
import type { RealtimeSnapshot } from "../types/realtime";

function parseSnapshot(input: unknown): Partial<RealtimeSnapshot> {
  if (!input || typeof input !== "object") {
    return {};
  }
  return input as Partial<RealtimeSnapshot>;
}

function parsePayload(text: string): Partial<RealtimeSnapshot> {
  try {
    return parseSnapshot(JSON.parse(text));
  } catch {
    return {};
  }
}

export function useRealtimeChannel() {
  const store = useRealtimeStore();
  const wsRef = ref<WebSocket | null>(null);
  const pollTimer = ref<number | null>(null);
  const reconnectTimer = ref<number | null>(null);
  const pollInFlight = ref(false);

  const wsUrl = runtimeConfig.realtimeWsUrl;
  const pollUrl = runtimeConfig.realtimePollUrl;
  let activePollController: AbortController | null = null;
  let socketGeneration = 0;

  async function fetchPolling() {
    if (pollInFlight.value) {
      return;
    }
    pollInFlight.value = true;
    const controller = new AbortController();
    activePollController = controller;
    try {
      const resp = await fetch(pollUrl, {
        signal: controller.signal,
        headers: buildTraceHeaders("realtime-polling", { Accept: "application/json" }),
      });
      const payload = parsePayload(await resp.text());
      if (!resp.ok) {
        store.markDegraded(`polling_http_${resp.status}`, "polling");
        return;
      }
      store.applySnapshot(payload, "polling", "degraded");
    } catch (err) {
      if (!controller.signal.aborted) {
        store.markDegraded(`polling_error_${String(err)}`, "polling");
      }
    } finally {
      if (activePollController === controller) {
        activePollController = null;
      }
      pollInFlight.value = false;
    }
  }

  function cancelPollingRequest() {
    if (activePollController) {
      activePollController.abort();
      activePollController = null;
    }
  }

  function stopPolling() {
    if (pollTimer.value !== null) {
      window.clearInterval(pollTimer.value);
      pollTimer.value = null;
    }
    cancelPollingRequest();
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

  function clearReconnectTimer() {
    if (reconnectTimer.value !== null) {
      window.clearTimeout(reconnectTimer.value);
      reconnectTimer.value = null;
    }
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
    if (!wsRef.value) {
      return;
    }
    const socket = wsRef.value;
    wsRef.value = null;
    socket.onopen = null;
    socket.onmessage = null;
    socket.onerror = null;
    socket.onclose = null;
    socket.close();
  }

  function connectWebSocket() {
    clearReconnectTimer();
    stopPolling();
    socketGeneration += 1;
    const generation = socketGeneration;
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
      if (generation !== socketGeneration) {
        return;
      }
      stopPolling();
      store.connected = true;
      store.mode = "realtime";
      store.source = "websocket";
      store.lastError = "";
    };

    wsRef.value.onmessage = (event) => {
      if (generation !== socketGeneration) {
        return;
      }
      try {
        const payload = parseSnapshot(JSON.parse(event.data));
        store.applySnapshot(payload, "websocket", "realtime");
      } catch (err) {
        store.markDegraded(`ws_message_error_${String(err)}`, "polling");
        startPolling();
      }
    };

    wsRef.value.onerror = () => {
      if (generation !== socketGeneration) {
        return;
      }
      store.markDegraded("ws_transport_error", "polling");
      startPolling();
    };

    wsRef.value.onclose = () => {
      if (generation !== socketGeneration) {
        return;
      }
      store.markDegraded("ws_closed", "polling");
      startPolling();
      scheduleReconnect();
    };
  }

  function stop() {
    clearReconnectTimer();
    stopPolling();
    socketGeneration += 1;
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
