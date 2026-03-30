<script setup lang="ts">
defineProps<{
  eyebrow: string;
  title: string;
  subtitle?: string;
  badge?: string;
}>();
</script>

<template>
  <div class="section-header">
    <div class="section-header-copy">
      <p class="eyebrow">{{ eyebrow }}</p>
      <h3>{{ title }}</h3>
      <p v-if="subtitle" class="muted section-subtitle">{{ subtitle }}</p>
    </div>
    <span v-if="badge" class="pill ghost">{{ badge }}</span>
  </div>
</template>
