<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, RouterView, useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const tabs = [
  { to: "/owner/dashboard", label: "首页" },
  { to: "/owner/orders", label: "订单" },
  { to: "/owner/navigation", label: "导航" },
];

const activeTab = computed(() => tabs.find((tab) => route.path === tab.to) ?? tabs[0]);
const currentUser = computed(() => auth.currentUser);

const pageMeta = computed(() => {
  switch (activeTab.value.to) {
    case "/owner/orders":
      return {
        title: "订单",
        summary: "查看当前订单、费用和处理进度。",
        status: "待处理",
        sideNote: "当前页重点是确认状态和完成结算。",
      };
    case "/owner/navigation":
      return {
        title: "导航",
        summary: "查看目标车位、路线摘要和地图。",
        status: "可导航",
        sideNote: "当前页重点是路线和地图展示。",
      };
    default:
      return {
        title: "首页",
        summary: "查看推荐结果并发起停车预约。",
        status: "服务中",
        sideNote: "当前页重点是推荐、预约和最近订单。",
      };
  }
});

async function logout() {
  await auth.logout();
  await router.replace("/login");
}
</script>

<template>
  <div class="experience-shell owner-shell">
    <aside class="owner-sidebar" aria-label="用户端导航">
      <div class="owner-sidebar-brand">
        <p class="owner-brand-title">智慧停车</p>
        <p class="muted owner-brand-subtitle">{{ currentUser?.display_name ?? "停车服务" }}</p>
      </div>
      <nav class="owner-sidebar-nav">
        <RouterLink
          v-for="tab in tabs"
          :key="tab.to"
          :to="tab.to"
          :class="['owner-sidebar-link', 'owner-nav-pill', { active: route.path === tab.to }]"
        >
          {{ tab.label }}
        </RouterLink>
      </nav>
      <div class="owner-sidebar-status">
        <a-tag color="arcoblue">用户端</a-tag>
        <a-tag color="green">当前 {{ activeTab.label }}</a-tag>
        <a-tag color="gold">{{ currentUser?.role ?? "OWNER" }}</a-tag>
        <p class="muted">{{ pageMeta.sideNote }}</p>
        <a-button size="small" status="normal" @click="logout">退出登录</a-button>
      </div>
    </aside>

    <div class="owner-content">
      <header class="shell-banner owner-page-header">
        <div class="shell-banner-copy owner-page-copy">
          <p class="eyebrow">用户端</p>
          <h1>{{ pageMeta.title }}</h1>
          <p>{{ pageMeta.summary }}</p>
        </div>
        <div class="owner-page-side">
          <a-tag color="arcoblue">当前页面：{{ activeTab.label }}</a-tag>
          <a-tag color="green">{{ pageMeta.status }}</a-tag>
        </div>
      </header>

      <main class="experience-main">
        <RouterView />
      </main>
    </div>

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
