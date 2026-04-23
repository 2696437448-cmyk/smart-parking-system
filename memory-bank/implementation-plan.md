# 实施计划（执行单元）

默认单步粒度为 0.5~1 天，每步必须包含测试与回滚策略。

## 规划护栏

1. 算法核心或跨服务集成步骤，统一预留 1.5 倍缓冲。
2. 每步编码前必须明确“可能卡点”。
3. 已通过闸门不可回退；每步完成后必须做回归抽查。
4. Git 闸门强制执行：`branch created`、`commit exists`、`PR merged`、`tag created`。
5. Step18 定义为工程化基线完成态，Step24 定义为原始题目主链历史稳定基线，Step30 定义为功能增强基线，Step36 定义为发布化稳定锚点，Step40 定义为“当前默认完成态”。
6. 后续开发只允许在 Step40 基线之上增强，不允许退化 Step40 已通过能力。
7. 已经并入主线的后续增强，应直接写进 Step40 之后的主线计划，不再继续按 worktree 临时状态描述。

## 全步骤通用 Git 闸门（强制）

1. 每步必须在独立分支执行：`feat/stepNN-*`。
2. 每步至少 2 次提交（代码 + 证据文档）。
3. 每步必须通过 PR 合并到 `main`。
4. 每步必须打 `stepNN-pass` 标签。
5. 任一 Git 闸门未过，本步视为失败，禁止进入下一步。

## 已完成阶段说明

1. Step0~Step18：工程化基线阶段，已作为历史证据保留。
2. Step19A~24：原始题目需求补完阶段，已完成 Spark strict、确定性 Hungarian、共享计费、业务前端、演示入口与主链全量验收。
3. Step25~30：增强阶段，已完成近真实数据接入、App 壳层、地图导航增强、物业图表与增强验收收口。
4. Step31~36：发布化增强阶段，已完成环境模板、preflight、CI、release bundle、安全扫描与发布化总验收。
5. Step37：提示词体系与第一轮前后端现代化起点。
6. Step38~40：dashboard 合同/体验收敛、聚合层模块化与综合验收升级阶段。
7. 登录与最终 UI / 学习资料增强已合入 `main`，当前主线已同时具备统一登录、最终 UI 和 `study/` 学习包。
8. 当前默认稳定入口：Step40。
9. 当前继续开发入口：Post-Step40 增强迭代。

## Step 0 - Step 37（历史阶段）

1. Step0~Step10：完成数据健康、仓库骨架、合同冻结、网关基线、一致性主链、模型服务、容错、MQ、实时通道、可观测性与技术验收。
2. Step11：完成多源 ETL，产出 `forecast_feature_table` 与 `dispatch_input_table`。
3. Step12：完成 LSTM + 基线训练与评估对比。
4. Step13：完成模型注册、激活、回滚与热切换。
5. Step14：完成 Java `parking-service` 与 Redis/Redisson/MySQL 一致性主链。
6. Step15：完成 Spring Cloud Gateway + Resilience4j 网关治理。
7. Step16：完成 Vue3 + TypeScript + Pinia 前端工程化。
8. Step17：完成可观测性与性能证据补齐。
9. Step18：完成第一阶段全量验收与论文证据收口。
10. Step19A：完成 Spark strict 与依赖基线收敛。
11. Step19B：完成确定性真实 Hungarian。
12. Step20：完成共享计费与账单主链。
13. Step21：完成业主端 / 物业端页面化交付。
14. Step22：完成收益统计与业务监控收口。
15. Step23：完成演示入口升级。
16. Step24：完成主链默认全量验收。
17. Step25：完成文档与完成态口径收敛。
18. Step26：完成近真实 raw ingest 与 Spark 关联分析增强。
19. Step27：完成 `Vue + Capacitor` App 壳层与移动优先业主端交付。
20. Step28：完成 Leaflet + OpenStreetMap 页面内地图预览导航。
21. Step29：完成物业页 ECharts 图表化展示。
22. Step30：完成增强版验收与答辩材料收口，并升级默认完成态。
23. Step31：完成 Post-Step30 路线冻结。
24. Step32：完成环境模板、preflight 与统一命令入口。
25. Step33：完成 CI 层与最小自动回归。
26. Step34：完成 release bundle 与交付资产目录规范。
27. Step35：完成安全与配置硬化。
28. Step36：完成发布化总验收并升级默认完成态到 Step36。
29. Step37：完成项目专用 prompt library、角色化布局、聚合接口、样式分层与第一轮现代化改造。

## Step37 - 提示词驱动的现代化优化入口（已完成）

- 目标：在 Step36 默认完成态之上建立新的提示词驱动优化入口，并完成第一轮前后端现代化改造。
- 输出：项目专用提示词库、统一 prompt 入口、业主/物业视图聚合接口、前端结构拆分、UI 设计升级、路由级懒加载与 Step37 验收脚本。
- 验证：`python3 scripts/test_step37_prompt_frontend_modernization.py`。
- 证据：`memory-bank/project-prompt-library.md`、`reports/step37_execution.md`。

## Step38 - dashboard 合同与体验收敛（已完成）

- 目标：让 owner/admin dashboard 的 OpenAPI、前端页面级编排层与统一状态表达收敛到同一口径。
- 输出：
  - `openapi/smart-parking.yaml` 收录 `/api/v1/owner/dashboard` 与 `/api/v1/admin/dashboard`
  - `useOwnerDashboardView` / `useOwnerOrderView` / `useOwnerNavigationView` / `useAdminDashboardView`
  - `useOrderContext`、`useViewState`、`ViewStateNotice`
  - Step38 gate 与执行报告
- 验证：`python3 scripts/test_step38_dashboard_contract_and_viewmodels.py`。
- 证据：`reports/step38_execution.md`、`reports/step38_gate_results.json`。

## Step39 - dashboard 聚合层与性能硬化（已完成）

- 目标：在不改 URL 与业务语义的前提下，把 dashboard 聚合逻辑从 controller 中抽离，并完成前端请求/实时通道与包体硬化。
- 输出：
  - `ParkingDashboardViewModules.java`
  - `requestJson` 与 `useRealtimeChannel` 硬化
  - ECharts admin 按需加载与 chunk 拆分
  - Step39 gate 与执行报告
- 验证：`python3 scripts/test_step39_dashboard_hardening.py`。
- 证据：`reports/step39_execution.md`、`reports/step39_gate_results.json`。

## Step40 - 综合验收与默认完成态升级（已完成）

- 目标：串联 Step30 / Step36 / Step37 与 Step38 / Step39 新 gate，完成新的默认完成态升级。
- 输出：
  - `scripts/test_step40_release_acceptance.py`
  - Step40 技术验收报告与 gate result
  - README / runbook / memory-bank 统一升级到 Step40
  - Step40 默认 release bundle
- 验证：`python3 scripts/test_step40_release_acceptance.py`、`python3 scripts/test_step40_release_acceptance.py --static-only`。
- 证据：`reports/step40_technical_acceptance.md`、`reports/step40_gate_results.json`。

## Post-Step40 已并入主线的增强（已完成）

### A. 统一登录与角色入口

- 输出：
  - `apps/frontend/src/pages/LoginPage.vue`
  - `apps/frontend/src/stores/auth.ts`
  - `apps/frontend/src/services/auth.ts`
  - `services/gateway-service/src/main/java/com/smartparking/gateway/auth/*`
- 验证：
  - `python3 scripts/test_step43_login_auth.py`
  - `python3 scripts/test_step44_authenticated_owner_identity.py`

### B. 最终 UI 与学习资料收口

- 输出：
  - Owner/Admin 新布局与亮色主题
  - `scripts/test_step41_arco_tech_ui.py`
  - `scripts/test_step42_shadcn_ui_polish.py`
  - `scripts/test_step43_simple_bright_ui.py`
  - `study/` 目录
- 验证：
  - `python3 scripts/test_step41_arco_tech_ui.py`
  - `python3 scripts/test_step42_shadcn_ui_polish.py`
  - `python3 scripts/test_step43_simple_bright_ui.py`
