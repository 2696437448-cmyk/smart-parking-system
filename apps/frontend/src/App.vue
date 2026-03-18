<script setup lang="ts">
import { computed } from "vue";
import { useRoute, RouterLink, RouterView } from "vue-router";

const route = useRoute();
const pageTitle = computed(() => {
  if (route.path.startsWith("/admin")) {
    return "物业端资源监控与收益统计";
  }
  if (route.path.startsWith("/owner/navigation")) {
    return "业主端导航引导";
  }
  return "业主端预约与共享计费";
});
</script>

<template>
  <div class="shell">
    <aside class="sidebar">
      <p class="eyebrow">Step24 Delivery</p>
      <h1>Smart Parking</h1>
      <p class="sidebar-copy">
        基于 Pinia、WebSocket、Polling 与手动重连机制构建的多页面业务前端。
      </p>
      <nav class="nav-links">
        <RouterLink to="/owner/dashboard">业主端</RouterLink>
        <RouterLink to="/owner/navigation">导航页</RouterLink>
        <RouterLink to="/admin/monitor">物业端</RouterLink>
      </nav>
    </aside>

    <main class="content">
      <header class="topbar">
        <div>
          <p class="eyebrow">Business UI</p>
          <h2>{{ pageTitle }}</h2>
        </div>
        <div class="badge-group">
          <span class="pill">Vue Router</span>
          <span class="pill">Pinia</span>
          <span class="pill">Realtime + Fallback</span>
        </div>
      </header>
      <RouterView />
    </main>
  </div>
</template>
