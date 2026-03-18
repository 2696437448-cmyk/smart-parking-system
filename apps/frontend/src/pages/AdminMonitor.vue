<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, computed } from "vue";
import { useRealtimeStore } from "../stores/realtime";
import { useRealtimeChannel } from "../composables/useRealtimeChannel";

const gatewayBase = import.meta.env.VITE_GATEWAY_BASE_URL ?? "http://localhost:8080";
const store = useRealtimeStore();
const { reconnect } = useRealtimeChannel();
const monitor = ref<Record<string, any> | null>(null);
const revenue = ref<Array<Record<string, any>>>([]);
const loading = ref(false);
const errorText = ref("");
let timer: number | null = null;

const statusClass = computed(() => (store.mode === "realtime" ? "status-realtime" : "status-degraded"));

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

async function fetchJson(url: string) {
  const response = await fetch(url, {
    headers: {
      "X-Trace-Id": `frontend-admin-${Date.now()}`,
    },
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error ?? `http_${response.status}`);
  }
  return payload;
}

async function refreshBusinessViews() {
  loading.value = true;
  errorText.value = "";
  try {
    const [monitorPayload, revenuePayload] = await Promise.all([
      fetchJson(`${gatewayBase}/api/v1/admin/monitor/summary?date=${today()}`),
      fetchJson(`${gatewayBase}/api/v1/admin/revenue/summary?date=${today()}`),
    ]);
    monitor.value = monitorPayload;
    revenue.value = revenuePayload.summaries ?? [];
  } catch (error) {
    errorText.value = `物业视图刷新失败: ${String(error)}`;
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  void refreshBusinessViews();
  timer = window.setInterval(() => {
    void refreshBusinessViews();
  }, 8000);
});

onBeforeUnmount(() => {
  if (timer !== null) {
    window.clearInterval(timer);
  }
});
</script>

<template>
  <section class="panel-grid admin-grid">
    <article class="panel hero-panel">
      <div class="status-bar" :class="statusClass">
        <span>{{ store.modeLabel }}</span>
        <span>/</span>
        <span>{{ store.sourceLabel }}</span>
      </div>
      <h3>物业端业务监控</h3>
      <p class="muted">业务视图展示收益与资源状态，技术看板仅作为诊断补充。</p>
      <div class="action-row">
        <button class="primary" type="button" :disabled="loading" @click="refreshBusinessViews">刷新业务数据</button>
        <button type="button" @click="reconnect">手动重连</button>
      </div>
      <p v-if="errorText" class="error-text">{{ errorText }}</p>
    </article>

    <article class="panel metric-cluster">
      <div class="metric-card">
        <p class="label">占用率</p>
        <p class="value">{{ store.occupancyRatePercent }}</p>
      </div>
      <div class="metric-card">
        <p class="label">活动预约</p>
        <p class="value">{{ monitor?.active_reservations ?? store.activeReservations }}</p>
      </div>
      <div class="metric-card">
        <p class="label">今日收益</p>
        <p class="value">¥{{ Number(monitor?.revenue_total ?? 0).toFixed(2) }}</p>
      </div>
      <div class="metric-card">
        <p class="label">最后更新</p>
        <p class="value">{{ store.updatedAtText }}</p>
      </div>
    </article>

    <article class="panel revenue-panel">
      <h3>区域收益汇总</h3>
      <table class="summary-table">
        <thead>
          <tr>
            <th>区域</th>
            <th>收入</th>
            <th>订单数</th>
            <th>利用率</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in revenue" :key="String(item.region_id)">
            <td>{{ item.region_id }}</td>
            <td>¥{{ Number(item.revenue_amount ?? 0).toFixed(2) }}</td>
            <td>{{ item.order_count }}</td>
            <td>{{ (Number(item.utilization_rate ?? 0) * 100).toFixed(1) }}%</td>
          </tr>
        </tbody>
      </table>
    </article>
  </section>
</template>
