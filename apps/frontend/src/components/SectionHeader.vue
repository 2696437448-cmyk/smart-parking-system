<script setup lang="ts">
import { useSlots } from "vue";

defineProps<{
  eyebrow: string;
  title: string;
  subtitle?: string;
  badge?: string;
  badgeTone?: "default" | "accent";
}>();

const slots = useSlots();
</script>

<template>
  <div class="section-header">
    <div class="section-header-copy">
      <div class="section-header-kicker">
        <p class="eyebrow">{{ eyebrow }}</p>
        <div class="section-header-side">
          <a-tag v-if="badge" :color="badgeTone === 'accent' ? 'cyan' : 'arcoblue'">{{ badge }}</a-tag>
        </div>
      </div>
      <h3>{{ title }}</h3>
      <p v-if="subtitle" class="muted section-subtitle">{{ subtitle }}</p>
    </div>
    <div v-if="slots.actions" class="section-header-actions">
      <slot name="actions" />
    </div>
  </div>
</template>
