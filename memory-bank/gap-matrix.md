# 技术差距矩阵（Step40 默认完成态）

> 目的：统一记录“原始题目主链已完成什么、增强阶段补了什么、默认完成态现在在哪里”。

## 1. 当前稳定基线

1. 当前稳定默认完成态：`Step40`。
2. 含义：在 Step36 发布化稳定基线之上，进一步完成 dashboard 合同与体验收敛、聚合层模块化、前端性能硬化与综合验收升级。
3. 历史基线：
   - `Step36`：发布化稳定锚点
   - `Step30`：功能与增强交付基线
   - `Step24`：原始题目主链基线

## 2. 主链需求对齐状态

### 2.1 架构与服务形态

1. 目标：`Java 主业务 + Python 算法 + Vue3 前端 + Docker Compose 单机可复现`。
2. 当前：已对齐，形成 `gateway-service + parking-service + model-service + realtime-service + frontend-app`。
3. 判定：已完成。

### 2.2 一致性主链路

1. 目标：Redis 幂等 + Redisson 锁 + MySQL 唯一约束。
2. 当前：已对齐并持续保持在 Step40 基线中。
3. 判定：已完成。

### 2.3 数据工程主链

1. 目标：PySpark ETL，产出统一特征表，验收必须走 Spark strict。
2. 当前：已对齐，并在 Step26 增强为 raw ingest + Spark analytics。
3. 判定：已完成。

### 2.4 模型与调度

1. 目标：轻量 LSTM + 确定性 Hungarian。
2. 当前：已完成并可复现。
3. 判定：已完成。

### 2.5 共享计费与收益统计

1. 目标：预约、预估、结算、账单、收益汇总闭环。
2. 当前：已完成，`billing_records` 仍是唯一收益数据源。
3. 判定：已完成。

### 2.6 业主端 / 物业端业务页面

1. 目标：业主端预约/计费/导航，物业端监控/收益统计。
2. 当前：已完成，并在 Step27~29 增强为移动优先、地图化、图表化交付，在 Step38/39 继续增强为统一状态表达、view-model 下沉与 admin 按需图表加载。
3. 判定：已完成。

### 2.7 演示入口与默认完成态

1. 目标：一键启动后落到业务页面，而不是 RabbitMQ/Grafana。
2. 当前：已完成，并在 Step40 后升级默认演示与验收入口；当前主线默认从 `/login` 进入业务页。
3. 判定：已完成。

### 2.8 统一登录与最终 UI

1. 目标：统一登录入口、角色识别、最终 UI 结构、学习资料与演示文档全部进入主线。
2. 当前：已完成，`feat/login-auth` 与 `feat/ui-refinement` 对应成果都已经收口到 `main`。
3. 判定：已完成。

## 3. 增强阶段完成项（Step25~30）

1. Step25：文档与完成态口径收敛。
2. Step26：近真实数据接入与 Spark 关联分析。
3. Step27：App 壳层与移动优先业主端。
4. Step28：地图导航增强。
5. Step29：物业端图表化展示。
6. Step30：增强验收与答辩升级。

## 4. 发布化与现代化完成项（Step31~37）

1. Step31：Post-Step30 路线收敛。
2. Step32：环境模板与 preflight 基线。
3. Step33：CI 与回归自动化。
4. Step34：发布包与交付物管理。
5. Step35：安全与配置硬化。
6. Step36：发布化总验收。
7. Step37：提示词驱动现代化入口。

## 5. Post-Step36 优化缺口关闭情况

### 5.1 Step38 - dashboard 合同收敛

1. 目标：补齐 owner/admin dashboard OpenAPI 合同，并让前端页面级数据编排层可复用。
2. 当前：已完成，OpenAPI、`dashboard.ts`、view-model composable 与统一页面状态表达已对齐。
3. 证据：`openapi/smart-parking.yaml`、`scripts/test_step38_dashboard_contract_and_viewmodels.py`、`reports/step38_execution.md`。
4. 判定：已完成。

### 5.2 Step39 - dashboard 聚合层模块化

1. 目标：把 dashboard 组装逻辑从 controller 中抽离，同时完成前端请求、实时与包体硬化。
2. 当前：已完成，`ParkingDashboardViewModules.java` 已落地，`requestJson` 与 `useRealtimeChannel` 已收敛，build warning 已消除。
3. 证据：`services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewModules.java`、`scripts/test_step39_dashboard_hardening.py`、`reports/step39_execution.md`。
4. 判定：已完成。

### 5.3 Step40 - 综合验收与默认完成态升级

1. 目标：串联 Step30 / Step36 / Step37 与 Step38 / Step39 新 gate，升级新的默认完成态。
2. 当前：已完成，Step40 综合验收入口、报告、bundle 与文档口径均已落地。
3. 证据：`scripts/test_step40_release_acceptance.py`、`reports/step40_technical_acceptance.md`、`reports/step40_gate_results.json`。
4. 判定：已完成。

### 5.4 登录与最终 UI 合流

1. 目标：把统一登录、最终亮色 UI、学习资料与更新后的文档说明纳入主线。
2. 当前：已完成，主线已包含登录页、auth store、Owner/Admin 新布局、`study/` 学习包以及更新后的 README / runbook / thesis-docs。
3. 证据：`apps/frontend/src/pages/LoginPage.vue`、`apps/frontend/src/stores/auth.ts`、`study/README.md`、`scripts/test_step41_arco_tech_ui.py`、`scripts/test_step43_login_auth.py`。
4. 判定：已完成。

### 5.7 Step38

1. 状态：完成。
2. 备注：重点解决 dashboard 合同、view-model 与统一状态表达。

### 5.8 Step39

1. 状态：完成。
2. 备注：重点解决 dashboard 聚合层膨胀与 ECharts 包体 warning。

### 5.9 Step40

1. 状态：完成。
2. 备注：重点解决默认完成态升级、综合验收与交付包收口。

### 5.10 登录 / UI / 文档收口

1. 状态：完成。
2. 备注：重点解决统一登录、最终 UI、学习资料和更新后的文档说明全部进入主线。
