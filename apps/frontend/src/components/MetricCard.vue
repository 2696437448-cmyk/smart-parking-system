<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  label: string;
  value: string | number;
  note?: string;
  tone?: "default" | "accent" | "calm";
  eyebrow?: string;
}>();

const isNumericValue = computed(() => typeof props.value === "number");

const toneLabel = computed(() => {
  switch (props.tone) {
    case "accent":
      return "重点";
    case "calm":
      return "平稳";
    default:
      return "跟踪";
  }
});

const toneColor = computed(() => {
  switch (props.tone) {
    case "accent":
      return "cyan";
    case "calm":
      return "green";
    default:
      return "arcoblue";
  }
});
</script>

<template>
  <article class="metric-card-shell" :data-tone="tone ?? 'default'">
    <div class="metric-card-meta">
      <div>
        <p v-if="eyebrow" class="metric-eyebrow eyebrow">{{ eyebrow }}</p>
        <p class="metric-label">{{ label }}</p>
      </div>
      <a-tag size="small" :color="toneColor">{{ toneLabel }}</a-tag>
    </div>
    <a-statistic v-if="isNumericValue" class="metric-statistic" :value="Number(value)" animation />
    <p v-else class="metric-value">{{ value }}</p>
    <p v-if="note" class="metric-note metric-card-trend">{{ note }}</p>
  </article>
</template>
