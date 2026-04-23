import type { NavigationView, OrderDetail, OwnerDashboardView } from "../types/dashboard";
import { gatewayUrl, requestJson } from "./http";

export const ORDER_STORAGE_KEY = "smartParkingCurrentOrderId";

export interface OwnerDashboardParams {
  location: string;
  preferredWindow: string;
  orderId?: string;
}

export interface ReservationPayload {
  location: string;
  preferredWindow: string;
  slotId: string;
}

export function getStoredOrderId() {
  return localStorage.getItem(ORDER_STORAGE_KEY) ?? "";
}

export function setStoredOrderId(orderId: string) {
  if (orderId) {
    localStorage.setItem(ORDER_STORAGE_KEY, orderId);
  }
}

export async function fetchOwnerDashboard(params: OwnerDashboardParams) {
  return requestJson<OwnerDashboardView>(
    "owner-dashboard",
    gatewayUrl("/api/v1/owner/dashboard", {
      location: params.location,
      preferred_window: params.preferredWindow,
      order_id: params.orderId ?? "",
    }),
  );
}

export async function reserveOwnerSlot(payload: ReservationPayload) {
  return requestJson<Record<string, unknown>>("owner-reservation", gatewayUrl("/api/v1/owner/reservations"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Idempotency-Key": `reserve-${payload.slotId}-${payload.preferredWindow}`,
    },
    body: JSON.stringify({
      preferred_window: payload.preferredWindow,
      location: payload.location,
      slot_id: payload.slotId,
    }),
  });
}

export async function fetchOrderDetail(orderId: string) {
  return requestJson<OrderDetail>("owner-order", gatewayUrl(`/api/v1/owner/orders/${orderId}`));
}

export async function completeOrder(orderId: string, endedAt: string) {
  return requestJson<Record<string, unknown>>("owner-complete", gatewayUrl(`/api/v1/owner/orders/${orderId}/complete`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Idempotency-Key": `complete-${orderId}`,
    },
    body: JSON.stringify({ ended_at: endedAt }),
  });
}

export async function fetchNavigation(orderId: string) {
  return requestJson<NavigationView>("owner-navigation", gatewayUrl(`/api/v1/owner/navigation/${orderId}`));
}
