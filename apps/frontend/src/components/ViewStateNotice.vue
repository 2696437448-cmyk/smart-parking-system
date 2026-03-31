<script setup lang="ts">
import { computed } from "vue";
import type { ViewStateTone } from "../composables/useViewState";

const props = defineProps<{
  tone: ViewStateTone;
  title: string;
  message: string;
  detail?: string;
}>();

const toneLabel = computed(() => {
  switch (props.tone) {
    case "loading":
      return "加载中";
    case "empty":
      return "空数据";
    case "error":
      return "错误";
    case "degraded":
      return "已降级";
    case "stale":
      return "待刷新";
    default:
      return "已更新";
  }
});
</script>

<template>
  <article class="state-notice" :data-tone="tone">
    <div class="state-notice-head">
      <p class="eyebrow">View State</p>
      <span class="pill ghost">{{ toneLabel }}</span>
    </div>
    <strong>{{ title }}</strong>
    <p>{{ message }}</p>
    <p v-if="detail" class="muted state-detail">{{ detail }}</p>
  </article>
</template>
