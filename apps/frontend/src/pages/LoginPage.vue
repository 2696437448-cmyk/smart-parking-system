<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { formatRequestError, HttpRequestError } from "../services/http";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();

const username = ref("owner_demo");
const password = ref("demo123");
const busy = ref(false);
const errorMessage = ref("");

const redirectPath = computed(() => {
  const redirect = route.query.redirect;
  return typeof redirect === "string" ? redirect : "";
});

function applyDemoAccount(role: "OWNER" | "ADMIN") {
  if (role === "ADMIN") {
    username.value = "admin_demo";
    password.value = "admin123";
    return;
  }
  username.value = "owner_demo";
  password.value = "demo123";
}

function resolveDestination(role: "OWNER" | "ADMIN") {
  if (role === "ADMIN" && redirectPath.value.startsWith("/admin")) {
    return redirectPath.value;
  }
  if (role === "OWNER" && redirectPath.value.startsWith("/owner")) {
    return redirectPath.value;
  }
  return role === "ADMIN" ? "/admin/monitor" : "/owner/dashboard";
}

async function submitLogin() {
  busy.value = true;
  errorMessage.value = "";
  try {
    const payload = await auth.login(username.value.trim(), password.value);
    await router.replace(resolveDestination(payload.user.role));
  } catch (error) {
    if (error instanceof HttpRequestError && error.status === 401) {
      errorMessage.value = "用户名或密码错误，请使用演示账号重新登录。";
    } else {
      errorMessage.value = formatRequestError(error);
    }
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <section class="experience-shell smart-login">
    <div class="smart-login-backdrop" aria-hidden="true"></div>
    <article class="panel smart-login-panel" v-motion-slide-visible-once-bottom>
      <div class="shell-status-strip smart-login-strip">
        <a-tag color="arcoblue">Gateway Auth</a-tag>
        <a-tag color="cyan">Demo Login</a-tag>
        <a-tag color="gold">Smart Parking</a-tag>
      </div>

      <div class="shell-banner-copy smart-login-copy">
        <p class="eyebrow">Unified Entry</p>
        <h1>统一登录入口</h1>
        <p>让业主端和管理端都从同一个入口进入，再根据角色自动跳转到各自页面。</p>
      </div>

      <div class="detail-list compact-detail smart-login-help">
        <p><strong>业主演示</strong> owner_demo / demo123</p>
        <p><strong>管理演示</strong> admin_demo / admin123</p>
      </div>

      <a-alert
        v-if="errorMessage"
        type="error"
        :show-icon="true"
        :closable="true"
        class="smart-login-alert"
        @close="errorMessage = ''"
      >
        {{ errorMessage }}
      </a-alert>

      <a-form layout="vertical" class="smart-login-form" :model="{ username, password }" @submit.prevent="submitLogin">
        <a-form-item label="用户名">
          <a-input v-model="username" placeholder="请输入用户名" allow-clear />
        </a-form-item>
        <a-form-item label="密码">
          <a-input v-model="password" type="password" placeholder="请输入密码" allow-clear />
        </a-form-item>

        <div class="chip-row smart-login-actions">
          <a-button type="primary" long :loading="busy" @click="submitLogin">立即登录</a-button>
          <a-button status="normal" long @click="applyDemoAccount('OWNER')">填充业主演示</a-button>
          <a-button status="normal" long @click="applyDemoAccount('ADMIN')">填充管理演示</a-button>
        </div>
      </a-form>
    </article>
  </section>
</template>

<style scoped>
.smart-login {
  position: relative;
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 32px 20px;
  overflow: hidden;
}

.smart-login-backdrop {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at top left, rgba(55, 215, 255, 0.24), transparent 38%),
    radial-gradient(circle at bottom right, rgba(255, 184, 77, 0.18), transparent 32%),
    linear-gradient(160deg, rgba(6, 17, 26, 0.98), rgba(4, 31, 43, 0.92));
}

.smart-login-panel {
  position: relative;
  z-index: 1;
  width: min(100%, 520px);
  display: grid;
  gap: 20px;
}

.smart-login-strip,
.smart-login-actions {
  justify-content: flex-start;
}

.smart-login-help,
.smart-login-alert,
.smart-login-form {
  position: relative;
  z-index: 1;
}
</style>
