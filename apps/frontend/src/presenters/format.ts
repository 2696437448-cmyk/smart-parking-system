export function formatCurrency(value: number | null | undefined) {
  return `¥${Number(value ?? 0).toFixed(2)}`;
}

export function formatPercent(value: number | null | undefined) {
  return `${Number((value ?? 0) * 100).toFixed(1)}%`;
}

export function formatDatetimeLabel(value: string | null | undefined) {
  return value ? value.replace("T", " ").slice(0, 16) : "暂无";
}

export function formatTraceDetail(traceId: string | null | undefined, service: string | null | undefined) {
  if (!traceId && !service) {
    return "";
  }
  return `trace ${traceId ?? "N/A"} / ${service ?? "unknown"}`;
}
