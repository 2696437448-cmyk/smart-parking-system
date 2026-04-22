<script setup lang="ts">
import { computed } from "vue";
import MetricCard from "../components/MetricCard.vue";
import SectionHeader from "../components/SectionHeader.vue";
import StatusBadge from "../components/StatusBadge.vue";
import ViewStateNotice from "../components/ViewStateNotice.vue";
import { formatCurrency, formatTraceDetail } from "../presenters/format";
import { ownerDashboardHero } from "../presenters/owner";
import { useOwnerDashboardView } from "../composables/useOwnerDashboardView";

const {
  authenticatedUserId,
  location,
  windowStart,
  windowEnd,
  busy,
  dashboard,
  state,
  preferredWindow,
  recommendations,
  latestOrder,
  activeSummary,
  loadRecommendations,
  reserveAndOpenOrders,
  openOrders,
} = useOwnerDashboardView();

const heroSummary = computed(() => ownerDashboardHero(dashboard.value?.summary));
const latestTrace = computed(() => (dashboard.value ? formatTraceDetail(dashboard.value.trace_id, dashboard.value.service) : ""));
</script>

<template>
  <section class="page-grid owner-page-grid owner-dashboard dashboard-grid">
    <article class="panel summary-panel" v-motion-slide-visible-once-bottom>
      <SectionHeader eyebrow="首页" title="停车服务" subtitle="查看推荐结果、最近订单和停车信息。" :badge="heroSummary.badge" badge-tone="accent">
        <template #actions>
          <a-space class="hero-actions" wrap size="medium">
            <a-button type="primary" :loading="busy" @click="openOrders">查看订单</a-button>
            <a-button status="normal" :loading="busy" @click="loadRecommendations">刷新推荐</a-button>
          </a-space>
        </template>
      </SectionHeader>
      <p class="hero-note">{{ activeSummary }}</p>
      <div class="metric-grid compact-metric-grid">
        <MetricCard label="目标区域" :value="dashboard?.summary.region_id ?? location" :note="dashboard?.summary.region_label ?? '社区停车区'" tone="accent" eyebrow="区域" />
        <MetricCard label="候选车位" :value="dashboard?.summary.recommendation_count ?? recommendations.length" note="根据时间和区域生成" tone="calm" />
        <MetricCard label="计费单位" :value="`${dashboard?.billing_rule.unit_minutes ?? 15} 分钟`" :note="dashboard?.billing_rule.timezone ?? 'Asia/Shanghai'" />
        <MetricCard label="最近订单" :value="dashboard?.summary.latest_order_id || '暂无'" :note="`${dashboard?.summary.latest_billing_status ?? '无'} / ${formatCurrency(dashboard?.summary.latest_amount)}`" />
      </div>
      <div class="hero-footer">
        <StatusBadge :label="state.badge" tone="calm" />
        <p class="muted hero-trace">{{ latestTrace || '等待下一次同步' }}</p>
      </div>
    </article>

    <article class="panel form-panel" v-motion-slide-visible-once-left>
      <SectionHeader eyebrow="预约" title="预约参数" subtitle="填写区域和时间后获取推荐结果。" badge="可调整">
        <template #actions>
          <StatusBadge :label="preferredWindow" tone="default" />
        </template>
      </SectionHeader>
      <a-form layout="vertical" class="smart-form-grid" :model="{ authenticatedUserId, location, windowStart, windowEnd }">
        <div class="form-grid">
          <a-form-item label="登录账号">
            <a-input :model-value="authenticatedUserId" disabled />
          </a-form-item>
          <a-form-item label="区域">
            <a-select v-model="location">
              <a-option value="R1">R1</a-option>
              <a-option value="R2">R2</a-option>
              <a-option value="R3">R3</a-option>
            </a-select>
          </a-form-item>
          <a-form-item label="开始时间">
            <input v-model="windowStart" type="datetime-local" />
          </a-form-item>
          <a-form-item label="结束时间">
            <input v-model="windowEnd" type="datetime-local" />
          </a-form-item>
        </div>
      </a-form>
      <div class="detail-list compact-detail">
        <p><strong>当前预约窗口</strong> {{ preferredWindow }}</p>
        <p><strong>计费规则</strong> {{ dashboard?.billing_rule.rounding_mode ?? 'CEIL_TO_UNIT' }}</p>
      </div>
      <ViewStateNotice :tone="state.tone" :title="state.title" :message="state.message" :detail="state.detail" :badge="state.badge" />
    </article>

    <article class="panel recommendation-panel" v-motion-slide-visible-once-right>
      <SectionHeader eyebrow="推荐" title="推荐结果" subtitle="直接查看可用车位、费用和预计到达时间。" :badge="`${recommendations.length} 个候选`" badge-tone="accent" />
      <div v-if="latestOrder" class="detail-card journey-card">
        <div class="journey-card-head">
          <p class="metric-label">最近订单</p>
          <StatusBadge :label="latestOrder.billing_status" tone="accent" />
        </div>
        <strong>{{ latestOrder.order_id }}</strong>
        <p>{{ latestOrder.slot_id }} / {{ latestOrder.region_id }}</p>
        <p>状态：{{ latestOrder.billing_status }}</p>
      </div>
      <div class="recommend-grid">
        <article v-for="item in recommendations" :key="String(item.slot_id)" class="recommend-card">
          <div class="card-topline">
            <p class="card-title">{{ item.slot_display_name ?? item.slot_id }}</p>
            <span class="price-tag">{{ formatCurrency(item.estimated_amount) }}</span>
          </div>
          <StatusBadge :label="item.region_label ?? location" tone="default" />
          <p>{{ item.region_label ?? item.slot_id }}</p>
          <p>预计到达：{{ item.eta_minutes }} 分钟</p>
          <p>{{ item.destination?.display_name ?? '社区车位入口' }}</p>
          <a-button type="primary" class="recommend-action" :loading="busy" @click="reserveAndOpenOrders(String(item.slot_id))">立即预约</a-button>
        </article>
      </div>
      <div v-if="!recommendations.length && state.tone !== 'loading'" class="empty-state">
        <p class="metric-label">暂无推荐结果</p>
        <p class="muted">请调整区域或预约窗口后重试。</p>
      </div>
    </article>
  </section>
</template>
