<script setup lang="ts">
import StatusBadge from "./StatusBadge.vue";

defineProps<{
  eyebrow: string;
  title: string;
  subtitle?: string;
  badge?: string;
  badgeTone?: "default" | "accent" | "calm" | "warn";
}>();
</script>

<template>
  <div class="section-header">
    <div class="section-header-copy">
      <p class="eyebrow">{{ eyebrow }}</p>
      <h3>{{ title }}</h3>
      <p v-if="subtitle" class="muted section-subtitle">{{ subtitle }}</p>
    </div>
    <StatusBadge v-if="badge" :label="badge" :tone="badgeTone ?? 'accent'" />
  </div>
</template>
