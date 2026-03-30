# 实施计划（执行单元）

默认单步粒度为 0.5~1 天，每步必须包含测试与回滚策略。

## 规划护栏

1. 算法核心或跨服务集成步骤，统一预留 1.5 倍缓冲。
2. 每步编码前必须明确“可能卡点”。
3. 未完成 Step 0 数据基线，禁止进入后续开发。
4. 已通过闸门不可回退；每步完成后必须做回归抽查。
5. Git 闸门强制执行：`branch created`、`commit exists`、`PR merged`、`tag created`。
6. Step18 定义为“工程化基线完成态”，Step24 定义为“原始题目主链闭环的历史稳定基线”，Step30 定义为“功能增强基线”，Step36 定义为“当前默认完成态”。
7. 后续开发只允许在 Step36 基线之上增强，不允许退化 Step36 已通过能力。

## 全步骤通用 Git 闸门（强制）

1. 每步必须在独立分支执行：`feat/stepNN-*`。
2. 每步至少 2 次提交（代码 + 证据文档）。
3. 每步必须通过 PR 合并到 `main`。
4. 每步必须打 `stepNN-pass` 标签。
5. 任一 Git 闸门未过，本步视为失败，禁止进入下一步。

## 已完成阶段说明

1. Step0~Step18：工程化基线阶段，已作为历史证据保留。
2. Step19A~24：原始题目需求补完阶段，已完成 Spark strict、确定性 Hungarian、共享计费、业务前端、演示入口与新的主链全量验收。
3. Step25~30：增强阶段，已完成近真实数据接入、App 壳层、地图导航增强、物业图表与增强验收收口。
4. Step31~36：发布化增强阶段，已完成环境模板、preflight、CI、release bundle、安全扫描与发布化总验收。
5. 当前默认稳定入口：Step36。
6. 当前继续开发入口：Post-Step36 增强迭代。

## Step 0 - Step 24（历史阶段）

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

## Step25 - 文档与完成态口径收敛（已完成）

- 目标：统一 `memory-bank`、README、runbook、脚本与实际执行状态。
- 输出：以 Step24 为历史主链基线、以 Step30 为当前默认完成态的统一文档口径。
- 验证：文档间不再互相冲突。
- 证据：`reports/step25_execution.md`。

## Step26 - 近真实数据接入与 Spark 关联分析增强（已完成）

- 目标：在不新增微服务的前提下，引入近真实 raw 数据接入层，并让 ETL 除特征表外再产出关联分析结果。
- 输出：`sensor_event_raw`、`lpr_event_raw`、`resident_trip_raw` 接入能力；`Step26` 关联分析摘要；支持 MySQL raw -> Spark ETL 主链。
- 验证：raw 数据可写入 MySQL；ETL 可从 raw 表跑到特征表和分析摘要；明文车牌不落库；Spark strict 通过。
- 证据：`reports/step26_execution.md`、`reports/step26_spark_quality.json`。

## Step27 - 业主端跨端 App 壳层与移动端改造（已完成）

- 目标：在现有 Vue 前端基础上交付 `Vue + Capacitor` App 壳层，并将业主端改造为移动优先体验。
- 输出：Capacitor 配置、Android 壳层、移动优先业主端页面、底部导航与 App 风格布局。
- 验证：桌面浏览器与移动视口均可访问；`npm run typecheck`、`npm run build`、Capacitor 壳层检查通过。
- 证据：`reports/step27_execution.md`。

## Step28 - 地图导航增强（已完成）

- 目标：将导航体验从“仅外链跳转”升级为“页面内地图预览 + 外部地图 fallback”。
- 输出：Leaflet + OpenStreetMap 预览、扩展后的 `NavigationTarget`、地图与 ETA 统一展示。
- 验证：导航页可展示地图预览、目的地、ETA、路线摘要与外部地图跳转；旧 `map_url` 仍兼容。
- 证据：`reports/step28_execution.md`。

## Step29 - 物业端图表化展示（已完成）

- 目标：将物业端业务页面从表格/指标卡升级为图表化业务管理页。
- 输出：ECharts 图表页面、收益趋势/区域对比/占用率趋势/预测对照接口与展示。
- 验证：物业页图表可用、数据可回溯、与 Grafana 技术图表边界清晰。
- 证据：`reports/step29_execution.md`。

## Step30 - 增强验收与答辩升级（已完成）

- 目标：在 Step24 基线之上完成 Step26~29 的增强验收与答辩材料升级，并将默认完成态升级到 Step30。
- 输出：Step30 增强验收脚本与报告、升级后的 README/runbook/thesis evidence package。
- 验证：Step24 原回归通过；新增 raw ingest、Spark analytics、Capacitor app shell、地图导航、ECharts 图表全部通过。
- 证据：`reports/step30_gate_results.json`、`reports/step30_technical_acceptance.md`。

## Step31 - Post-Step30 路线收敛（已完成）

- 目标：为 Step30 之后的迭代建立新的阶段目标，避免“主链完成后没有下一步定义”。
- 输出：Step31~36 发布化增强路线、更新后的 memory-bank/README/runbook 口径。
- 验证：Step30 仍作为默认完成态；后续路线与阶段边界写清楚。
- 证据：`reports/step31_execution.md`。

## Step32 - 环境模板与 preflight 基线（已完成）

- 目标：统一根目录环境模板、启动前检查与常用命令入口，减少启动/验收前置问题。
- 输出：`.env.example`、`scripts/preflight_check.sh`、`Makefile`、支持 `preflight` 的 `defense_demo.sh`、可覆盖的 compose 环境变量。
- 验证：`./scripts/preflight_check.sh --static`、`make preflight-static` 通过；严格 `make preflight` 在 Docker daemon 就绪时作为启动前门禁执行。
- 证据：`reports/step32_execution.md`。

## Step33 - CI 与回归自动化（已完成）

- 目标：把当前本地可跑的关键闸门收敛到 CI，形成最小自动回归。
- 输出：GitHub Actions 工作流、前端 typecheck/build、OpenAPI 校验、`make ci-smoke`、Step33 轻量 smoke gate。
- 验证：本地 `make ci-smoke`、OpenAPI 校验、前端 typecheck/build 通过；workflow YAML 与 smoke gate 已落库。
- 证据：`reports/step33_execution.md`、`reports/step33_ci_smoke.json`。

## Step34 - 发布包与演示交付物（已完成）

- 目标：把项目从“源码可跑”提升到“交付包可分发、可复现”。
- 输出：`scripts/create_release_bundle.sh`、`make release-bundle`、`deliverables/` 目录规范、版本化交付包。
- 验证：`make release-bundle` 通过，并生成版本化 tar.gz 交付包。
- 证据：`reports/step34_execution.md`。

## Step35 - 安全与配置硬化（已完成）

- 目标：收敛默认凭证、敏感配置与运行时安全边界。
- 输出：`.env.secure.example`、敏感项扫描脚本、配置分层策略、默认密码/账号风险提示、README/ops 文档中的安全恢复建议。
- 验证：`make security-scan` 通过。
- 证据：`reports/step35_execution.md`、`reports/step35_gate_results.json`、`reports/step35_security_scan.json`。

## Step36 - 发布化总验收（已完成）

- 目标：在 Step30 主链与 Step31~35 发布化增强之上形成新的交付完成态。
- 输出：Step36 发布化验收脚本与报告、新的默认交付 runbook、升级后的默认完成态口径。
- 验证：Step30 历史功能基线继续通过，且 CI / security scan / release bundle / latest bundle 检查通过。
- 证据：`reports/step36_gate_results.json`、`reports/step36_technical_acceptance.md`。

## Step37 - 提示词驱动的现代化优化入口（已完成）

- 目标：在 Step36 默认完成态之上建立新的提示词驱动优化入口，并完成第一轮前后端现代化改造。
- 输出：项目专用提示词库、统一 prompt 入口、业主/物业视图聚合接口、前端结构拆分、UI 设计升级、路由级懒加载与新的 Step37 验收脚本。
- 验证：提示词文档覆盖 6 个方向；前端 `typecheck` / `build` 通过；Step21 / Step27 / Step28 / Step29 相关能力不退化；新视图接口可用且旧接口继续兼容。
- 证据：`memory-bank/project-prompt-library.md`、`reports/step37_execution.md`、`scripts/test_step37_prompt_frontend_modernization.py`。
