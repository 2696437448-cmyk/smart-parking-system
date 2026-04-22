import { computed, onBeforeUnmount, ref } from "vue";

export type ViewStateTone = "loading" | "ready" | "empty" | "error" | "degraded" | "stale";

interface ReadyOptions {
  title: string;
  message: string;
  detail?: string;
  staleTitle?: string;
  staleMessage?: string;
  staleDetail?: string;
  badge?: string;
}

export function useViewState(staleAfterMs = 60_000) {
  const tone = ref<ViewStateTone>("loading");
  const title = ref("正在加载页面数据");
  const message = ref("正在同步当前业务视图，请稍候。");
  const detail = ref("");
  const badge = ref("加载中");
  const updatedAt = ref(0);
  let staleTimer: number | null = null;

  function clearStaleTimer() {
    if (staleTimer !== null) {
      window.clearTimeout(staleTimer);
      staleTimer = null;
    }
  }

  function setState(
    nextTone: ViewStateTone,
    nextTitle: string,
    nextMessage: string,
    nextDetail = "",
    nextUpdatedAt = updatedAt.value,
    nextBadge = badge.value,
  ) {
    tone.value = nextTone;
    title.value = nextTitle;
    message.value = nextMessage;
    detail.value = nextDetail;
    updatedAt.value = nextUpdatedAt;
    badge.value = nextBadge;
  }

  function markLoading(nextTitle = "正在加载页面数据", nextMessage = "正在同步当前业务视图，请稍候。", nextDetail = "") {
    clearStaleTimer();
    setState("loading", nextTitle, nextMessage, nextDetail, updatedAt.value, "加载中");
  }

  function markEmpty(nextTitle = "当前暂无数据", nextMessage = "请调整条件或稍后重试。", nextDetail = "") {
    clearStaleTimer();
    setState("empty", nextTitle, nextMessage, nextDetail, Date.now(), "空数据");
  }

  function markError(nextTitle = "页面加载失败", nextMessage = "请求未成功完成。", nextDetail = "") {
    clearStaleTimer();
    setState("error", nextTitle, nextMessage, nextDetail, Date.now(), "错误");
  }

  function markDegraded(nextTitle = "当前已降级", nextMessage = "系统已切换到兼容模式，但主业务链仍可继续使用。", nextDetail = "") {
    clearStaleTimer();
    setState("degraded", nextTitle, nextMessage, nextDetail, Date.now(), "已降级");
  }

  function markReady(options: ReadyOptions) {
    clearStaleTimer();
    const timestamp = Date.now();
    setState("ready", options.title, options.message, options.detail ?? "", timestamp);
    if (staleAfterMs <= 0) {
      return;
    }
    staleTimer = window.setTimeout(() => {
      if (tone.value === "ready") {
        setState(
          "stale",
          options.staleTitle ?? "当前视图可能已过时",
          options.staleMessage ?? options.message,
          options.staleDetail ?? options.detail ?? "",
          timestamp,
          "待刷新",
        );
      }
    }, staleAfterMs);
    badge.value = options.badge ?? "已更新";
  }

  onBeforeUnmount(() => {
    clearStaleTimer();
  });

  return {
    snapshot: computed(() => ({
      tone: tone.value,
      title: title.value,
      message: message.value,
      detail: detail.value,
      badge: badge.value,
      updatedAt: updatedAt.value,
    })),
    markLoading,
    markReady,
    markEmpty,
    markError,
    markDegraded,
  };
}
