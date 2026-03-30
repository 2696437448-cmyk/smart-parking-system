import { buildTraceHeaders, runtimeConfig } from "./runtime";

function toQueryValue(value: string | number | boolean | undefined | null) {
  if (value === undefined || value === null) {
    return "";
  }
  return String(value);
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

export async function requestJson<T>(scope: string, url: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: buildTraceHeaders(scope, options.headers ?? {}),
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error ?? `http_${response.status}`);
  }
  return payload as T;
}
