<script setup lang="ts">
import { computed, defineAsyncComponent } from "vue";
import KeyValueList from "../components/KeyValueList.vue";
import SectionHeader from "../components/SectionHeader.vue";
import StatusBadge from "../components/StatusBadge.vue";
import ViewStateNotice from "../components/ViewStateNotice.vue";
import { ownerNavigationMetaItems, routeSummaryLines } from "../presenters/owner";
import { useOwnerNavigationView } from "../composables/useOwnerNavigationView";

const MapPreview = defineAsyncComponent(() => import("../components/MapPreview.vue"));
const { navigation, destinationTitle, routeSummaryText, state } = useOwnerNavigationView();
const navigationMetaItems = computed(() => ownerNavigationMetaItems(navigation.value));
const routeSummaryTextLines = computed(() => routeSummaryLines(navigation.value));
</script>

<template>
  <section class="page-grid nav-page-grid owner-navigation">
    <article class="panel hero-card nav-info-card">
      <SectionHeader
        eyebrow="Navigation Preview"
        title="地图导航引导"
        subtitle="保持 `map_url` 兼容，同时把路线摘要、ETA 和页面内地图预览放到一个统一页面。"
        :badge="navigation ? `ETA ${navigation.eta_minutes} 分钟` : '等待订单'"
        badge-tone="accent"
      />
      <p class="hero-note">{{ routeSummaryText }}</p>
      <ViewStateNotice :tone="state.tone" :title="state.title" :message="state.message" :detail="state.detail" :badge="state.badge" />
      <div v-if="navigation" class="detail-list compact-detail">
        <div class="navigation-badge-row">
          <StatusBadge :label="navigation.region_label" tone="accent" />
          <StatusBadge :label="navigation.slot_display_name ?? navigation.slot_id" tone="default" />
        </div>
        <KeyValueList :items="navigationMetaItems" />
        <div class="route-line-list">
          <p v-for="line in routeSummaryTextLines" :key="line" class="muted route-line">{{ line }}</p>
        </div>
        <a class="primary inline-link" :href="String(navigation.map_url)" target="_blank" rel="noreferrer">打开外部地图</a>
      </div>
      <div v-else-if="state.tone !== 'loading'" class="empty-state">
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
        badge-tone="default"
      />
      <MapPreview
        :lat="Number(navigation.destination?.lat ?? 0)"
        :lng="Number(navigation.destination?.lng ?? 0)"
        :title="destinationTitle"
        :caption="routeSummaryTextLines.join(' · ')"
      />
    </article>
  </section>
</template>
