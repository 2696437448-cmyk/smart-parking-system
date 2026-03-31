<script setup lang="ts">
import MetricCard from "../components/MetricCard.vue";
import SectionHeader from "../components/SectionHeader.vue";
import ViewStateNotice from "../components/ViewStateNotice.vue";
import { useOwnerDashboardView } from "../composables/useOwnerDashboardView";

const {
  userId,
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
</script>

<template>
  <section class="page-grid owner-page-grid owner-dashboard">
    <article class="panel hero-card owner-hero">
      <SectionHeader
        eyebrow="Owner Journey"
        title="预约与出行首页"
        subtitle="把区域推荐、账单提示和下一步动作收敛成一套移动优先入口。"
        :badge="dashboard?.summary.region_label ?? '智慧停车'"
      />
      <p class="hero-note">{{ activeSummary }}</p>
      <div class="action-row">
        <button class="primary" type="button" :disabled="busy" @click="openOrders">查看订单</button>
        <button type="button" :disabled="busy" @click="loadRecommendations">刷新推荐</button>
      </div>
      <div class="metric-grid compact-metric-grid">
        <MetricCard
          label="目标区域"
          :value="dashboard?.summary.region_id ?? location"
          :note="dashboard?.summary.region_label ?? '社区停车区'"
          tone="accent"
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
          :note="dashboard?.summary.latest_billing_status ?? 'NONE'"
        />
      </div>
    </article>

    <article class="panel form-panel">
      <SectionHeader
        eyebrow="Reservation Inputs"
        title="预约参数"
        subtitle="保持演示可控，同时把真实业务入口聚焦在区域、时间窗和车位选择。"
      />
      <div class="form-grid">
        <label>
          <span>用户 ID</span>
          <input v-model="userId" type="text" />
        </label>
        <label>
          <span>区域</span>
          <select v-model="location">
            <option value="R1">R1</option>
            <option value="R2">R2</option>
            <option value="R3">R3</option>
          </select>
        </label>
        <label>
          <span>开始时间</span>
          <input v-model="windowStart" type="datetime-local" />
        </label>
        <label>
          <span>结束时间</span>
          <input v-model="windowEnd" type="datetime-local" />
        </label>
      </div>
      <div class="detail-list compact-detail">
        <p><strong>当前预约窗口</strong> {{ preferredWindow }}</p>
        <p><strong>计费规则</strong> {{ dashboard?.billing_rule.rounding_mode ?? 'CEIL_TO_UNIT' }}</p>
      </div>
      <ViewStateNotice :tone="state.tone" :title="state.title" :message="state.message" :detail="state.detail" />
    </article>

    <article class="panel recommendation-panel">
      <SectionHeader
        eyebrow="Slot Suggestions"
        title="推荐车位"
        subtitle="展示可预约车位、预计费用、距离和导航目标，减少在多个页面之间来回切换。"
        :badge="`${recommendations.length} 个候选`"
      />
      <div v-if="latestOrder" class="detail-card journey-card">
        <p class="metric-label">最近订单</p>
        <strong>{{ latestOrder.order_id }}</strong>
        <p>{{ latestOrder.slot_id }} / {{ latestOrder.region_id }}</p>
        <p>账单状态：{{ latestOrder.billing_status }}</p>
      </div>
      <div class="recommend-grid">
        <button
          v-for="item in recommendations"
          :key="String(item.slot_id)"
          class="recommend-card"
          type="button"
          :disabled="busy"
          @click="reserveAndOpenOrders(String(item.slot_id))"
        >
          <div class="card-topline">
            <p class="card-title">{{ item.slot_display_name ?? item.slot_id }}</p>
            <span class="price-tag">¥{{ Number(item.estimated_amount ?? 0).toFixed(2) }}</span>
          </div>
          <p>{{ item.region_label ?? item.slot_id }}</p>
          <p>ETA：{{ item.eta_minutes }} 分钟</p>
          <p>{{ item.destination?.display_name ?? '社区车位入口' }}</p>
        </button>
      </div>
      <div v-if="!recommendations.length && state.tone !== 'loading'" class="empty-state">
        <p class="metric-label">暂无推荐结果</p>
        <p class="muted">请调整区域或预约窗口后重试。</p>
      </div>
    </article>
  </section>
</template>
