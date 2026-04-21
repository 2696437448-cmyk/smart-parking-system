<script setup lang="ts">
import { computed, defineAsyncComponent } from "vue";
import KeyValueList from "../components/KeyValueList.vue";
import SectionHeader from "../components/SectionHeader.vue";
import ViewStateNotice from "../components/ViewStateNotice.vue";
import { ownerNavigationMetaItems, routeSummaryLines } from "../presenters/owner";
import { useOwnerNavigationView } from "../composables/useOwnerNavigationView";

const MapPreview = defineAsyncComponent(() => import("../components/MapPreview.vue"));
const { navigation, destinationTitle, routeSummaryText, state } = useOwnerNavigationView();
const navigationMetaItems = computed(() => ownerNavigationMetaItems(navigation.value));
const route_summary = computed(() => navigation.value?.route_summary ?? null);
const routeSummaryTextLines = computed(() => routeSummaryLines(navigation.value));
</script>

<template>
  <section class="page-grid nav-page-grid owner-navigation navigation-task-panel">
    <article class="panel hero-card nav-info-card" v-motion-slide-visible-once-left>
      <SectionHeader
        eyebrow="Navigation Task"
        title="目标车位导航"
        subtitle="把 ETA、路线摘要和目标锁定信息集中呈现，让导航页像一张任务面板。"
        :badge="navigation ? `ETA ${navigation.eta_minutes} 分钟` : '等待订单'"
        badge-tone="accent"
      />
      <p class="hero-note">{{ routeSummaryText }}</p>
      <ViewStateNotice :tone="state.tone" :title="state.title" :message="state.message" :detail="state.detail" :badge="state.badge" />
      <div v-if="navigation" class="detail-list compact-detail">
        <div class="navigation-badge-row">
          <a-tag color="cyan">{{ navigation.region_label }}</a-tag>
          <a-tag color="arcoblue">{{ navigation.slot_display_name ?? navigation.slot_id }}</a-tag>
        </div>
        <KeyValueList :items="navigationMetaItems" />
        <div class="route-line-list">
          <p v-for="line in routeSummaryTextLines" :key="line" class="muted route-line">{{ line }}</p>
        </div>
        <a-button type="primary" class="inline-link" :href="String(navigation.map_url)" target="_blank">打开外部地图</a-button>
      </div>
      <div v-else-if="state.tone !== 'loading'" class="empty-state">
        <p class="metric-label">等待订单</p>
        <p class="muted">请先创建预约，再进入导航页查看路径。</p>
      </div>
    </article>

    <article class="panel map-panel" v-if="navigation" v-motion-slide-visible-once-right>
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
        :caption="route_summary?.summary ?? routeSummaryTextLines.join(' · ')"
      />
    </article>
  </section>
</template>
