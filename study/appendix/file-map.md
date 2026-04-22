# 项目文件地图

这份地图只列当前学习最值得优先阅读的文件，不追求全量枚举。  
原则是：`先主线，后扩展；先入口，后细节。`

## frontend

目录：`apps/frontend/src`

- `main.ts`
  Vue 应用入口。
- `router.ts`
  页面路由入口。
- `pages/OwnerDashboard.vue`
  业主首页与推荐入口。
- `pages/OwnerOrders.vue`
  订单状态与结算页。
- `pages/OwnerNavigation.vue`
  导航页。
- `pages/AdminMonitor.vue`
  物业监管总览页。
- `composables/useOwnerDashboardView.ts`
  业主页面的主要逻辑入口。
- `composables/useAdminDashboardView.ts`
  物业页的主要逻辑入口。
- `services/http.ts`
  统一请求层。
- `stores/realtime.ts`
  实时状态存储。

## gateway

目录：`services/gateway-service/src/main/java/com/smartparking/gateway`

- `GatewayServiceApplication.java`
  Spring Boot 入口。
- `GatewayRoutesConfig.java`
  路由转发规则。
- `TraceIdGlobalFilter.java`
  Trace 透传。
- `ModelFallbackController.java`
  模型服务 fallback。

## parking-service

目录：`services/parking-service/src/main/java/com/smartparking/parking`

- `ParkingServiceApplication.java`
  核心业务入口，包含预约主链相关类。
- `ParkingBusinessExtensions.java`
  计费、订单、导航、经营汇总等业务扩展。
- `ParkingDashboardViewController.java`
  dashboard 接口入口。
- `ParkingDashboardViewModules.java`
  Query / Assembler / ViewService 分层。
- `ParkingEnhancementController.java`
  原始数据接入、趋势分析、地理信息辅助。

## model-service

文件：`services/model_service.py`

- `_forecast()`
  做供需预测。
- `_optimize()`
  做车位分配优化。
- `_hungarian_assign()`
  Hungarian 分配核心实现。
- `_switch_model()`
  模型激活 / 回滚。

## realtime-service

文件：`services/realtime_service.py`

- `Handler.do_GET()`
  处理健康检查、metrics 和 WebSocket 连接。
- `_ws_accept()`
  WebSocket 握手相关逻辑。
- `_ws_text_frame()`
  文本帧构造。

## scripts

- `scripts/defense_demo.sh`
  启动、验收和演示的统一入口。
- `scripts/step11_etl.py`
  ETL 管道。
- `scripts/step12_train_models.py`
  训练轻量模型。
- `scripts/step13_sync_model_registry.py`
  同步模型注册表。
- `scripts/test_step40_release_acceptance.py`
  默认 Step40 验收。

## docs / reports / memory-bank

- `README.md`
  项目总入口。
- `docs/defense_demo_runbook.md`
  演示和答辩运行手册。
- `reports/step40_technical_acceptance.md`
  当前完成态验收报告。
- `reports/thesis_evidence_package.md`
  论文证据包。
- `memory-bank/architecture.md`
  架构描述。

## 历史保留文件提醒

- `services/parking_service.py`
  旧的 Python 业务服务版本，不是当前默认主线。
- `services/stub_server.py`
  早期阶段的简单测试服务，不是学习主入口。
