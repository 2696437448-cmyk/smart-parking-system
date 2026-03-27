<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import EChartPanel from "../components/EChartPanel.vue";
import { useRealtimeStore } from "../stores/realtime";
import { useRealtimeChannel } from "../composables/useRealtimeChannel";

const gatewayBase = import.meta.env.VITE_GATEWAY_BASE_URL ?? "http://localhost:8080";
const store = useRealtimeStore();
const { reconnect } = useRealtimeChannel();
const monitor = ref<Record<string, any> | null>(null);
const revenueSummary = ref<Array<Record<string, any>>>([]);
const revenueTrend = ref<Array<Record<string, any>>>([]);
const occupancyTrend = ref<Array<Record<string, any>>>([]);
const forecastCompare = ref<Array<Record<string, any>>>([]);
const loading = ref(false);
const errorText = ref("");
let timer: number | null = null;

const statusClass = computed(() => (store.mode === "realtime" ? "status-realtime" : "status-degraded"));

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

async function fetchJson(url: string) {
  const response = await fetch(url, {
    headers: { "X-Trace-Id": `frontend-admin-${Date.now()}` },
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
    const [monitorPayload, revenuePayload, trendPayload, occupancyPayload, comparePayload] = await Promise.all([
      fetchJson(`${gatewayBase}/api/v1/admin/monitor/summary?date=${today()}`),
      fetchJson(`${gatewayBase}/api/v1/admin/revenue/summary?date=${today()}`),
      fetchJson(`${gatewayBase}/api/v1/admin/revenue/trend?days=7`),
      fetchJson(`${gatewayBase}/api/v1/admin/occupancy/trend?limit=12`),
      fetchJson(`${gatewayBase}/api/v1/admin/forecast/compare?limit=12`),
    ]);
    monitor.value = monitorPayload;
    revenueSummary.value = revenuePayload.summaries ?? [];
    revenueTrend.value = trendPayload.points ?? [];
    occupancyTrend.value = occupancyPayload.points ?? [];
    forecastCompare.value = comparePayload.points ?? [];
  } catch (error) {
    errorText.value = `物业视图刷新失败: ${String(error)}`;
  } finally {
    loading.value = false;
  }
}

const revenueTrendOption = computed(() => ({
  tooltip: { trigger: "axis" },
  grid: { left: 36, right: 20, top: 30, bottom: 28 },
  xAxis: { type: "category", data: revenueTrend.value.map((item) => item.date) },
  yAxis: { type: "value" },
  series: [{ type: "line", smooth: true, areaStyle: {}, data: revenueTrend.value.map((item) => Number(item.revenue_amount ?? 0)) }],
}));

const regionCompareOption = computed(() => ({
  tooltip: { trigger: "axis" },
  grid: { left: 36, right: 20, top: 30, bottom: 28 },
  xAxis: { type: "category", data: revenueSummary.value.map((item) => item.region_id) },
  yAxis: { type: "value" },
  series: [{ type: "bar", data: revenueSummary.value.map((item) => Number(item.revenue_amount ?? 0)), itemStyle: { color: "#ec7b37" } }],
}));

const occupancyOption = computed(() => ({
  tooltip: { trigger: "axis" },
  grid: { left: 36, right: 20, top: 30, bottom: 28 },
  xAxis: { type: "category", data: occupancyTrend.value.map((item) => String(item.ts).slice(11, 16)) },
  yAxis: { type: "value", min: 0, max: 1 },
  series: [{ type: "line", smooth: true, data: occupancyTrend.value.map((item) => Number(item.occupancy_rate ?? 0)), itemStyle: { color: "#227c9d" } }],
}));

const forecastCompareOption = computed(() => ({
  tooltip: { trigger: "axis" },
  legend: { data: ["预测", "实际"] },
  grid: { left: 36, right: 20, top: 40, bottom: 28 },
  xAxis: { type: "category", data: forecastCompare.value.map((item) => String(item.ts).slice(11, 16)) },
  yAxis: { type: "value" },
  series: [
    { name: "预测", type: "line", smooth: true, data: forecastCompare.value.map((item) => Number(item.predicted_gap ?? 0)), itemStyle: { color: "#2a9d8f" } },
    { name: "实际", type: "line", smooth: true, data: forecastCompare.value.map((item) => Number(item.actual_gap ?? 0)), itemStyle: { color: "#9c6644" } },
  ],
}));

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
  <section class="page-grid admin-page-grid">
    <article class="panel hero-card admin-hero">
      <div class="status-bar" :class="statusClass">
        <span>{{ store.modeLabel }}</span>
        <span>/</span>
        <span>{{ store.sourceLabel }}</span>
      </div>
      <h3>物业经营驾驶舱</h3>
      <p class="muted">
        业务图表与经营指标集中展示；Grafana 继续保留为技术诊断视图。
      </p>
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
        <p class="label">调度策略</p>
        <p class="value small-value">{{ monitor?.dispatch_strategy ?? "hungarian_optimal" }}</p>
      </div>
    </article>

    <EChartPanel title="日收益趋势" subtitle="最近 7 天收入变化" :option="revenueTrendOption" />
    <EChartPanel title="区域收益对比" subtitle="按区域对比当日收入" :option="regionCompareOption" />
    <EChartPanel title="车位占用率趋势" subtitle="来自 ETL / forecast 输出" :option="occupancyOption" />
    <EChartPanel title="预测值 vs 实际值" subtitle="用于答辩说明预测效果" :option="forecastCompareOption" />
  </section>
</template>
