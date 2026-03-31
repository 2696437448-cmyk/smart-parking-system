import { buildTraceHeaders, runtimeConfig } from "./runtime";

export class HttpRequestError extends Error {
  status: number;
  traceId: string;
  scope: string;
  payload: unknown;

  constructor(scope: string, status: number, message: string, traceId: string, payload: unknown) {
    super(message);
    this.name = "HttpRequestError";
    this.scope = scope;
    this.status = status;
    this.traceId = traceId;
    this.payload = payload;
  }
}

function toQueryValue(value: string | number | boolean | undefined | null) {
  if (value === undefined || value === null) {
    return "";
  }
  return String(value);
}

function mergeHeaders(...sources: HeadersInit[]) {
  const headers = new Headers();
  for (const source of sources) {
    const nextHeaders = new Headers(source);
    nextHeaders.forEach((value, key) => {
      headers.set(key, value);
    });
  }
  return Object.fromEntries(headers.entries());
}

function parsePayload(text: string) {
  const trimmed = text.trim();
  if (!trimmed) {
    return null;
  }
  try {
    return JSON.parse(trimmed) as unknown;
  } catch {
    return trimmed;
  }
}

function payloadMessage(payload: unknown, status: number) {
  if (payload && typeof payload === "object") {
    const message = (payload as Record<string, unknown>).error;
    if (typeof message === "string" && message.trim()) {
      return message.trim();
    }
  }
  if (typeof payload === "string" && payload.trim()) {
    return payload.trim();
  }
  return `http_${status}`;
}

function payloadTraceId(payload: unknown) {
  if (!payload || typeof payload !== "object") {
    return "";
  }
  const traceId = (payload as Record<string, unknown>).trace_id;
  return typeof traceId === "string" ? traceId : "";
}

export function gatewayUrl(path: string, query: Record<string, string | number | boolean | undefined | null> = {}) {
  const url = new URL(path, runtimeConfig.gatewayBaseUrl);
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null || value === "") {
      continue;
    }
    url.searchParams.set(key, toQueryValue(value));
  }
  return url.toString();
}

export function formatRequestError(error: unknown) {
  if (error instanceof HttpRequestError) {
    return error.traceId ? `${error.message} (trace ${error.traceId})` : error.message;
  }
  return String(error);
}

export async function requestJson<T>(scope: string, url: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: buildTraceHeaders(scope, mergeHeaders({ Accept: "application/json" }, options.headers ?? {})),
  });
  const text = await response.text();
  const payload = parsePayload(text);
  const traceId = response.headers.get("X-Trace-Id") ?? payloadTraceId(payload);

  if (!response.ok) {
    throw new HttpRequestError(scope, response.status, payloadMessage(payload, response.status), traceId, payload);
  }
  if (payload === null || typeof payload !== "object") {
    throw new HttpRequestError(scope, response.status, "invalid_json_response", traceId, payload);
  }
  return payload as T;
}
