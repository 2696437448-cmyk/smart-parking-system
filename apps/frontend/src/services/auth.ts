import { gatewayUrl, requestJson } from "./http";

export interface AuthUser {
  user_id: string;
  username: string;
  display_name: string;
  role: "OWNER" | "ADMIN";
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: "Bearer";
  expires_in: number;
  user: AuthUser;
}

export async function loginRequest(payload: LoginPayload) {
  return requestJson<LoginResponse>("auth-login", gatewayUrl("/api/v1/auth/login"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export async function fetchCurrentUser() {
  return requestJson<AuthUser>("auth-me", gatewayUrl("/api/v1/auth/me"));
}

export async function logoutRequest() {
  return requestJson<Record<string, string>>("auth-logout", gatewayUrl("/api/v1/auth/logout"), {
    method: "POST",
  });
}
