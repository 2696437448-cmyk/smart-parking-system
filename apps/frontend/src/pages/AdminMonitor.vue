<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import EChartPanel from "../components/EChartPanel.vue";
import MetricCard from "../components/MetricCard.vue";
import SectionHeader from "../components/SectionHeader.vue";
import { useRealtimeStore } from "../stores/realtime";
import { useRealtimeChannel } from "../composables/useRealtimeChannel";
import { fetchAdminDashboard } from "../services/admin";
import type { AdminDashboardView } from "../types/dashboard";

const store = useRealtimeStore();
const { reconnect } = useRealtimeChannel();
const dashboard = ref<AdminDashboardView | null>(null);
const loading = ref(false);
const errorText = ref("");
let timer: number | null = null;

const statusClass = computed(() => (store.mode === "realtime" ? "status-realtime" : "status-degraded"));

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

async function refreshBusinessViews() {
  loading.value = true;
  errorText.value = "";
  try {
    dashboard.value = await fetchAdminDashboard({
      date: today(),
      trendDays: 7,
      trendLimit: 12,
    });
  } catch (error) {
    errorText.value = `物业视图刷新失败: ${String(error)}`;
  } finally {
    loading.value = false;
  }
}

const revenueTrendOption = computed(() => ({
  tooltip: { trigger: "axis" },
  grid: { left: 36, right: 20, top: 30, bottom: 28 },
  xAxis: { type: "category", data: (dashboard.value?.sections.revenue_trend ?? []).map((item) => item.date) },
  yAxis: { type: "value" },
  series: [{ type: "line", smooth: true, areaStyle: {}, data: (dashboard.value?.sections.revenue_trend ?? []).map((item) => Number(item.revenue_amount ?? 0)) }],
}));

const regionCompareOption = computed(() => ({
  tooltip: { trigger: "axis" },
  grid: { left: 36, right: 20, top: 30, bottom: 28 },
  xAxis: { type: "category", data: (dashboard.value?.sections.revenue_summary ?? []).map((item) => item.region_id) },
  yAxis: { type: "value" },
  series: [{ type: "bar", data: (dashboard.value?.sections.revenue_summary ?? []).map((item) => Number(item.revenue_amount ?? 0)), itemStyle: { color: "#f17b42" } }],
}));

const occupancyOption = computed(() => ({
  tooltip: { trigger: "axis" },
  grid: { left: 36, right: 20, top: 30, bottom: 28 },
  xAxis: { type: "category", data: (dashboard.value?.sections.occupancy_trend ?? []).map((item) => String(item.ts).slice(11, 16)) },
  yAxis: { type: "value", min: 0, max: 1 },
  series: [{ type: "line", smooth: true, data: (dashboard.value?.sections.occupancy_trend ?? []).map((item) => Number(item.occupancy_rate ?? 0)), itemStyle: { color: "#1d7f8c" } }],
}));

const forecastCompareOption = computed(() => ({
  tooltip: { trigger: "axis" },
  legend: { data: ["预测", "实际"] },
  grid: { left: 36, right: 20, top: 40, bottom: 28 },
  xAxis: { type: "category", data: (dashboard.value?.sections.forecast_compare ?? []).map((item) => String(item.ts).slice(11, 16)) },
  yAxis: { type: "value" },
  series: [
    { name: "预测", type: "line", smooth: true, data: (dashboard.value?.sections.forecast_compare ?? []).map((item) => Number(item.predicted_gap ?? 0)), itemStyle: { color: "#2a9d8f" } },
    { name: "实际", type: "line", smooth: true, data: (dashboard.value?.sections.forecast_compare ?? []).map((item) => Number(item.actual_gap ?? 0)), itemStyle: { color: "#9c6644" } },
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
  <section class="page-grid admin-page-grid admin-dashboard">
    <article class="panel hero-card admin-hero">
      <div class="status-bar" :class="statusClass">
        <span>{{ store.modeLabel }}</span>
        <span>/</span>
        <span>{{ store.sourceLabel }}</span>
      </div>
      <SectionHeader
        eyebrow="Business Dashboard"
        title="物业经营驾驶舱"
        subtitle="前端通过聚合接口一次获取经营视图，实时状态仍保持 WebSocket 优先、Polling 降级。"
        :badge="dashboard?.summary.dispatch_strategy ?? 'hungarian_optimal'"
      />
      <div class="action-row">
        <button class="primary" type="button" :disabled="loading" @click="refreshBusinessViews">刷新业务数据</button>
        <button type="button" @click="reconnect">手动重连</button>
      </div>
      <p v-if="errorText" class="error-text">{{ errorText }}</p>
    </article>

    <article class="panel summary-panel">
      <div class="metric-grid">
        <MetricCard label="实时占用率" :value="store.occupancyRatePercent" :note="`${store.sourceLabel} / ${store.modeLabel}`" tone="accent" />
        <MetricCard label="活动预约" :value="dashboard?.summary.active_reservations ?? store.activeReservations" note="预约主链当前负载" />
        <MetricCard label="今日收益" :value="`¥${Number(dashboard?.summary.revenue_total ?? 0).toFixed(2)}`" note="billing_records 汇总" tone="calm" />
        <MetricCard label="调度策略" :value="dashboard?.summary.dispatch_strategy ?? 'hungarian_optimal'" note="保持 Step19B 确定性" />
      </div>
    </article>

    <article class="panel insight-panel">
      <SectionHeader
        eyebrow="Operational Highlights"
        title="视图聚合摘要"
        subtitle="让业务页聚焦解释，而不是让页面自己拼多个接口。"
      />
      <div class="metric-grid compact-metric-grid">
        <MetricCard label="覆盖区域" :value="dashboard?.highlights.region_count ?? 0" note="收益区域摘要数" />
        <MetricCard label="收益点位" :value="dashboard?.highlights.revenue_points ?? 0" note="趋势采样数" />
        <MetricCard label="预测点位" :value="dashboard?.highlights.forecast_points ?? 0" note="预测对照采样数" />
        <MetricCard label="峰值占用率" :value="`${Number((dashboard?.highlights.peak_occupancy ?? 0) * 100).toFixed(1)}%`" note="occupancy trend 最高值" />
      </div>
      <div class="detail-list compact-detail">
        <p><strong>诊断入口</strong> Grafana {{ dashboard?.diagnostic_links?.grafana ?? "N/A" }}</p>
        <p><strong>消息入口</strong> RabbitMQ {{ dashboard?.diagnostic_links?.rabbitmq ?? "N/A" }}</p>
        <p><strong>降级说明</strong> {{ dashboard?.degraded_metadata?.realtime_transport ?? "websocket_with_polling_fallback" }}</p>
      </div>
    </article>

    <div class="chart-cluster">
      <EChartPanel title="日收益趋势" subtitle="最近 7 天收入变化" :option="revenueTrendOption" />
      <EChartPanel title="区域收益对比" subtitle="按区域对比当日收入" :option="regionCompareOption" />
      <EChartPanel title="车位占用率趋势" subtitle="来自 ETL / forecast 输出" :option="occupancyOption" />
      <EChartPanel title="预测值 vs 实际值" subtitle="用于答辩说明预测效果" :option="forecastCompareOption" />
    </div>
  </section>
</template>
