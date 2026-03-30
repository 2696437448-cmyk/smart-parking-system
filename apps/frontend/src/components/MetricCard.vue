<script setup lang="ts">
defineProps<{
  label: string;
  value: string | number;
  note?: string;
  tone?: "default" | "accent" | "calm";
}>();
</script>

<template>
  <article class="metric-card" :data-tone="tone ?? 'default'">
    <p class="metric-label">{{ label }}</p>
    <p class="metric-value">{{ value }}</p>
    <p v-if="note" class="metric-note">{{ note }}</p>
  </article>
</template>
