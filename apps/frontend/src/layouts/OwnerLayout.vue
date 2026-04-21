<script setup lang="ts">
import { IconCompass, IconFire, IconNotification } from "@arco-design/web-vue/es/icon";
import { RouterLink, RouterView, useRoute } from "vue-router";

const route = useRoute();
const tabs = [
  { to: "/owner/dashboard", label: "推荐" },
  { to: "/owner/orders", label: "订单" },
  { to: "/owner/navigation", label: "导航" },
];
</script>

<template>
  <div class="experience-shell owner-shell">
    <header class="shell-banner owner-banner">
      <div class="shell-status-strip">
        <a-tag color="arcoblue">Owner AI Assist</a-tag>
        <a-tag color="cyan">Journey Status</a-tag>
        <a-tag color="gold">Smart Parking</a-tag>
      </div>
      <div class="owner-command-bar">
        <div class="shell-banner-copy">
          <p class="eyebrow">Owner Control Surface</p>
          <h1>智慧停车业主控制台</h1>
          <p>让推荐、预约、账单与导航收束成一条可执行的停车旅程，保持移动端和 Web 端都清晰可用。</p>
        </div>
        <div class="chip-row">
          <span class="pill"><IconCompass /> 智能推荐</span>
          <span class="pill"><IconFire /> 计费感知</span>
          <span class="pill"><IconNotification /> 路径同步</span>
        </div>
      </div>
    </header>

    <nav class="owner-top-nav" aria-label="owner top navigation">
      <RouterLink v-for="tab in tabs" :key="tab.to" :to="tab.to" :class="{ active: route.path === tab.to }">
        {{ tab.label }}
      </RouterLink>
    </nav>

    <main class="experience-main">
      <RouterView />
    </main>

    <nav class="bottom-nav owner-bottom-nav" aria-label="owner bottom navigation">
      <RouterLink v-for="tab in tabs" :key="tab.to" :to="tab.to" :class="{ active: route.path === tab.to }">
        {{ tab.label }}
      </RouterLink>
    </nav>
  </div>
</template>
