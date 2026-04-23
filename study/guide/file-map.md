# 按功能链看的文件地图

这份地图不是全量文件列表，而是告诉你：如果你正在学某条链，最值得优先看哪些文件。

## Chain 01：Owner Dashboard 请求链

- `apps/frontend/src/router.ts`
- `apps/frontend/src/pages/OwnerDashboard.vue`
- `apps/frontend/src/composables/useOwnerDashboardView.ts`
- `apps/frontend/src/services/owner.ts`
- `services/gateway-service/src/main/java/com/smartparking/gateway/GatewayRoutesConfig.java`
- `services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewController.java`

## Chain 02：预约 / 订单 / 计费 / 导航闭环

- `apps/frontend/src/pages/OwnerDashboard.vue`
- `apps/frontend/src/pages/OwnerOrders.vue`
- `apps/frontend/src/pages/OwnerNavigation.vue`
- `apps/frontend/src/composables/useOrderContext.ts`
- `apps/frontend/src/composables/useOwnerOrderView.ts`
- `apps/frontend/src/composables/useOwnerNavigationView.ts`
- `services/parking-service/src/main/java/com/smartparking/parking/ParkingServiceApplication.java`
- `services/parking-service/src/main/java/com/smartparking/parking/ParkingBusinessExtensions.java`

## Chain 03：Admin Dashboard 聚合与 Realtime 降级链

- `apps/frontend/src/pages/AdminMonitor.vue`
- `apps/frontend/src/composables/useAdminDashboardView.ts`
- `apps/frontend/src/composables/useRealtimeChannel.ts`
- `apps/frontend/src/stores/realtime.ts`
- `apps/frontend/src/types/dashboard.ts`
- `services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewController.java`
- `services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewModules.java`
- `services/realtime_service.py`

## Chain 04：ETL / 模型 / Registry / 验收链

- `scripts/step11_etl.py`
- `scripts/step12_train_models.py`
- `scripts/step13_sync_model_registry.py`
- `services/model_service.py`
- `artifacts/models/model_registry.json`
- `scripts/test_step40_release_acceptance.py`
- `reports/step40_technical_acceptance.md`

## 只在补充阅读时再看的文件

- `services/parking_service.py`
- `services/stub_server.py`
- 早期 Step 报告
- 与当前主线无关的历史脚本
