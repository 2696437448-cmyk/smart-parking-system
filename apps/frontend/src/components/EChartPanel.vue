<script setup lang="ts">
import { BarChart, LineChart } from "echarts/charts";
import { GridComponent, LegendComponent, TitleComponent, TooltipComponent } from "echarts/components";
import { init, use, type EChartsType } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";

use([BarChart, LineChart, GridComponent, LegendComponent, TitleComponent, TooltipComponent, CanvasRenderer]);

const props = defineProps<{
  title: string;
  option: Record<string, unknown>;
  subtitle?: string;
  note?: string;
}>();

const root = ref<HTMLElement | null>(null);
let chart: EChartsType | null = null;

function render() {
  if (!root.value) {
    return;
  }
  if (!chart) {
    chart = init(root.value);
  }
  chart.setOption(props.option, true);
  chart.resize();
}

function handleResize() {
  chart?.resize();
}

onMounted(() => {
  render();
  window.addEventListener("resize", handleResize);
});

watch(
  () => props.option,
  () => {
    render();
  },
  { deep: true },
);

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
  chart?.dispose();
  chart = null;
});
</script>

<template>
  <article class="panel chart-panel">
    <div class="chart-head">
      <div>
        <p class="eyebrow">Business Chart</p>
        <h3>{{ title }}</h3>
      </div>
      <p v-if="subtitle" class="muted chart-subtitle">{{ subtitle }}</p>
    </div>
    <div ref="root" class="chart-canvas"></div>
    <p v-if="note" class="muted chart-note">{{ note }}</p>
  </article>
</template>
