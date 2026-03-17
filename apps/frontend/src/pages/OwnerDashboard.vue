<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const gatewayBase = import.meta.env.VITE_GATEWAY_BASE_URL ?? "http://localhost:8080";

function pad(value: number): string {
  return value.toString().padStart(2, "0");
}

function toLocalInput(date: Date): string {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function plusMinutes(base: Date, minutes: number): Date {
  return new Date(base.getTime() + minutes * 60 * 1000);
}

const now = new Date();
const userId = ref("owner-demo-001");
const location = ref("R1");
const windowStart = ref(toLocalInput(now));
const windowEnd = ref(toLocalInput(plusMinutes(now, 60)));
const loading = ref(false);
const recommendations = ref<Array<Record<string, any>>>([]);
const orderDetail = ref<Record<string, any> | null>(null);
const errorText = ref("");

const preferredWindow = computed(() => `${windowStart.value}:00/${windowEnd.value}:00`);
const currentOrderId = computed(() => String(orderDetail.value?.order_id ?? ""));

async function readJson(url: string, options: RequestInit = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "X-Trace-Id": `frontend-${Date.now()}`,
      ...(options.headers ?? {}),
    },
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error ?? `http_${response.status}`);
  }
  return payload;
}

async function loadRecommendations() {
  loading.value = true;
  errorText.value = "";
  try {
    const url = new URL(`${gatewayBase}/api/v1/owner/recommendations`);
    url.searchParams.set("location", location.value);
    url.searchParams.set("preferred_window", preferredWindow.value);
    const payload = await readJson(url.toString());
    recommendations.value = payload.results ?? [];
  } catch (error) {
    errorText.value = `推荐加载失败: ${String(error)}`;
  } finally {
    loading.value = false;
  }
}

async function loadOrder(orderId: string) {
  if (!orderId) {
    return;
  }
  try {
    orderDetail.value = await readJson(`${gatewayBase}/api/v1/owner/orders/${orderId}`);
  } catch (error) {
    errorText.value = `订单查询失败: ${String(error)}`;
  }
}

async function reserve(slotId: string) {
  loading.value = true;
  errorText.value = "";
  try {
    const payload = await readJson(`${gatewayBase}/api/v1/owner/reservations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Idempotency-Key": `reserve-${userId.value}-${slotId}-${windowStart.value}`,
      },
      body: JSON.stringify({
        user_id: userId.value,
        preferred_window: preferredWindow.value,
        location: location.value,
        slot_id: slotId,
      }),
    });
    await loadOrder(String(payload.order_id ?? payload.reservation_id ?? ""));
  } catch (error) {
    errorText.value = `预约失败: ${String(error)}`;
  } finally {
    loading.value = false;
  }
}

async function completeOrder() {
  if (!currentOrderId.value) {
    return;
  }
  loading.value = true;
  errorText.value = "";
  try {
    await readJson(`${gatewayBase}/api/v1/owner/orders/${currentOrderId.value}/complete`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Idempotency-Key": `complete-${currentOrderId.value}`,
      },
      body: JSON.stringify({
        ended_at: `${windowEnd.value}:00`,
      }),
    });
    await loadOrder(currentOrderId.value);
  } catch (error) {
    errorText.value = `结算失败: ${String(error)}`;
  } finally {
    loading.value = false;
  }
}

function openNavigation() {
  if (!currentOrderId.value) {
    return;
  }
  void router.push({ path: "/owner/navigation", query: { orderId: currentOrderId.value } });
}

onMounted(() => {
  void loadRecommendations();
});
</script>

<template>
  <section class="panel-grid owner-grid">
    <article class="panel form-panel">
      <h3>预约表单</h3>
      <div class="field-grid">
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
      <div class="action-row">
        <button class="primary" type="button" :disabled="loading" @click="loadRecommendations">
          {{ loading ? "处理中..." : "获取推荐" }}
        </button>
        <span class="muted">当前窗口：{{ preferredWindow }}</span>
      </div>
      <p v-if="errorText" class="error-text">{{ errorText }}</p>
    </article>

    <article class="panel">
      <h3>推荐车位</h3>
      <div class="recommend-list">
        <button
          v-for="item in recommendations"
          :key="String(item.slot_id)"
          class="recommend-card"
          type="button"
          :disabled="loading"
          @click="reserve(String(item.slot_id))"
        >
          <p class="card-title">{{ item.slot_id }}</p>
          <p>预估金额：¥{{ Number(item.estimated_amount ?? 0).toFixed(2) }}</p>
          <p>ETA：{{ item.eta_minutes }} 分钟</p>
          <p>{{ item.destination?.display_name }}</p>
        </button>
      </div>
    </article>

    <article class="panel order-panel">
      <h3>当前订单 / 账单</h3>
      <div v-if="orderDetail" class="detail-list">
        <p><strong>订单号</strong> {{ orderDetail.order_id }}</p>
        <p><strong>车位</strong> {{ orderDetail.slot_id }}</p>
        <p><strong>计费状态</strong> {{ orderDetail.billing_status }}</p>
        <p><strong>预估金额</strong> ¥{{ Number(orderDetail.estimated_amount ?? 0).toFixed(2) }}</p>
        <p><strong>最终金额</strong> ¥{{ Number(orderDetail.final_amount ?? 0).toFixed(2) }}</p>
        <p><strong>计费分钟</strong> {{ orderDetail.billable_minutes }}</p>
        <p><strong>结算日期</strong> {{ orderDetail.recognized_on || "未结算" }}</p>
        <div class="action-row">
          <button class="primary" type="button" @click="completeOrder">完成停车并结算</button>
          <button type="button" @click="openNavigation">查看导航</button>
        </div>
      </div>
      <p v-else class="muted">选择推荐车位后会在这里展示订单与账单详情。</p>
    </article>
  </section>
</template>
