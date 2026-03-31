import { computed, ref, watch } from "vue";
import { formatRequestError } from "../services/http";
import { fetchNavigation } from "../services/owner";
import type { NavigationView } from "../types/dashboard";
import { useOrderContext } from "./useOrderContext";
import { useViewState } from "./useViewState";

export function useOwnerNavigationView() {
  const orderContext = useOrderContext();
  const state = useViewState(60_000);
  const navigation = ref<NavigationView | null>(null);

  async function loadNavigation() {
    if (!orderContext.orderId.value) {
      navigation.value = null;
      state.markEmpty("等待订单上下文", "请先创建预约，再进入导航页查看路线与地图预览。");
      return;
    }

    state.markLoading("正在加载导航信息", "正在同步 ETA、路线摘要与页面内地图预览。");
    try {
      const payload = await fetchNavigation(orderContext.orderId.value);
      navigation.value = payload;
      await orderContext.ensureRouteOrderId("/owner/navigation");
      state.markReady({
        title: "导航信息已更新",
        message: "路线摘要、外部地图链接和页面内预览已经同步完成。",
        detail: `trace ${payload.trace_id} / ${payload.service}`,
        staleMessage: "导航信息可能已过时，请刷新订单或重新进入导航页同步最新 ETA。",
      });
    } catch (error) {
      navigation.value = null;
      state.markError("导航信息加载失败", formatRequestError(error), "请检查当前订单是否存在，或回到订单页恢复上下文。");
    }
  }

  const routeSummaryText = computed(() => navigation.value?.route_summary?.summary ?? "请先创建订单，再进入导航页。");
  const destinationTitle = computed(() => String(navigation.value?.slot_display_name ?? navigation.value?.destination?.display_name ?? "目标车位"));

  watch(
    () => orderContext.orderId.value,
    () => {
      void loadNavigation();
    },
    { immediate: true },
  );

  return {
    orderId: orderContext.orderId,
    navigation,
    destinationTitle,
    routeSummaryText,
    state: state.snapshot,
    loadNavigation,
  };
}
