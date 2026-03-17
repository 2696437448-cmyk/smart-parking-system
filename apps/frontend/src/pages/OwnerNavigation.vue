<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, RouterLink } from "vue-router";

const route = useRoute();
const gatewayBase = import.meta.env.VITE_GATEWAY_BASE_URL ?? "http://localhost:8080";
const navigation = ref<Record<string, any> | null>(null);
const errorText = ref("");
const orderId = computed(() => String(route.query.orderId ?? ""));

async function loadNavigation() {
  if (!orderId.value) {
    return;
  }
  try {
    const response = await fetch(`${gatewayBase}/api/v1/owner/navigation/${orderId.value}`, {
      headers: {
        "X-Trace-Id": `frontend-navigation-${Date.now()}`,
      },
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error ?? `http_${response.status}`);
    }
    navigation.value = payload;
  } catch (error) {
    errorText.value = `导航信息加载失败: ${String(error)}`;
  }
}

onMounted(() => {
  void loadNavigation();
});
</script>

<template>
  <section class="panel navigation-panel">
    <div class="action-row">
      <RouterLink class="text-link" to="/owner/dashboard">返回业主端</RouterLink>
      <span class="muted">地图跳转 + ETA 展示</span>
    </div>
    <h3>导航引导</h3>
    <p v-if="errorText" class="error-text">{{ errorText }}</p>
    <div v-if="navigation" class="detail-list">
      <p><strong>订单号</strong> {{ navigation.order_id }}</p>
      <p><strong>目标车位</strong> {{ navigation.slot_id }}</p>
      <p><strong>预计到达</strong> {{ navigation.eta_minutes }} 分钟</p>
      <p><strong>目的地</strong> {{ navigation.destination?.display_name }}</p>
      <p>
        <strong>坐标</strong>
        {{ navigation.destination?.lat }}, {{ navigation.destination?.lng }}
      </p>
      <a class="primary inline-link" :href="String(navigation.map_url)" target="_blank" rel="noreferrer">
        打开地图导航
      </a>
    </div>
    <p v-else-if="!errorText" class="muted">请先在业主端创建订单，再进入导航页。</p>
  </section>
</template>
