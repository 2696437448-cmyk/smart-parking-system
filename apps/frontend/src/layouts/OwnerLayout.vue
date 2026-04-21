<script setup lang="ts">
import { computed } from "vue";
import { IconCompass, IconFire, IconNotification } from "@arco-design/web-vue/es/icon";
import { RouterLink, RouterView, useRoute } from "vue-router";

const route = useRoute();
const tabs = [
  { to: "/owner/dashboard", label: "推荐" },
  { to: "/owner/orders", label: "订单" },
  { to: "/owner/navigation", label: "导航" },
];

const activeTab = computed(() => tabs.find((tab) => route.path === tab.to) ?? tabs[0]);

const journeyMeta = computed(() => {
  switch (activeTab.value.to) {
    case "/owner/orders":
      return {
        eyebrow: "Order Mission",
        title: "停车旅程任务中心",
        summary: "当前重点切换到账单确认与停车结算，信息顺序会围绕订单状态、金额和下一步动作展开。",
        stage: "账单与状态确认",
      };
    case "/owner/navigation":
      return {
        eyebrow: "Navigation Mission",
        title: "停车旅程任务中心",
        summary: "当前重点切换到目标车位导航，ETA、路线摘要和地图预览被压缩到同一条任务视图中。",
        stage: "目标车位导航",
      };
    default:
      return {
        eyebrow: "Reservation Mission",
        title: "停车旅程任务中心",
        summary: "当前重点是完成推荐、预约和订单串联，让首页先承担停车任务入口，再自然过渡到账单与导航。",
        stage: "智能预约中枢",
      };
  }
});
</script>

<template>
  <div class="experience-shell owner-shell">
    <header class="shell-banner owner-banner owner-journey-header">
      <div class="shell-status-strip">
        <a-tag color="arcoblue">Owner AI Assist</a-tag>
        <a-tag color="cyan">Journey Status</a-tag>
        <a-tag color="gold">Smart Parking</a-tag>
      </div>
      <div class="owner-command-bar owner-journey-bar">
        <div class="shell-banner-copy owner-journey-copy">
          <p class="eyebrow">{{ journeyMeta.eyebrow }}</p>
          <h1>{{ journeyMeta.title }}</h1>
          <p>{{ journeyMeta.summary }}</p>
        </div>
        <div class="chip-row owner-journey-actions">
          <span class="pill"><IconCompass /> 智能推荐</span>
          <span class="pill"><IconFire /> 计费感知</span>
          <span class="pill"><IconNotification /> 路径同步</span>
        </div>
      </div>
      <div class="owner-journey-meta">
        <span class="pill ghost">当前阶段：{{ journeyMeta.stage }}</span>
        <span class="pill">当前页面：{{ activeTab.label }}</span>
        <span class="pill">移动端 / Web 双端协同</span>
      </div>
    </header>

    <nav class="owner-top-nav" aria-label="owner top navigation">
      <RouterLink
        v-for="tab in tabs"
        :key="tab.to"
        :to="tab.to"
        :class="['owner-nav-pill', { active: route.path === tab.to }]"
      >
        {{ tab.label }}
      </RouterLink>
    </nav>

    <main class="experience-main">
      <RouterView />
    </main>

    <nav class="bottom-nav owner-bottom-nav owner-mobile-dock" aria-label="owner bottom navigation">
      <RouterLink
        v-for="tab in tabs"
        :key="tab.to"
        :to="tab.to"
        :class="['owner-nav-pill', { active: route.path === tab.to }]"
      >
        {{ tab.label }}
      </RouterLink>
    </nav>
  </div>
</template>
