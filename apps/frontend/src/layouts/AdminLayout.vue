<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <div class="experience-shell admin-shell">
    <aside class="admin-rail">
      <p class="eyebrow">Admin Experience</p>
      <h1>物业经营驾驶舱</h1>
      <p class="muted">
        实时状态、收益趋势、区域经营对比和预测解释统一进入业务视图，技术诊断入口保持为备用。
      </p>
      <div class="chip-row">
        <span class="pill">ECharts</span>
        <span class="pill">Pinia</span>
        <span class="pill">WebSocket / Polling</span>
      </div>
      <nav class="admin-nav" aria-label="admin navigation">
        <RouterLink to="/admin/monitor">经营驾驶舱</RouterLink>
      </nav>
    </aside>

    <div class="admin-main">
      <header class="shell-banner admin-banner">
        <p class="eyebrow">Operations</p>
        <div class="shell-banner-row">
          <div class="shell-banner-copy">
            <h2>业务监控与经营分析</h2>
            <p>以聚合视图接口驱动页面，让前端聚焦展示层，让管理端更适合日常观察与答辩演示。</p>
          </div>
          <div class="chip-row">
            <span class="pill">Business Charts</span>
            <span class="pill">Realtime Aware</span>
            <span class="pill">View-Model API</span>
          </div>
        </div>
      </header>

      <main class="experience-main">
        <RouterView />
      </main>
    </div>
  </div>
</template>
