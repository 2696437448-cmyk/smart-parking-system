import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { fetchAdminDashboard } from "../services/admin";
import { formatRequestError } from "../services/http";
import { useRealtimeStore } from "../stores/realtime";
import type { AdminDashboardView } from "../types/dashboard";
import { useRealtimeChannel } from "./useRealtimeChannel";
import { useViewState } from "./useViewState";

function today() {
  return new Date().toISOString().slice(0, 10);
}

export function useAdminDashboardView() {
  const store = useRealtimeStore();
  const { reconnect } = useRealtimeChannel();
  const state = useViewState(20_000);
  const dashboard = ref<AdminDashboardView | null>(null);
  const busy = ref(false);
  let timer: number | null = null;

  const statusClass = computed(() => (store.mode === "realtime" ? "status-realtime" : "status-degraded"));
  const updatedAtText = computed(() => store.updatedAtText);
  const lastErrorText = computed(() => store.lastError || "无");

  function syncSurfaceState() {
    if (!dashboard.value) {
      return;
    }
    if (!dashboard.value.sections.revenue_trend.length) {
      state.markEmpty(
        "当前暂无经营图表数据",
        "请先完成订单结算，或检查收益与预测输出是否已经同步到 dashboard 聚合视图。",
        `trace ${dashboard.value.trace_id} / ${dashboard.value.service}`,
      );
      return;
    }

    const detail = [
      `trace ${dashboard.value.trace_id}`,
      `实时 ${store.modeLabel}`,
      `来源 ${store.sourceLabel}`,
      `更新时间 ${updatedAtText.value}`,
    ];
    if (store.lastError) {
      detail.push(store.lastError);
    }

    if (store.mode === "degraded") {
      state.markDegraded(
        "实时通道已降级",
        "页面仍会通过轮询与聚合接口持续更新，但 WebSocket 当前不可用，可稍后手动重连。",
        detail.join(" / "),
      );
      return;
    }

    state.markReady({
      title: "经营视图已更新",
      message: "经营摘要、趋势图和实时状态标签已经同步完成。",
      detail: detail.join(" / "),
      staleTitle: "经营视图可能已过时",
      staleMessage: "请刷新业务数据或手动重连实时通道，以恢复最新经营视图。",
      staleDetail: detail.join(" / "),
    });
  }

  async function refreshBusinessViews() {
    busy.value = true;
    if (!dashboard.value) {
      state.markLoading("正在刷新经营驾驶舱", "正在聚合收益、占用率、预测对照和实时标签。");
    }
    try {
      dashboard.value = await fetchAdminDashboard({
        date: today(),
        trendDays: 7,
        trendLimit: 12,
      });
      syncSurfaceState();
    } catch (error) {
      state.markError(
        "物业视图刷新失败",
        formatRequestError(error),
        "请检查 admin dashboard 聚合接口、收益图表依赖和实时状态服务。",
      );
    } finally {
      busy.value = false;
    }
  }

  watch(
    [() => store.mode, () => store.source, () => store.updatedAt, () => store.lastError],
    () => {
      syncSurfaceState();
    },
  );

  onMounted(() => {
    void refreshBusinessViews();
    timer = window.setInterval(() => {
      void refreshBusinessViews();
    }, 8000);
  });

  onBeforeUnmount(() => {
    if (timer !== null) {
      window.clearInterval(timer);
    }
  });

  return {
    dashboard,
    busy,
    state: state.snapshot,
    statusClass,
    updatedAtText,
    lastErrorText,
    refreshBusinessViews,
    reconnect,
    store,
  };
}
