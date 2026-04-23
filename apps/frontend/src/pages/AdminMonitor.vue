<script setup lang="ts">
import { computed, defineAsyncComponent } from "vue";
import MetricCard from "../components/MetricCard.vue";
import SectionHeader from "../components/SectionHeader.vue";
import ViewStateNotice from "../components/ViewStateNotice.vue";
import { adminStatusSummary } from "../presenters/admin";
import { formatCurrency, formatPercent } from "../presenters/format";
import { useAdminDashboardView } from "../composables/useAdminDashboardView";

const EChartPanel = defineAsyncComponent(() => import("../components/EChartPanel.vue"));
const { dashboard, busy, state, updatedAtText, lastErrorText, refreshBusinessViews, reconnect, store } = useAdminDashboardView();

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

const adminSummary = computed(() => adminStatusSummary(dashboard.value));
</script>

<template>
  <section class="page-grid admin-page-grid admin-dashboard admin-monitor-page">
    <article class="panel" v-motion-slide-visible-once-bottom>
      <SectionHeader eyebrow="物业端" title="物业监管" subtitle="一屏查看主要指标和运行状态。" :badge="adminSummary.dispatchBadge" badge-tone="accent">
        <template #actions>
          <a-space class="action-row" wrap size="medium">
            <a-button type="primary" :loading="busy" @click="refreshBusinessViews">刷新</a-button>
            <a-button :loading="busy" @click="reconnect">重连</a-button>
          </a-space>
        </template>
      </SectionHeader>
      <ViewStateNotice :tone="state.tone" :title="state.title" :message="state.message" :detail="state.detail" :badge="state.badge" />
      <div class="admin-summary-board">
        <MetricCard label="占用率" :value="store.occupancyRatePercent" :note="`${store.sourceLabel} / ${store.modeLabel}`" tone="accent" />
        <MetricCard label="今日收益" :value="formatCurrency(dashboard?.summary.revenue_total)" note="账单汇总" tone="calm" />
        <MetricCard label="活动预约" :value="dashboard?.summary.active_reservations ?? store.activeReservations" note="当前负载" />
        <MetricCard label="调度策略" :value="dashboard?.summary.dispatch_strategy ?? 'hungarian_optimal'" note="当前策略" />
        <MetricCard label="峰值占用率" :value="formatPercent(dashboard?.highlights.peak_occupancy)" note="高峰统计" />
      </div>
      <div class="shell-status-strip">
        <a-tag color="arcoblue">{{ store.modeLabel }}</a-tag>
        <a-tag color="green">{{ store.sourceLabel }}</a-tag>
        <a-tag color="gold">{{ adminSummary.degradedHint }}</a-tag>
      </div>
    </article>

    <section class="admin-monitor-grid">
      <div class="admin-main-chart" v-if="dashboard" v-motion-slide-visible-once-top>
        <EChartPanel title="收益趋势" subtitle="最近 7 天" note="查看每日收益变化。" :option="revenueTrendOption" />
      </div>

      <div class="admin-side-cards">
        <article class="panel" v-motion-slide-visible-once-top>
          <SectionHeader eyebrow="运行" title="运行状态" subtitle="查看最近更新和当前说明。" :badge="adminSummary.degradedHint" />
          <div class="summary-note-list">
            <p><strong>最近更新：</strong>{{ updatedAtText }}</p>
            <p><strong>最近错误：</strong>{{ lastErrorText }}</p>
            <p><strong>数据来源：</strong>{{ store.sourceLabel }}</p>
            <p><strong>运行方式：</strong>{{ store.modeLabel }}</p>
          </div>
        </article>

        <article class="panel" v-motion-slide-visible-once-top>
          <SectionHeader eyebrow="摘要" title="区域情况" subtitle="查看区域和采样点位。" />
          <div class="summary-note-list">
            <p><strong>覆盖区域：</strong>{{ dashboard?.highlights.region_count ?? 0 }}</p>
            <p><strong>收益点位：</strong>{{ dashboard?.highlights.revenue_points ?? 0 }}</p>
            <p><strong>预测点位：</strong>{{ dashboard?.highlights.forecast_points ?? 0 }}</p>
            <p><strong>当前提示：</strong>{{ adminSummary.degradedHint }}</p>
          </div>
        </article>
      </div>
    </section>

    <div class="admin-chart-cluster" v-if="dashboard" v-motion-slide-visible-once-bottom>
      <EChartPanel title="区域收益" subtitle="按区域查看" note="对比不同区域的收益。" :option="regionCompareOption" />
      <EChartPanel title="占用率趋势" subtitle="最近采样" note="查看车位占用变化。" :option="occupancyOption" />
    </div>
  </section>
</template>
