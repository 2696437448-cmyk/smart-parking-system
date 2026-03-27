<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

const gatewayBase = import.meta.env.VITE_GATEWAY_BASE_URL ?? "http://localhost:8080";
const ORDER_STORAGE_KEY = "smartParkingCurrentOrderId";
const route = useRoute();
const router = useRouter();

const orderDetail = ref<Record<string, any> | null>(null);
const errorText = ref("");
const loading = ref(false);
const orderId = computed(() => String(route.query.orderId ?? localStorage.getItem(ORDER_STORAGE_KEY) ?? ""));

async function readJson(url: string, options: RequestInit = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "X-Trace-Id": `frontend-orders-${Date.now()}`,
      ...(options.headers ?? {}),
    },
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error ?? `http_${response.status}`);
  }
  return payload;
}

async function loadOrder() {
  if (!orderId.value) {
    return;
  }
  loading.value = true;
  errorText.value = "";
  try {
    orderDetail.value = await readJson(`${gatewayBase}/api/v1/owner/orders/${orderId.value}`);
    localStorage.setItem(ORDER_STORAGE_KEY, orderId.value);
  } catch (error) {
    errorText.value = `订单查询失败: ${String(error)}`;
  } finally {
    loading.value = false;
  }
}

async function completeOrder() {
  if (!orderId.value || !orderDetail.value) {
    return;
  }
  loading.value = true;
  errorText.value = "";
  try {
    await readJson(`${gatewayBase}/api/v1/owner/orders/${orderId.value}/complete`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Idempotency-Key": `complete-${orderId.value}`,
      },
      body: JSON.stringify({ ended_at: orderDetail.value.ended_at }),
    });
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

onMounted(() => {
  void loadOrder();
});
</script>

<template>
  <section class="page-grid owner-page-grid">
    <article class="panel hero-card">
      <p class="eyebrow">Order Center</p>
      <h3>订单与账单</h3>
      <p class="muted">这一页用于查看账单、完成停车结算，并进入导航页。</p>
      <div class="action-row">
        <button class="primary" type="button" :disabled="loading" @click="loadOrder">刷新订单</button>
        <button type="button" :disabled="!orderId" @click="openNavigation">查看导航</button>
      </div>
      <p v-if="errorText" class="error-text">{{ errorText }}</p>
    </article>

    <article class="panel order-panel">
      <div v-if="orderDetail" class="detail-list order-stack">
        <div class="bill-card accent-card">
          <span class="metric-label">当前订单</span>
          <strong>{{ orderDetail.order_id }}</strong>
          <p>{{ orderDetail.slot_id }} / {{ orderDetail.region_id }}</p>
        </div>
        <div class="bill-card">
          <span class="metric-label">预估金额</span>
          <strong>¥{{ Number(orderDetail.estimated_amount ?? 0).toFixed(2) }}</strong>
          <p>计费状态：{{ orderDetail.billing_status }}</p>
        </div>
        <div class="bill-card">
          <span class="metric-label">最终金额</span>
          <strong>¥{{ Number(orderDetail.final_amount ?? 0).toFixed(2) }}</strong>
          <p>计费分钟：{{ orderDetail.billable_minutes }}</p>
        </div>
        <div class="detail-list compact-detail">
          <p><strong>开始时间</strong> {{ orderDetail.started_at }}</p>
          <p><strong>结束时间</strong> {{ orderDetail.ended_at }}</p>
          <p><strong>结算日期</strong> {{ orderDetail.recognized_on || "未结算" }}</p>
          <p><strong>计费规则</strong> {{ orderDetail.billing_rule?.timezone }} / {{ orderDetail.billing_rule?.unit_minutes }} 分钟</p>
        </div>
        <button class="primary" type="button" :disabled="loading" @click="completeOrder">完成停车并结算</button>
      </div>
      <p v-else class="muted">暂无订单，请先在“推荐”页创建预约。</p>
    </article>
  </section>
</template>
