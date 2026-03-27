import { createRouter, createWebHistory } from "vue-router";
import OwnerDashboard from "./pages/OwnerDashboard.vue";
import OwnerOrders from "./pages/OwnerOrders.vue";
import OwnerNavigation from "./pages/OwnerNavigation.vue";
import AdminMonitor from "./pages/AdminMonitor.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/owner/dashboard" },
    { path: "/owner/dashboard", component: OwnerDashboard },
    { path: "/owner/orders", component: OwnerOrders },
    { path: "/owner/navigation", component: OwnerNavigation },
    { path: "/admin/monitor", component: AdminMonitor },
  ],
});

export default router;
