<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
import StatusBadge from "../components/StatusBadge.vue";

const tabs = [
  { to: "/owner/dashboard", label: "推荐" },
  { to: "/owner/orders", label: "订单" },
  { to: "/owner/navigation", label: "导航" },
];
</script>

<template>
  <div class="experience-shell owner-shell owner-shell-refined">
    <header class="shell-banner owner-banner">
      <p class="eyebrow">Owner Experience</p>
      <div class="shell-banner-row">
        <div class="shell-banner-copy">
          <h1>智慧停车业主端</h1>
          <p>
            聚焦预约、账单与导航的移动优先体验，保留 Web 演示能力，同时继续兼容 Capacitor App 壳层。
          </p>
        </div>
        <div class="chip-row">
          <StatusBadge label="Capacitor Ready" tone="accent" />
          <StatusBadge label="Leaflet Map" tone="default" />
          <StatusBadge label="Billing Flow" tone="calm" />
        </div>
      </div>
    </header>

    <nav class="owner-top-nav" aria-label="owner top navigation">
      <RouterLink v-for="tab in tabs" :key="tab.to" :to="tab.to">{{ tab.label }}</RouterLink>
    </nav>

    <main class="experience-main">
      <RouterView />
    </main>

    <nav class="bottom-nav owner-bottom-nav" aria-label="owner bottom navigation">
      <RouterLink v-for="tab in tabs" :key="tab.to" :to="tab.to">{{ tab.label }}</RouterLink>
    </nav>
  </div>
</template>
