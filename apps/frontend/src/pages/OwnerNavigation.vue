<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import MapPreview from "../components/MapPreview.vue";

const route = useRoute();
const gatewayBase = import.meta.env.VITE_GATEWAY_BASE_URL ?? "http://localhost:8080";
const ORDER_STORAGE_KEY = "smartParkingCurrentOrderId";

const navigation = ref<Record<string, any> | null>(null);
const errorText = ref("");
const orderId = computed(() => String(route.query.orderId ?? localStorage.getItem(ORDER_STORAGE_KEY) ?? ""));

async function loadNavigation() {
  if (!orderId.value) {
    return;
  }
  try {
    const response = await fetch(`${gatewayBase}/api/v1/owner/navigation/${orderId.value}`, {
      headers: { "X-Trace-Id": `frontend-navigation-${Date.now()}` },
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
  <section class="page-grid nav-page-grid">
    <article class="panel hero-card nav-info-card">
      <p class="eyebrow">Navigation Preview</p>
      <h3>地图导航引导</h3>
      <p class="muted">保持 `map_url` 兼容，同时提供页面内地图预览与路线摘要。</p>
      <p v-if="errorText" class="error-text">{{ errorText }}</p>
      <div v-if="navigation" class="detail-list compact-detail">
        <p><strong>订单号</strong> {{ navigation.order_id }}</p>
        <p><strong>目标车位</strong> {{ navigation.slot_display_name ?? navigation.slot_id }}</p>
        <p><strong>区域</strong> {{ navigation.region_label }}</p>
        <p><strong>预计到达</strong> {{ navigation.eta_minutes }} 分钟</p>
        <p><strong>路线摘要</strong> {{ navigation.route_summary?.summary }}</p>
        <p><strong>距离</strong> {{ navigation.route_summary?.distance_km }} km</p>
        <a class="primary inline-link" :href="String(navigation.map_url)" target="_blank" rel="noreferrer">打开外部地图</a>
      </div>
      <p v-else-if="!errorText" class="muted">请先创建订单，再进入导航页。</p>
    </article>

    <article class="panel map-panel" v-if="navigation">
      <div class="section-head">
        <div>
          <p class="eyebrow">Leaflet + OSM</p>
          <h3>目的地地图</h3>
        </div>
        <span class="pill ghost">ETA {{ navigation.eta_minutes }} 分钟</span>
      </div>
      <MapPreview
        :lat="Number(navigation.destination?.lat ?? 0)"
        :lng="Number(navigation.destination?.lng ?? 0)"
        :title="String(navigation.slot_display_name ?? navigation.destination?.display_name ?? '目标车位')"
      />
    </article>
  </section>
</template>
