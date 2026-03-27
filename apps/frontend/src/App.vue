<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";

const route = useRoute();

const pageTitle = computed(() => {
  if (route.path.startsWith("/admin")) {
    return "物业经营驾驶舱";
  }
  if (route.path.startsWith("/owner/navigation")) {
    return "导航引导";
  }
  if (route.path.startsWith("/owner/orders")) {
    return "订单与账单";
  }
  return "业主端 App";
});

const tabs = [
  { to: "/owner/dashboard", label: "推荐" },
  { to: "/owner/orders", label: "订单" },
  { to: "/owner/navigation", label: "导航" },
  { to: "/admin/monitor", label: "物业" },
];
</script>

<template>
  <div class="app-shell">
    <aside class="rail">
      <p class="eyebrow">Step27-Step29</p>
      <h1>Smart Parking</h1>
      <p class="rail-copy">
        在 Step24 业务闭环基础上，继续增强近真实数据、跨端 App、地图导航与经营图表。
      </p>
      <nav class="rail-nav">
        <RouterLink v-for="tab in tabs" :key="tab.to" :to="tab.to">{{ tab.label }}</RouterLink>
      </nav>
    </aside>

    <div class="shell-main">
      <header class="topbar">
        <div>
          <p class="eyebrow">Owner / Admin Experience</p>
          <h2>{{ pageTitle }}</h2>
        </div>
        <div class="badge-row">
          <span class="pill">Capacitor</span>
          <span class="pill">Leaflet</span>
          <span class="pill">ECharts</span>
        </div>
        <p class="muted shell-capabilities">Pinia · WebSocket · Polling · 手动重连</p>
      </header>

      <main class="page-body">
        <RouterView />
      </main>
    </div>

    <nav class="bottom-nav">
      <RouterLink v-for="tab in tabs" :key="tab.to" :to="tab.to">{{ tab.label }}</RouterLink>
    </nav>
  </div>
</template>
