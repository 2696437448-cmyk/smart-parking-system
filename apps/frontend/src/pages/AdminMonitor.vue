<script setup lang="ts">
import { computed, defineAsyncComponent } from "vue";
import MetricCard from "../components/MetricCard.vue";
import SectionHeader from "../components/SectionHeader.vue";
import ViewStateNotice from "../components/ViewStateNotice.vue";
import { adminChartCards, adminStatusSummary } from "../presenters/admin";
import { formatCurrency, formatPercent } from "../presenters/format";
import { useAdminDashboardView } from "../composables/useAdminDashboardView";

const EChartPanel = defineAsyncComponent(() => import("../components/EChartPanel.vue"));
const { dashboard, busy, state, statusClass, updatedAtText, lastErrorText, refreshBusinessViews, reconnect, store } = useAdminDashboardView();

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

const chartCards = computed(() => adminChartCards(dashboard.value));
const adminSummary = computed(() => adminStatusSummary(dashboard.value));
</script>

<template>
  <section class="page-grid admin-page-grid admin-dashboard operations-cockpit">
    <article class="panel hero-card admin-hero" v-motion-slide-visible-once-bottom>
      <div class="shell-status-strip">
        <a-tag color="cyan">{{ store.modeLabel }}</a-tag>
        <a-tag color="arcoblue">{{ store.sourceLabel }}</a-tag>
        <a-tag color="gold">{{ adminSummary.degradedHint }}</a-tag>
      </div>
      <SectionHeader
        eyebrow="Operations Cockpit"
        title="停车运营驾驶舱"
        subtitle="聚合接口、实时通道和解释层统一进入经营观察面板，让页面更像正在运行的系统。"
        :badge="adminSummary.dispatchBadge"
        badge-tone="accent"
      />
      <a-space class="action-row" wrap size="medium">
        <a-button type="primary" :loading="busy" @click="refreshBusinessViews">刷新业务数据</a-button>
        <a-button :loading="busy" @click="reconnect">手动重连</a-button>
      </a-space>
      <ViewStateNotice :tone="state.tone" :title="state.title" :message="state.message" :detail="state.detail" :badge="state.badge" />
    </article>

    <article class="panel summary-panel kpi-signal-grid" v-motion-slide-visible-once-top>
      <div class="metric-grid">
        <MetricCard label="实时占用率" :value="store.occupancyRatePercent" :note="`${store.sourceLabel} / ${store.modeLabel}`" tone="accent" eyebrow="Realtime" />
        <MetricCard label="今日收益" :value="formatCurrency(dashboard?.summary.revenue_total)" note="billing_records 汇总" tone="calm" />
        <MetricCard label="活动预约" :value="dashboard?.summary.active_reservations ?? store.activeReservations" note="预约主链当前负载" />
        <MetricCard label="调度策略" :value="dashboard?.summary.dispatch_strategy ?? 'hungarian_optimal'" note="保持 Step19B 确定性" />
      </div>
      <div class="summary-card-grid">
        <article v-for="card in chartCards" :key="card.title" class="summary-mini-card">
          <p class="metric-label">{{ card.title }}</p>
          <strong class="summary-mini-value">{{ card.value }}</strong>
          <p class="metric-note">{{ card.note }}</p>
        </article>
      </div>
    </article>

    <article class="panel insight-panel" v-motion-slide-visible-once-top>
      <SectionHeader
        eyebrow="Operational Highlights"
        title="视图聚合摘要"
        subtitle="让业务页聚焦解释，而不是让页面自己拼多个接口。"
        :badge="adminSummary.degradedHint"
      />
      <div class="metric-grid compact-metric-grid">
        <MetricCard label="覆盖区域" :value="dashboard?.highlights.region_count ?? 0" note="收益区域摘要数" />
        <MetricCard label="收益点位" :value="dashboard?.highlights.revenue_points ?? 0" note="趋势采样数" />
        <MetricCard label="预测点位" :value="dashboard?.highlights.forecast_points ?? 0" note="预测对照采样数" />
        <MetricCard label="峰值占用率" :value="formatPercent(dashboard?.highlights.peak_occupancy)" note="occupancy trend 最高值" />
      </div>
      <div class="insight-badges">
        <a-tag color="cyan">{{ store.modeLabel }}</a-tag>
        <a-tag color="arcoblue">{{ store.sourceLabel }}</a-tag>
        <a-tag color="gold">{{ adminSummary.degradedHint }}</a-tag>
      </div>
      <div class="detail-list compact-detail">
        <p><strong>最近更新</strong> {{ updatedAtText }}</p>
        <p><strong>最近错误</strong> {{ lastErrorText }}</p>
        <p><strong>诊断入口</strong> Grafana {{ dashboard?.diagnostic_links?.grafana ?? 'N/A' }}</p>
        <p><strong>消息入口</strong> RabbitMQ {{ dashboard?.diagnostic_links?.rabbitmq ?? 'N/A' }}</p>
        <p><strong>降级说明</strong> {{ dashboard?.degraded_metadata?.realtime_transport ?? 'websocket_with_polling_fallback' }}</p>
      </div>
    </article>

    <div class="chart-cluster" v-if="dashboard" v-motion-slide-visible-once-bottom>
      <EChartPanel title="日收益趋势" subtitle="最近 7 天收入变化" note="用于观察订单结算与收入起伏。" :option="revenueTrendOption" />
      <EChartPanel title="区域收益对比" subtitle="按区域对比当日收入" note="用于解释不同区域的经营贡献。" :option="regionCompareOption" />
      <EChartPanel title="车位占用率趋势" subtitle="来自 ETL / forecast 输出" note="用于观察高峰期车位占用状态。" :option="occupancyOption" />
      <EChartPanel title="预测值 vs 实际值" subtitle="用于答辩说明预测效果" note="用于比较模型预测与实际缺口的接近程度。" :option="forecastCompareOption" />
    </div>
  </section>
</template>
