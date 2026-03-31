import { computed, ref, watch } from "vue";
import { formatRequestError } from "../services/http";
import { completeOrder, fetchOrderDetail } from "../services/owner";
import type { OrderDetail } from "../types/dashboard";
import { useOrderContext } from "./useOrderContext";
import { useViewState } from "./useViewState";

export function useOwnerOrderView() {
  const orderContext = useOrderContext();
  const state = useViewState(60_000);
  const orderDetail = ref<OrderDetail | null>(null);
  const busy = ref(false);

  async function loadOrder() {
    if (!orderContext.orderId.value) {
      orderDetail.value = null;
      state.markEmpty("暂无订单上下文", "请先在推荐页创建预约，再查看账单与结算详情。");
      return;
    }

    busy.value = true;
    state.markLoading("正在加载订单", "正在同步当前订单、账单规则与结算状态。");
    try {
      const payload = await fetchOrderDetail(orderContext.orderId.value);
      orderDetail.value = payload;
      orderContext.rememberOrderId(orderContext.orderId.value);
      await orderContext.ensureRouteOrderId("/owner/orders");
      state.markReady({
        title: payload.billing_status === "CONFIRMED" ? "订单已结算" : "订单已同步",
        message:
          payload.billing_status === "CONFIRMED"
            ? "最终账单已经确认，可继续查看导航和费用明细。"
            : "订单当前仍处于预估账单阶段，可在停车完成后再次结算。",
        detail: `trace ${payload.trace_id} / ${payload.service}`,
        staleMessage: "当前订单信息可能已过时，请刷新订单以同步最新账单状态。",
      });
    } catch (error) {
      orderDetail.value = null;
      state.markError("订单查询失败", formatRequestError(error), "请检查订单号是否仍有效，或回到推荐页重新恢复订单上下文。");
    } finally {
      busy.value = false;
    }
  }

  async function finishOrder() {
    if (!orderContext.orderId.value || !orderDetail.value) {
      return;
    }
    busy.value = true;
    state.markLoading("正在完成结算", "正在提交结束时间并确认最终账单。");
    try {
      await completeOrder(orderContext.orderId.value, orderDetail.value.ended_at);
      await loadOrder();
    } catch (error) {
      state.markError("结算失败", formatRequestError(error), "账单主链语义未变，请稍后重试或检查当前订单状态。");
      busy.value = false;
    }
  }

  async function openNavigation() {
    await orderContext.navigateWithOrder("/owner/navigation", orderContext.orderId.value);
  }

  const orderStatusNote = computed(() => {
    if (!orderDetail.value) {
      return "暂无订单，请先完成预约。";
    }
    if (orderDetail.value.billing_status === "CONFIRMED") {
      return "订单已结算，可继续查看导航和费用明细。";
    }
    return "订单已创建，完成停车后可确认最终账单。";
  });

  watch(
    () => orderContext.orderId.value,
    () => {
      void loadOrder();
    },
    { immediate: true },
  );

  return {
    orderId: orderContext.orderId,
    orderDetail,
    busy,
    state: state.snapshot,
    orderStatusNote,
    loadOrder,
    finishOrder,
    openNavigation,
  };
}
