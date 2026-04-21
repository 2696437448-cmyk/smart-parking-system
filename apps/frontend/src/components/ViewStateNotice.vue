<script setup lang="ts">
import { computed } from "vue";
import type { ViewStateTone } from "../composables/useViewState";

const props = defineProps<{
  tone: ViewStateTone;
  title: string;
  message: string;
  detail?: string;
  badge?: string;
}>();

const toneLabel = computed(() => {
  switch (props.tone) {
    case "loading":
      return "系统同步中";
    case "empty":
      return "暂无业务数据";
    case "error":
      return "状态异常";
    case "degraded":
      return "已进入降级链路";
    case "stale":
      return "数据待刷新";
    default:
      return "状态稳定";
  }
});
</script>

<template>
  <article class="state-notice" :data-tone="tone">
    <div class="state-notice-head">
      <p class="eyebrow">View State</p>
      <a-tag color="cyan">{{ badge ?? toneLabel }}</a-tag>
    </div>
    <a-alert :title="title" show-icon>
      {{ message }}
    </a-alert>
    <p v-if="detail" class="muted state-detail">{{ detail }}</p>
  </article>
</template>
