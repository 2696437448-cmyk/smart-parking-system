<script setup lang="ts">
import { IconDashboard, IconLiveBroadcast, IconSafe } from "@arco-design/web-vue/es/icon";
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <div class="experience-shell admin-shell">
    <aside class="admin-control-rail">
      <div class="shell-status-strip">
        <a-tag color="cyan">Operations Grid</a-tag>
        <a-tag color="arcoblue">Realtime Aware</a-tag>
      </div>
      <div class="shell-banner-copy">
        <p class="eyebrow">Admin Command Rail</p>
        <h1>停车运营驾驶舱</h1>
        <p class="muted">收益、状态、图表和降级解释被收束到一套可连续观察的运营界面中。</p>
      </div>
      <div class="chip-row">
        <span class="pill"><IconDashboard /> Dashboard</span>
        <span class="pill"><IconLiveBroadcast /> Live State</span>
        <span class="pill"><IconSafe /> Stable Runtime</span>
      </div>
      <nav class="admin-nav" aria-label="admin navigation">
        <RouterLink to="/admin/monitor">经营驾驶舱</RouterLink>
      </nav>
    </aside>

    <div class="admin-main">
      <header class="shell-banner admin-banner">
        <div class="shell-status-strip">
          <a-tag color="gold">Operations View</a-tag>
          <a-tag color="cyan">Business Charts</a-tag>
        </div>
        <div class="shell-banner-copy">
          <p class="eyebrow">Operations Command</p>
          <h2>业务监控与经营分析</h2>
          <p>聚合接口、实时状态和解释层共用一套深色中控语言，让管理页看起来像正在运行的系统。</p>
        </div>
      </header>

      <main class="experience-main">
        <RouterView />
      </main>
    </div>
  </div>
</template>
