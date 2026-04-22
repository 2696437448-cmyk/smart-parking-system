<script setup lang="ts">
defineProps<{
  items: Array<{ label: string; value: string }>;
}>();
</script>

<template>
  <div class="key-value-list">
    <div v-for="item in items" :key="`${item.label}-${item.value}`" class="key-value-row">
      <span class="key-label">{{ item.label }}</span>
      <strong class="key-value">{{ item.value }}</strong>
    </div>
  </div>
</template>
