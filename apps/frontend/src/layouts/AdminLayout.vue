<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, RouterView, useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const currentUser = computed(() => auth.currentUser);

const pageMeta = computed(() => {
  if (route.path === "/admin/monitor") {
    return {
      title: "物业监管",
      summary: "一屏查看主要指标、趋势和运行状态。",
      snapshot: "实时优先，异常时自动回退",
    };
  }

  return {
    title: "物业监管",
    summary: "统一查看停车场运行情况。",
    snapshot: "基础运行模式",
  };
});

async function logout() {
  await auth.logout();
  await router.replace("/login");
}
</script>

<template>
  <div class="experience-shell admin-shell admin-simple-shell">
    <div class="admin-main">
      <header class="shell-banner admin-header">
        <div class="shell-banner-copy admin-header-copy">
          <p class="eyebrow">物业端</p>
          <h1>{{ pageMeta.title }}</h1>
          <p>{{ pageMeta.summary }}</p>
        </div>
        <div class="admin-header-side">
          <div class="shell-status-strip">
            <a-tag color="arcoblue">实时</a-tag>
            <a-tag color="green">已连接</a-tag>
            <a-tag color="gold">{{ currentUser?.display_name ?? "未登录用户" }}</a-tag>
          </div>
          <p class="muted admin-header-note">{{ pageMeta.snapshot }}</p>
          <nav class="admin-nav" aria-label="admin navigation">
            <RouterLink to="/admin/monitor">物业监管</RouterLink>
          </nav>
          <a-button size="small" status="normal" @click="logout">退出登录</a-button>
        </div>
      </header>

      <main class="experience-main">
        <RouterView />
      </main>
    </div>
  </div>
</template>
