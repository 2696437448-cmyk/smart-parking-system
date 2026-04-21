<script setup lang="ts">
import { IconDashboard, IconLiveBroadcast, IconSafe } from "@arco-design/web-vue/es/icon";
import { computed } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";

const route = useRoute();

const pageMeta = computed(() => {
  if (route.path === "/admin/monitor") {
    return {
      eyebrow: "Operations Command",
      title: "业务监控与经营分析",
      summary: "把运营摘要、趋势图表、运行模式和降级解释收束到更像成熟后台的产品页面里。",
      snapshot: "实时链路优先，轮询兜底",
    };
  }

  return {
    eyebrow: "Operations Command",
    title: "停车运营平台",
    summary: "统一的运营壳层已经就绪。",
    snapshot: "基础运行模式",
  };
});
</script>

<template>
  <div class="experience-shell admin-shell">
    <aside class="admin-sidebar-shell admin-control-rail">
      <div class="admin-sidebar-brand">
        <div class="shell-status-strip">
          <a-tag color="cyan">Operations Grid</a-tag>
          <a-tag color="arcoblue">Realtime Aware</a-tag>
        </div>
        <div class="shell-banner-copy">
          <p class="eyebrow">Admin Command Rail</p>
          <h1>停车运营驾驶舱</h1>
          <p class="muted">收益、状态、图表和降级解释被收束到一套可连续观察的运营界面中。</p>
        </div>
      </div>
      <div class="chip-row">
        <span class="pill"><IconDashboard /> Dashboard</span>
        <span class="pill"><IconLiveBroadcast /> Live State</span>
        <span class="pill"><IconSafe /> Stable Runtime</span>
      </div>
      <nav class="admin-nav admin-sidebar-nav" aria-label="admin navigation">
        <RouterLink to="/admin/monitor">
          <span>经营驾驶舱</span>
          <small>Dashboard</small>
        </RouterLink>
      </nav>
      <div class="detail-list compact-detail admin-sidebar-notes">
        <p><strong>默认模式</strong> 实时事件流 + 轮询回退</p>
        <p><strong>目标能力</strong> 让管理者快速判断收益、占用率和系统状态</p>
      </div>
      <div class="admin-sidebar-footer">
        <span class="pill ghost">中控式布局</span>
        <span class="pill">图表按需加载</span>
      </div>
    </aside>

    <div class="admin-main">
      <header class="shell-banner admin-banner admin-page-header">
        <div class="shell-banner-copy admin-page-header-copy">
          <p class="eyebrow">{{ pageMeta.eyebrow }}</p>
          <h2>{{ pageMeta.title }}</h2>
          <p>{{ pageMeta.summary }}</p>
        </div>
        <div class="admin-page-header-side">
          <div class="shell-status-strip">
            <a-tag color="gold">Operations View</a-tag>
            <a-tag color="cyan">Business Charts</a-tag>
          </div>
          <p class="muted admin-page-header-note">{{ pageMeta.snapshot }}</p>
        </div>
      </header>

      <main class="experience-main">
        <RouterView />
      </main>
    </div>
  </div>
</template>
