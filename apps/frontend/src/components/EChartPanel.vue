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
  <article class="chart-panel-shell" v-motion-slide-visible-once-bottom>
    <div class="chart-head chart-panel-head">
      <div class="chart-panel-copy">
        <div class="section-header-kicker chart-panel-kicker">
          <p class="eyebrow">Business Chart</p>
          <a-tag color="cyan">Live Chart</a-tag>
        </div>
        <h3>{{ title }}</h3>
        <p v-if="subtitle" class="muted chart-subtitle">{{ subtitle }}</p>
      </div>
      <div class="chart-panel-side">
        <p class="muted chart-microcopy">产品化趋势观察卡</p>
      </div>
    </div>
    <div ref="root" class="chart-canvas"></div>
    <p v-if="note" class="muted chart-note">{{ note }}</p>
  </article>
</template>
