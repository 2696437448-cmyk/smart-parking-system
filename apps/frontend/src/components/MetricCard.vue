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
</script>

<template>
  <article class="metric-card-shell" :data-tone="tone ?? 'default'">
    <p v-if="eyebrow" class="metric-eyebrow eyebrow">{{ eyebrow }}</p>
    <p class="metric-label">{{ label }}</p>
    <a-statistic v-if="isNumericValue" class="metric-statistic" :value="Number(value)" animation />
    <p v-else class="metric-value">{{ value }}</p>
    <p v-if="note" class="metric-note">{{ note }}</p>
  </article>
</template>
