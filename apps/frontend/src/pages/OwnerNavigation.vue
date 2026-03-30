<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import SectionHeader from "../components/SectionHeader.vue";
import MapPreview from "../components/MapPreview.vue";
import { fetchNavigation, getStoredOrderId } from "../services/owner";
import type { NavigationView } from "../types/dashboard";

const route = useRoute();

const navigation = ref<NavigationView | null>(null);
const errorText = ref("");
const orderId = computed(() => String(route.query.orderId ?? getStoredOrderId() ?? ""));
const routeSummaryText = computed(() => navigation.value?.route_summary?.summary ?? "请先创建订单，再进入导航页。");

async function loadNavigation() {
  if (!orderId.value) {
    return;
  }
  try {
    navigation.value = await fetchNavigation(orderId.value);
  } catch (error) {
    errorText.value = `导航信息加载失败: ${String(error)}`;
  }
}

watch(orderId, () => {
  void loadNavigation();
}, { immediate: true });
</script>

<template>
  <section class="page-grid nav-page-grid owner-navigation">
    <article class="panel hero-card nav-info-card">
      <SectionHeader
        eyebrow="Navigation Preview"
        title="地图导航引导"
        subtitle="保持 `map_url` 兼容，同时把路线摘要、ETA 和页面内地图预览放到一个统一页面。"
        :badge="navigation ? `ETA ${navigation.eta_minutes} 分钟` : '等待订单'"
      />
      <p class="hero-note">{{ routeSummaryText }}</p>
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
      <div v-else-if="!errorText" class="empty-state">
        <p class="metric-label">等待订单</p>
        <p class="muted">请先创建预约，再进入导航页查看路径。</p>
      </div>
    </article>

    <article class="panel map-panel" v-if="navigation">
      <SectionHeader
        eyebrow="Leaflet + OSM"
        title="目的地地图"
        subtitle="页面内预览和外部地图跳转并存，便于答辩展示与移动端使用。"
        :badge="`ETA ${navigation.eta_minutes} 分钟`"
      />
      <MapPreview
        :lat="Number(navigation.destination?.lat ?? 0)"
        :lng="Number(navigation.destination?.lng ?? 0)"
        :title="String(navigation.slot_display_name ?? navigation.destination?.display_name ?? '目标车位')"
      />
    </article>
  </section>
</template>
