<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const gatewayBase = import.meta.env.VITE_GATEWAY_BASE_URL ?? "http://localhost:8080";
const ORDER_STORAGE_KEY = "smartParkingCurrentOrderId";
const OWNER_ORDER_DETAIL_API_BASE = "/api/v1/owner/orders/";

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
const userId = ref("owner-app-001");
const location = ref("R1");
const windowStart = ref(toLocalInput(now));
const windowEnd = ref(toLocalInput(plusMinutes(now, 60)));
const loading = ref(false);
const recommendations = ref<Array<Record<string, any>>>([]);
const errorText = ref("");
const activeOrderId = ref(localStorage.getItem(ORDER_STORAGE_KEY) ?? "");

const preferredWindow = computed(() => `${windowStart.value}:00/${windowEnd.value}:00`);
const activeSummary = computed(() => {
  if (!activeOrderId.value) {
    return "暂无进行中的预约，可直接创建新预约。";
  }
  return `当前进行中订单：${activeOrderId.value}`;
});

async function readJson(url: string, options: RequestInit = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "X-Trace-Id": `frontend-owner-${Date.now()}`,
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
    const orderId = String(payload.order_id ?? payload.reservation_id ?? "");
    if (orderId) {
      activeOrderId.value = orderId;
      localStorage.setItem(ORDER_STORAGE_KEY, orderId);
      await router.push({ path: "/owner/orders", query: { orderId } });
    }
  } catch (error) {
    errorText.value = `预约失败: ${String(error)}`;
  } finally {
    loading.value = false;
  }
}

function openOrders() {
  void router.push({ path: "/owner/orders", query: activeOrderId.value ? { orderId: activeOrderId.value } : {} });
}

onMounted(() => {
  void loadRecommendations();
});
</script>

<template>
  <section class="page-grid owner-page-grid">
    <article class="panel hero-card owner-hero">
      <p class="eyebrow">Owner App</p>
      <h3>移动优先预约入口</h3>
      <p class="muted">
        这一页负责推荐与预约创建；订单详情、账单与结算从“订单”页继续完成。
      </p>
      <div class="hero-metrics">
        <div class="metric-pill">
          <span class="metric-label">区域</span>
          <strong>{{ location }}</strong>
        </div>
        <div class="metric-pill wide">
          <span class="metric-label">状态</span>
          <strong>{{ activeSummary }}</strong>
        </div>
      </div>
      <div class="action-row">
        <button class="primary" type="button" @click="openOrders">查看订单</button>
        <button type="button" @click="loadRecommendations">刷新推荐</button>
      </div>
    </article>

    <article class="panel form-panel">
      <h3>预约参数</h3>
      <div class="field-grid compact-grid">
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
      <p class="muted">当前预约窗口：{{ preferredWindow }}</p>
      <p v-if="errorText" class="error-text">{{ errorText }}</p>
    </article>

    <article class="panel recommendation-panel">
      <div class="section-head">
        <div>
          <p class="eyebrow">Slot Suggestions</p>
          <h3>推荐车位</h3>
        </div>
        <span class="pill ghost">{{ recommendations.length }} 个候选</span>
      </div>
      <div class="recommend-list mobile-cards">
        <button
          v-for="item in recommendations"
          :key="String(item.slot_id)"
          class="recommend-card"
          type="button"
          :disabled="loading"
          @click="reserve(String(item.slot_id))"
        >
          <div class="card-topline">
            <p class="card-title">{{ item.slot_display_name ?? item.slot_id }}</p>
            <span class="price-tag">¥{{ Number(item.estimated_amount ?? 0).toFixed(2) }}</span>
          </div>
          <p>{{ item.region_label ?? item.slot_id }}</p>
          <p>ETA：{{ item.eta_minutes }} 分钟</p>
          <p>{{ item.destination?.display_name }}</p>
        </button>
      </div>
    </article>
  </section>
</template>
