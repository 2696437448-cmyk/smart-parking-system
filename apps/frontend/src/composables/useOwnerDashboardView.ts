import { computed, onMounted, ref } from "vue";
import { formatRequestError } from "../services/http";
import { fetchOwnerDashboard, reserveOwnerSlot } from "../services/owner";
import type { OwnerDashboardView, RecommendationItem } from "../types/dashboard";
import { useAuthStore } from "../stores/auth";
import { useOrderContext } from "./useOrderContext";
import { useViewState } from "./useViewState";

function pad(value: number) {
  return value.toString().padStart(2, "0");
}

function toLocalInput(date: Date) {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function plusMinutes(base: Date, minutes: number) {
  return new Date(base.getTime() + minutes * 60 * 1000);
}

export function useOwnerDashboardView() {
  const auth = useAuthStore();
  const orderContext = useOrderContext();
  const state = useViewState(45_000);
  const now = new Date();

  const location = ref("R1");
  const windowStart = ref(toLocalInput(now));
  const windowEnd = ref(toLocalInput(plusMinutes(now, 60)));
  const busy = ref(false);
  const dashboard = ref<OwnerDashboardView | null>(null);

  const currentUser = computed(() => auth.currentUser);
  const authenticatedUserId = computed(() => currentUser.value?.user_id ?? "");
  const preferredWindow = computed(() => `${windowStart.value}:00/${windowEnd.value}:00`);
  const recommendations = computed<RecommendationItem[]>(() => dashboard.value?.recommendations ?? []);
  const latestOrder = computed(() => dashboard.value?.latest_order ?? null);
  const activeSummary = computed(() => dashboard.value?.journey.message ?? "正在准备推荐车位。");

  async function loadRecommendations() {
    if (!authenticatedUserId.value) {
      state.markError("登录态缺失", "当前无法识别业主身份。", "请重新登录后再尝试访问预约页。");
      return;
    }
    busy.value = true;
    state.markLoading("正在刷新推荐视图", "正在从 owner dashboard 聚合接口同步推荐、账单规则和最近订单上下文。");
    try {
      const payload = await fetchOwnerDashboard({
        location: location.value,
        preferredWindow: preferredWindow.value,
        orderId: orderContext.orderId.value,
      });
      dashboard.value = payload;
      if (!payload.recommendations.length) {
        state.markEmpty("当前暂无推荐结果", "请调整区域或预约窗口后重试。", `trace ${payload.trace_id} / ${payload.service}`);
      } else if (payload.latest_order) {
        state.markReady({
          title: "推荐与订单上下文已同步",
          message: "推荐车位、计费规则和最近订单已经汇合到同一视图，可直接进入订单页继续流程。",
          detail: `trace ${payload.trace_id} / ${payload.service}`,
          staleMessage: "当前推荐结果可能已经过时，请点击刷新推荐以重新同步最新候选车位。",
          badge: "订单已同步",
        });
      } else {
        state.markReady({
          title: "推荐视图已更新",
          message: "当前预约窗口的候选车位已经刷新，可直接选择车位发起预约。",
          detail: `trace ${payload.trace_id} / ${payload.service}`,
          staleMessage: "推荐视图可能已经过时，请重新刷新以获取当前候选结果。",
          badge: "推荐已更新",
        });
      }
    } catch (error) {
      state.markError(
        "推荐加载失败",
        formatRequestError(error),
        "请检查 gateway、owner dashboard 聚合接口以及预约窗口参数。",
      );
    } finally {
      busy.value = false;
    }
  }

  async function reserveAndOpenOrders(slotId: string) {
    if (!authenticatedUserId.value) {
      state.markError("登录态缺失", "当前无法识别业主身份。", "请重新登录后再尝试提交预约。");
      return;
    }
    busy.value = true;
    state.markLoading("正在提交预约", "一致性主链正在锁定车位并恢复订单上下文。");
    try {
      const payload = await reserveOwnerSlot({
        preferredWindow: preferredWindow.value,
        location: location.value,
        slotId,
      });
      const nextOrderId = String(payload.order_id ?? payload.reservation_id ?? "").trim();
      if (!nextOrderId) {
        state.markError("预约返回缺少订单号", "当前无法自动恢复订单上下文。", "请刷新推荐页后重试。");
        return;
      }
      orderContext.rememberOrderId(nextOrderId);
      await orderContext.navigateWithOrder("/owner/orders", nextOrderId);
    } catch (error) {
      state.markError(
        "预约失败",
        formatRequestError(error),
        "幂等与锁语义保持不变，请调整参数后再次尝试。",
      );
    } finally {
      busy.value = false;
    }
  }

  async function openOrders() {
    await orderContext.navigateWithOrder("/owner/orders", latestOrder.value?.order_id ?? orderContext.orderId.value);
  }

  onMounted(() => {
    void loadRecommendations();
  });

  return {
    authenticatedUserId,
    location,
    windowStart,
    windowEnd,
    busy,
    dashboard,
    state: state.snapshot,
    preferredWindow,
    recommendations,
    latestOrder,
    activeSummary,
    currentUser,
    loadRecommendations,
    reserveAndOpenOrders,
    openOrders,
  };
}
