# Step38 执行报告（dashboard 合同与体验收敛）

## 执行范围

1. 目标：让 owner/admin dashboard 的 OpenAPI 契约、前端页面级 view-model 与统一页面状态表达收敛到同一口径。
2. 范围：
   - `openapi/smart-parking.yaml` dashboard 合同补齐
   - owner/admin 页面级数据编排层
   - 统一 `loading / error / empty / degraded / stale` 视图状态表达
   - 历史前端 gate 适配新结构
3. 不包含：
   - 修改 Spark / LSTM / Hungarian 语义
   - 改动 dashboard URL 或删除旧接口

## 实际改动

1. OpenAPI 合同
   - 新增 `/api/v1/owner/dashboard`
   - 新增 `/api/v1/admin/dashboard`
   - 增加 `OwnerDashboardResponse`、`AdminDashboardResponse` 及关联 schema

2. 前端页面级编排层
   - 新增 `apps/frontend/src/composables/useOwnerDashboardView.ts`
   - 新增 `apps/frontend/src/composables/useOwnerOrderView.ts`
   - 新增 `apps/frontend/src/composables/useOwnerNavigationView.ts`
   - 新增 `apps/frontend/src/composables/useAdminDashboardView.ts`
   - 新增 `apps/frontend/src/composables/useOrderContext.ts`
   - 新增 `apps/frontend/src/composables/useViewState.ts`
   - 新增 `apps/frontend/src/components/ViewStateNotice.vue`

3. 页面与类型
   - 更新 `apps/frontend/src/pages/OwnerDashboard.vue`
   - 更新 `apps/frontend/src/pages/OwnerOrders.vue`
   - 更新 `apps/frontend/src/pages/OwnerNavigation.vue`
   - 更新 `apps/frontend/src/pages/AdminMonitor.vue`
   - 更新 `apps/frontend/src/types/dashboard.ts`

4. 验收脚本
   - 更新 `scripts/test_step21_frontend_pages.py`
   - 更新 `scripts/test_step29_admin_charts.py`
   - 更新 `scripts/test_step33_ci_smoke.py`
   - 新增 `scripts/test_step38_dashboard_contract_and_viewmodels.py`

## 核心结果

1. dashboard 合同已不再只是隐式前后端约定，而是进入 OpenAPI 主规范。
2. 页面组件只负责展示和触发动作，数据获取、错误恢复、上下文恢复转移到 view-model / composable 层。
3. `ViewStateNotice` 与 `useViewState` 统一了页面状态表达，避免 owner/admin 各自实现分支。
4. `useOrderContext` 让推荐 -> 订单 -> 导航的订单恢复策略保持一致。

## 执行命令与结果

```bash
python3 scripts/validate_openapi.py --spec openapi/smart-parking.yaml
python3 scripts/test_step38_dashboard_contract_and_viewmodels.py
```

结果：通过。
