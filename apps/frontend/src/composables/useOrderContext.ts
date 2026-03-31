import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getStoredOrderId, setStoredOrderId } from "../services/owner";

function normalizeOrderId(input: unknown) {
  if (typeof input === "string") {
    return input.trim();
  }
  if (Array.isArray(input) && typeof input[0] === "string") {
    return input[0].trim();
  }
  return "";
}

export function useOrderContext() {
  const route = useRoute();
  const router = useRouter();

  const orderId = computed(() => normalizeOrderId(route.query.orderId) || getStoredOrderId().trim());
  const hasRouteOrderId = computed(() => Boolean(normalizeOrderId(route.query.orderId)));

  function rememberOrderId(nextOrderId: string) {
    const normalized = nextOrderId.trim();
    if (normalized) {
      setStoredOrderId(normalized);
    }
    return normalized;
  }

  async function ensureRouteOrderId(path = route.path) {
    const currentOrderId = orderId.value;
    if (!currentOrderId || hasRouteOrderId.value) {
      return;
    }
    await router.replace({
      path,
      query: {
        ...route.query,
        orderId: currentOrderId,
      },
    });
  }

  async function navigateWithOrder(path: string, nextOrderId = orderId.value) {
    const currentOrderId = rememberOrderId(nextOrderId);
    await router.push({
      path,
      query: currentOrderId ? { orderId: currentOrderId } : {},
    });
  }

  return {
    orderId,
    hasRouteOrderId,
    rememberOrderId,
    ensureRouteOrderId,
    navigateWithOrder,
  };
}
