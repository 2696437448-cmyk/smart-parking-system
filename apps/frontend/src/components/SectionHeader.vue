<script setup lang="ts">
defineProps<{
  eyebrow: string;
  title: string;
  subtitle?: string;
  badge?: string;
  badgeTone?: "default" | "accent";
}>();
</script>

<template>
  <div class="section-header">
    <div class="section-header-copy">
      <p class="eyebrow">{{ eyebrow }}</p>
      <h3>{{ title }}</h3>
      <p v-if="subtitle" class="muted section-subtitle">{{ subtitle }}</p>
    </div>
    <div class="section-header-side">
      <a-tag v-if="badge" :color="badgeTone === 'accent' ? 'cyan' : 'arcoblue'">{{ badge }}</a-tag>
    </div>
  </div>
</template>
