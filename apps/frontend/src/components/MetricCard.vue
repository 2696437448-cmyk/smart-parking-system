<script setup lang="ts">
defineProps<{
  label: string;
  value: string | number;
  note?: string;
  tone?: "default" | "accent" | "calm";
  eyebrow?: string;
}>();
</script>

<template>
  <article class="metric-card" :data-tone="tone ?? 'default'">
    <p v-if="eyebrow" class="metric-eyebrow">{{ eyebrow }}</p>
    <p class="metric-label">{{ label }}</p>
    <p class="metric-value">{{ value }}</p>
    <p v-if="note" class="metric-note">{{ note }}</p>
  </article>
</template>
