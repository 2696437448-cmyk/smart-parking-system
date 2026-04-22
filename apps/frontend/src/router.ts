import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "./stores/auth";

const OwnerLayout = () => import("./layouts/OwnerLayout.vue");
const AdminLayout = () => import("./layouts/AdminLayout.vue");
const LoginPage = () => import("./pages/LoginPage.vue");
const OwnerDashboard = () => import("./pages/OwnerDashboard.vue");
const OwnerOrders = () => import("./pages/OwnerOrders.vue");
const OwnerNavigation = () => import("./pages/OwnerNavigation.vue");
const AdminMonitor = () => import("./pages/AdminMonitor.vue");

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/login" },
    { path: "/login", component: LoginPage, meta: { guestOnly: true } },
    {
      path: "/owner",
      component: OwnerLayout,
      meta: { requiresAuth: true, role: "OWNER" },
      children: [
        { path: "", redirect: "/owner/dashboard" },
        { path: "dashboard", component: OwnerDashboard },
        { path: "orders", component: OwnerOrders },
        { path: "navigation", component: OwnerNavigation },
      ],
    },
    {
      path: "/admin",
      component: AdminLayout,
      meta: { requiresAuth: true, role: "ADMIN" },
      children: [
        { path: "", redirect: "/admin/monitor" },
        { path: "monitor", component: AdminMonitor },
      ],
    },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  const requiresAuth = Boolean(to.meta.requiresAuth);
  const guestOnly = Boolean(to.meta.guestOnly);
  const requiredRole = typeof to.meta.role === "string" ? to.meta.role : "";

  if (guestOnly) {
    await auth.restoreSession().catch(() => undefined);
    if (auth.isAuthenticated) {
      return auth.defaultLandingPath;
    }
    return true;
  }

  if (!requiresAuth) {
    return true;
  }

  try {
    await auth.restoreSession();
  } catch {
    return { path: "/login", query: { redirect: to.fullPath } };
  }

  if (!auth.isAuthenticated) {
    return { path: "/login", query: { redirect: to.fullPath } };
  }

  if (requiredRole && auth.currentUser?.role !== requiredRole) {
    return auth.defaultLandingPath;
  }

  return true;
});

export default router;
