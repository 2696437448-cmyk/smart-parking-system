<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import MetricCard from "../components/MetricCard.vue";
import SectionHeader from "../components/SectionHeader.vue";
import { completeOrder, fetchOrderDetail, getStoredOrderId, setStoredOrderId } from "../services/owner";
import type { OrderDetail } from "../types/dashboard";

const route = useRoute();
const router = useRouter();

const orderDetail = ref<OrderDetail | null>(null);
const errorText = ref("");
const loading = ref(false);
const orderId = computed(() => String(route.query.orderId ?? getStoredOrderId() ?? ""));

async function loadOrder() {
  if (!orderId.value) {
    return;
  }
  loading.value = true;
  errorText.value = "";
  try {
    orderDetail.value = await fetchOrderDetail(orderId.value);
    setStoredOrderId(orderId.value);
  } catch (error) {
    errorText.value = `订单查询失败: ${String(error)}`;
  } finally {
    loading.value = false;
  }
}

async function finishOrder() {
  if (!orderId.value || !orderDetail.value) {
    return;
  }
  loading.value = true;
  errorText.value = "";
  try {
    await completeOrder(orderId.value, orderDetail.value.ended_at);
    await loadOrder();
  } catch (error) {
    errorText.value = `结算失败: ${String(error)}`;
  } finally {
    loading.value = false;
  }
}

function openNavigation() {
  if (!orderId.value) {
    return;
  }
  void router.push({ path: "/owner/navigation", query: { orderId: orderId.value } });
}

const orderStatusNote = computed(() => {
  // The empty branch exists because the order page must still render when the owner has not created a reservation yet.
  if (!orderDetail.value) {
    return "暂无订单，请先完成预约。";
  }
  // The confirmed branch exists so the UI can explain that billing has already been finalized.
  if (orderDetail.value.billing_status === "CONFIRMED") {
    return "订单已结算，可继续查看导航和费用明细。";
  }
  // The estimated branch exists so the UI can encourage the owner to complete the parking flow.
  return "订单已创建，完成停车后可确认最终账单。";
});

watch(orderId, () => {
  void loadOrder();
}, { immediate: true });
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
        <button class="primary" type="button" :disabled="loading" @click="loadOrder">刷新订单</button>
        <button type="button" :disabled="!orderId" @click="openNavigation">查看导航</button>
      </div>
      <p v-if="errorText" class="error-text">{{ errorText }}</p>
    </article>

    <article class="panel order-panel">
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
          <p><strong>结算日期</strong> {{ orderDetail.recognized_on || "未结算" }}</p>
          <p><strong>计费规则</strong> {{ orderDetail.billing_rule?.timezone }} / {{ orderDetail.billing_rule?.unit_minutes }} 分钟</p>
        </div>
        <button class="primary" type="button" :disabled="loading" @click="finishOrder">完成停车并结算</button>
      </div>
      <div v-else class="empty-state">
        <p class="metric-label">暂无订单</p>
        <p class="muted">请先在“推荐”页创建预约，再回到此页查看账单。</p>
      </div>
    </article>
  </section>
</template>
