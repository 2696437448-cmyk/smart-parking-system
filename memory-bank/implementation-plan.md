# 实施计划（执行单元）

默认单步粒度为 0.5~1 天，每步必须包含测试与回滚策略。

## 规划护栏

1. 算法核心或跨服务集成步骤，统一预留 1.5 倍缓冲。
2. 每步编码前必须明确“可能卡点”。
3. 未完成 Step 0 数据基线，禁止进入后续开发。
4. 已通过闸门不可回退；每步完成后必须做回归抽查。
5. Git 闸门强制执行：`branch created`、`commit exists`、`PR merged`、`tag created`。
6. Step18 定义为“工程化基线完成态”，Step24 定义为“原始题目主链闭环的历史稳定基线”，Step30 定义为“当前默认完成态”。
7. 后续开发只允许在 Step30 基线之上增强，不允许退化 Step30 已通过能力。

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
4. 当前默认稳定入口：Step30。
5. 当前继续开发入口：Post-Step30 增强迭代。

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
