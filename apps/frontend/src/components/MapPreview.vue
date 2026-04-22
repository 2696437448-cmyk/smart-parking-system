<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import L from "leaflet";

const props = defineProps<{
  lat: number;
  lng: number;
  title: string;
  caption?: string;
}>();

const root = ref<HTMLElement | null>(null);
let map: L.Map | null = null;
let marker: L.CircleMarker | null = null;

function renderMap() {
  if (!root.value) {
    return;
  }
  if (!map) {
    map = L.map(root.value, { zoomControl: false, attributionControl: true }).setView([props.lat, props.lng], 16);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);
  }
  if (marker) {
    marker.remove();
  }
  map.setView([props.lat, props.lng], 16);
  marker = L.circleMarker([props.lat, props.lng], {
    radius: 10,
    color: "#ff7f32",
    fillColor: "#ffb26b",
    fillOpacity: 0.9,
    weight: 3,
  }).addTo(map);
  marker.bindPopup(props.title).openPopup();
}

onMounted(() => {
  renderMap();
});

watch(() => [props.lat, props.lng, props.title], () => {
  renderMap();
});

onBeforeUnmount(() => {
  map?.remove();
  map = null;
});
</script>

<template>
  <article class="map-preview-shell">
    <div class="chart-head chart-panel-head">
      <div class="chart-panel-copy">
        <div class="section-header-kicker chart-panel-kicker">
          <p class="eyebrow">地图</p>
          <a-tag color="arcoblue">预览</a-tag>
        </div>
        <h3>{{ title || "目标车位" }}</h3>
        <p class="muted chart-subtitle">查看目标车位位置，并支持跳转外部地图。</p>
      </div>
      <div class="chart-panel-side">
        <p class="muted chart-microcopy">路线预览</p>
      </div>
    </div>
    <div ref="root" class="map-preview leaflet-container"></div>
    <p v-if="caption" class="map-caption">{{ caption }}</p>
  </article>
</template>
