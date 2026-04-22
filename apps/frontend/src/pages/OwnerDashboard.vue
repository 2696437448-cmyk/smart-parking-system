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
  <section class="page-grid owner-page-grid owner-dashboard owner-smart-grid">
    <article class="panel hero-card owner-hero" v-motion-slide-visible-once-bottom>
      <SectionHeader
        :eyebrow="heroSummary.eyebrow"
        title="智能预约中枢"
        subtitle="把推荐、账单和下一步动作收束到同一屏，让首页直接承担停车旅程入口。"
        :badge="heroSummary.badge"
        badge-tone="accent"
      >
        <template #actions>
          <a-space class="hero-actions" wrap size="medium">
            <a-button type="primary" :loading="busy" @click="openOrders">查看订单</a-button>
            <a-button status="normal" :loading="busy" @click="loadRecommendations">刷新推荐</a-button>
          </a-space>
        </template>
      </SectionHeader>
      <div class="owner-summary-band">
        <div class="owner-summary-copy">
          <p class="hero-note">{{ activeSummary }}</p>
          <p class="muted hero-support">{{ heroSummary.helper }}</p>
        </div>
        <div class="metric-grid compact-metric-grid">
          <MetricCard
            label="目标区域"
            :value="dashboard?.summary.region_id ?? location"
            :note="dashboard?.summary.region_label ?? '社区停车区'"
            tone="accent"
            eyebrow="Region"
          />
          <MetricCard
            label="候选车位"
            :value="dashboard?.summary.recommendation_count ?? recommendations.length"
            note="按预约窗口与区域生成"
            tone="calm"
          />
          <MetricCard
            label="计费单位"
            :value="`${dashboard?.billing_rule.unit_minutes ?? 15} 分钟`"
            :note="dashboard?.billing_rule.timezone ?? 'Asia/Shanghai'"
          />
          <MetricCard
            label="最近订单"
            :value="dashboard?.summary.latest_order_id || '暂无'"
            :note="`${dashboard?.summary.latest_billing_status ?? 'NONE'} / ${formatCurrency(dashboard?.summary.latest_amount)}`"
          />
        </div>
      </div>
      <div class="hero-footer">
        <StatusBadge :label="state.badge" tone="calm" />
        <p class="muted hero-trace">{{ latestTrace || '等待下一次 dashboard 同步' }}</p>
      </div>
    </article>

    <article class="panel form-panel reservation-panel" v-motion-slide-visible-once-left>
      <SectionHeader
        eyebrow="Reservation Inputs"
        title="预约参数"
        subtitle="保留真实业务入口，同时把区域、时间窗和车位选择收进统一表单面板。"
        badge="可调整"
      >
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

    <article class="panel recommendation-panel recommendation-list" v-motion-slide-visible-once-right>
      <SectionHeader
        eyebrow="Slot Suggestions"
        title="推荐车位"
        subtitle="把候选车位、预计费用、到达时间和导航入口整合成可直接决策的推荐卡。"
        :badge="`${recommendations.length} 个候选`"
        badge-tone="accent"
      />
      <div v-if="latestOrder" class="detail-card journey-card">
        <div class="journey-card-head">
          <p class="metric-label">最近订单</p>
          <StatusBadge :label="latestOrder.billing_status" tone="accent" />
        </div>
        <strong>{{ latestOrder.order_id }}</strong>
        <p>{{ latestOrder.slot_id }} / {{ latestOrder.region_id }}</p>
        <p>账单状态：{{ latestOrder.billing_status }}</p>
      </div>
      <div class="recommend-grid">
        <article
          v-for="item in recommendations"
          :key="String(item.slot_id)"
          class="recommend-card"
        >
          <div class="card-topline">
            <p class="card-title">{{ item.slot_display_name ?? item.slot_id }}</p>
            <span class="price-tag">{{ formatCurrency(item.estimated_amount) }}</span>
          </div>
          <StatusBadge :label="item.region_label ?? location" tone="default" />
          <p>{{ item.region_label ?? item.slot_id }}</p>
          <p>ETA：{{ item.eta_minutes }} 分钟</p>
          <p>{{ item.destination?.display_name ?? '社区车位入口' }}</p>
          <a-button type="primary" class="recommend-action" :loading="busy" @click="reserveAndOpenOrders(String(item.slot_id))">
            预约并查看订单
          </a-button>
        </article>
      </div>
      <div v-if="!recommendations.length && state.tone !== 'loading'" class="empty-state">
        <p class="metric-label">暂无推荐结果</p>
        <p class="muted">请调整区域或预约窗口后重试。</p>
      </div>
    </article>
  </section>
</template>
