<script setup lang="ts">
import { computed } from "vue";
import { useRealtimeStore } from "./stores/realtime";
import { useRealtimeChannel } from "./composables/useRealtimeChannel";

const store = useRealtimeStore();
const { reconnect } = useRealtimeChannel();

const statusClass = computed(() => (store.mode === "realtime" ? "status-realtime" : "status-degraded"));
</script>

<template>
  <main class="page">
    <section class="hero-card">
      <p class="eyebrow">Step16 Frontend Engineering</p>
      <h1>物业实时看板</h1>
      <p class="subtitle">主链路 WebSocket，故障自动切换 Polling，状态由 Pinia 统一管理。</p>
      <div class="status-bar" :class="statusClass">
        <span>{{ store.modeLabel }}</span>
        <span>/</span>
        <span>{{ store.sourceLabel }}</span>
      </div>
      <button class="reconnect" type="button" @click="reconnect">手动重连</button>
    </section>

    <section class="grid">
      <article class="metric">
        <p class="label">占用率</p>
        <p class="value">{{ store.occupancyRatePercent }}</p>
      </article>
      <article class="metric">
        <p class="label">活动预约</p>
        <p class="value">{{ store.activeReservations }}</p>
      </article>
      <article class="metric">
        <p class="label">最后更新</p>
        <p class="value">{{ store.updatedAtText }}</p>
      </article>
    </section>

    <section class="diag">
      <h2>通道诊断</h2>
      <p><strong>connected</strong>: {{ store.connected }}</p>
      <p><strong>last_error</strong>: {{ store.lastError || "none" }}</p>
    </section>
  </main>
</template>
