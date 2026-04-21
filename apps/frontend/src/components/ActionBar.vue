<script setup lang="ts">
defineProps<{
  align?: "start" | "between";
}>();
</script>

<template>
  <div class="action-bar" :data-align="align ?? 'start'">
    <slot />
  </div>
</template>
