import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { AUTH_TOKEN_STORAGE_KEY, getStoredAccessToken } from "../services/http";
import { fetchCurrentUser, loginRequest, logoutRequest, type AuthUser } from "../services/auth";

const AUTH_USER_STORAGE_KEY = "smartParkingCurrentUser";

function readStoredUser() {
  if (typeof window === "undefined") {
    return null;
  }
  const raw = window.localStorage.getItem(AUTH_USER_STORAGE_KEY);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    window.localStorage.removeItem(AUTH_USER_STORAGE_KEY);
    return null;
  }
}

function writeStoredToken(token: string) {
  if (typeof window === "undefined") {
    return;
  }
  if (token) {
    window.localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, token);
    return;
  }
  window.localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
}

function writeStoredUser(user: AuthUser | null) {
  if (typeof window === "undefined") {
    return;
  }
  if (user) {
    window.localStorage.setItem(AUTH_USER_STORAGE_KEY, JSON.stringify(user));
    return;
  }
  window.localStorage.removeItem(AUTH_USER_STORAGE_KEY);
}

export const useAuthStore = defineStore("auth", () => {
  const accessToken = ref(getStoredAccessToken());
  const currentUser = ref<AuthUser | null>(readStoredUser());
  const restoreState = ref<"idle" | "loading" | "ready">("idle");
  const isAuthenticated = computed(() => Boolean(accessToken.value && currentUser.value));
  const defaultLandingPath = computed(() => (currentUser.value?.role === "ADMIN" ? "/admin/monitor" : "/owner/dashboard"));

  let restorePromise: Promise<void> | null = null;

  function syncSession(token: string, user: AuthUser) {
    accessToken.value = token;
    currentUser.value = user;
    writeStoredToken(token);
    writeStoredUser(user);
    restoreState.value = "ready";
  }

  function clearSession() {
    accessToken.value = "";
    currentUser.value = null;
    writeStoredToken("");
    writeStoredUser(null);
    restoreState.value = "idle";
  }

  async function login(username: string, password: string) {
    const payload = await loginRequest({ username, password });
    syncSession(payload.access_token, payload.user);
    return payload;
  }

  async function restoreSession(force = false) {
    if (restorePromise) {
      return restorePromise;
    }
    if (!force && isAuthenticated.value) {
      restoreState.value = "ready";
      return;
    }

    const token = getStoredAccessToken();
    if (!token) {
      clearSession();
      return;
    }

    accessToken.value = token;
    const cachedUser = readStoredUser();
    if (cachedUser) {
      currentUser.value = cachedUser;
    }

    restoreState.value = "loading";
    restorePromise = fetchCurrentUser()
      .then((user) => {
        currentUser.value = user;
        writeStoredUser(user);
        restoreState.value = "ready";
      })
      .catch((error: unknown) => {
        clearSession();
        throw error;
      })
      .finally(() => {
        restorePromise = null;
      });

    return restorePromise;
  }

  async function logout() {
    try {
      if (accessToken.value) {
        await logoutRequest();
      }
    } finally {
      clearSession();
    }
  }

  return {
    accessToken,
    currentUser,
    isAuthenticated,
    restoreState,
    defaultLandingPath,
    login,
    restoreSession,
    logout,
    clearSession,
  };
});
