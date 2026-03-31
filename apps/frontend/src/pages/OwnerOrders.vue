<script setup lang="ts">
import MetricCard from "../components/MetricCard.vue";
import SectionHeader from "../components/SectionHeader.vue";
import ViewStateNotice from "../components/ViewStateNotice.vue";
import { useOwnerOrderView } from "../composables/useOwnerOrderView";

const { orderDetail, busy, state, orderStatusNote, loadOrder, finishOrder, openNavigation } = useOwnerOrderView();
</script>

<template>
  <section class="page-grid owner-page-grid owner-orders">
    <article class="panel hero-card">
      <SectionHeader
        eyebrow="Order Center"
        title="订单与账单"
        subtitle="查看预约结果、计费规则与最终账单，并从这里进入导航引导。"
        :badge="orderDetail?.billing_status ?? 'WAITING'"
      />
      <p class="hero-note">{{ orderStatusNote }}</p>
      <div class="action-row">
        <button class="primary" type="button" :disabled="busy" @click="loadOrder">刷新订单</button>
        <button type="button" :disabled="busy || !orderDetail" @click="openNavigation">查看导航</button>
      </div>
    </article>

    <article class="panel order-panel">
      <ViewStateNotice :tone="state.tone" :title="state.title" :message="state.message" :detail="state.detail" />
      <div v-if="orderDetail" class="detail-list order-stack">
        <div class="metric-grid compact-metric-grid">
          <MetricCard label="当前订单" :value="orderDetail.order_id" :note="`${orderDetail.slot_id} / ${orderDetail.region_id}`" tone="accent" />
          <MetricCard label="预估金额" :value="`¥${Number(orderDetail.estimated_amount ?? 0).toFixed(2)}`" :note="`状态：${orderDetail.billing_status}`" />
          <MetricCard label="最终金额" :value="`¥${Number(orderDetail.final_amount ?? 0).toFixed(2)}`" :note="`计费分钟：${orderDetail.billable_minutes}`" tone="calm" />
          <MetricCard label="结算日期" :value="orderDetail.recognized_on || '未结算'" :note="orderDetail.billing_rule?.timezone ?? 'Asia/Shanghai'" />
        </div>
        <div class="detail-list compact-detail">
          <p><strong>开始时间</strong> {{ orderDetail.started_at }}</p>
          <p><strong>结束时间</strong> {{ orderDetail.ended_at }}</p>
          <p><strong>结算日期</strong> {{ orderDetail.recognized_on || '未结算' }}</p>
          <p><strong>计费规则</strong> {{ orderDetail.billing_rule?.timezone }} / {{ orderDetail.billing_rule?.unit_minutes }} 分钟</p>
        </div>
        <button class="primary" type="button" :disabled="busy" @click="finishOrder">完成停车并结算</button>
      </div>
      <div v-else-if="state.tone !== 'loading'" class="empty-state">
        <p class="metric-label">暂无订单</p>
        <p class="muted">请先在“推荐”页创建预约，再回到此页查看账单。</p>
      </div>
    </article>
  </section>
</template>
