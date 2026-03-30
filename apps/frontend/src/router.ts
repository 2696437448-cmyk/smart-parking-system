import { createRouter, createWebHistory } from "vue-router";

const OwnerLayout = () => import("./layouts/OwnerLayout.vue");
const AdminLayout = () => import("./layouts/AdminLayout.vue");
const OwnerDashboard = () => import("./pages/OwnerDashboard.vue");
const OwnerOrders = () => import("./pages/OwnerOrders.vue");
const OwnerNavigation = () => import("./pages/OwnerNavigation.vue");
const AdminMonitor = () => import("./pages/AdminMonitor.vue");

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/owner/dashboard" },
    {
      path: "/owner",
      component: OwnerLayout,
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
      children: [
        { path: "", redirect: "/admin/monitor" },
        { path: "monitor", component: AdminMonitor },
      ],
    },
  ],
});

export default router;
