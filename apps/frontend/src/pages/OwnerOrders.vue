<script setup lang="ts">
import { computed } from "vue";
import KeyValueList from "../components/KeyValueList.vue";
import MetricCard from "../components/MetricCard.vue";
import SectionHeader from "../components/SectionHeader.vue";
import StatusBadge from "../components/StatusBadge.vue";
import ViewStateNotice from "../components/ViewStateNotice.vue";
import { formatCurrency } from "../presenters/format";
import { ownerOrderMetaItems } from "../presenters/owner";
import { useOwnerOrderView } from "../composables/useOwnerOrderView";

const { orderDetail, busy, state, orderStatusNote, loadOrder, finishOrder, openNavigation } = useOwnerOrderView();
const orderMetaItems = computed(() => ownerOrderMetaItems(orderDetail.value));
</script>

<template>
  <section class="page-grid owner-page-grid owner-orders order-task-flow">
    <article class="panel hero-card" v-motion-slide-visible-once-bottom>
      <SectionHeader
        eyebrow="Order Task Flow"
        title="订单与账单任务流"
        subtitle="让订单状态、金额信息和下一步动作形成清晰顺序，而不是平铺展示。"
        :badge="orderDetail?.billing_status ?? 'WAITING'"
        badge-tone="accent"
      >
        <template #actions>
          <a-space class="action-row" wrap size="medium">
            <a-button type="primary" :loading="busy" @click="loadOrder">刷新订单</a-button>
            <a-button :disabled="busy || !orderDetail" @click="openNavigation">查看导航</a-button>
          </a-space>
        </template>
      </SectionHeader>
      <p class="hero-note">{{ orderStatusNote }}</p>
      <div class="order-status-band">
        <StatusBadge :label="orderDetail?.billing_status ?? 'WAITING'" tone="accent" />
        <p class="muted">先完成账单确认，再继续进入导航和停车结算。</p>
      </div>
    </article>

    <article class="panel order-panel billing-summary-card" v-motion-slide-visible-once-top>
      <ViewStateNotice :tone="state.tone" :title="state.title" :message="state.message" :detail="state.detail" :badge="state.badge" />
      <div v-if="orderDetail" class="detail-list order-stack">
        <div class="order-inline-status order-status-band">
          <StatusBadge :label="orderDetail.billing_status" tone="accent" />
          <p class="muted">当前订单已进入账单中心，可继续查看费用明细与导航入口。</p>
        </div>
        <div class="metric-grid compact-metric-grid">
          <MetricCard label="当前订单" :value="orderDetail.order_id" :note="`${orderDetail.slot_id} / ${orderDetail.region_id}`" tone="accent" eyebrow="Order" />
          <MetricCard label="预估金额" :value="formatCurrency(orderDetail.estimated_amount)" :note="`状态：${orderDetail.billing_status}`" />
          <MetricCard label="最终金额" :value="formatCurrency(orderDetail.final_amount)" :note="`计费分钟：${orderDetail.billable_minutes}`" tone="calm" />
          <MetricCard label="结算日期" :value="orderDetail.recognized_on || '未结算'" :note="orderDetail.billing_rule?.timezone ?? 'Asia/Shanghai'" />
        </div>
        <KeyValueList :items="orderMetaItems" />
        <div class="task-footer-actions">
          <a-button type="primary" class="settle-action" :loading="busy" @click="finishOrder">完成停车并结算</a-button>
          <a-button :disabled="busy || !orderDetail" @click="openNavigation">前往导航</a-button>
        </div>
      </div>
      <div v-else-if="state.tone !== 'loading'" class="empty-state">
        <p class="metric-label">暂无订单</p>
        <p class="muted">请先在“推荐”页创建预约，再回到此页查看账单。</p>
      </div>
    </article>
  </section>
</template>
