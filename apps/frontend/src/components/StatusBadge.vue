<script setup lang="ts">
defineProps<{
  label: string;
  tone?: "default" | "accent" | "calm" | "warn";
}>();
</script>

<template>
  <span class="status-badge" :data-tone="tone ?? 'default'">{{ label }}</span>
</template>
