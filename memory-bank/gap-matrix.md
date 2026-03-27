# 技术差距矩阵（Step36 默认完成态）

> 目的：统一记录“原始题目主链已完成什么、增强阶段补了什么、默认完成态现在在哪里”。

## 1. 当前稳定基线

1. 当前稳定默认完成态：`Step36`。
2. 含义：在 Step30 功能基线之上，进一步完成环境模板、preflight、CI、release bundle、安全扫描与发布化总验收。
3. 历史基线：
   - `Step30`：功能与增强交付基线
   - `Step24`：原始题目主链基线

## 2. 主链需求对齐状态

### 2.1 架构与服务形态

1. 目标：`Java 主业务 + Python 算法 + Vue3 前端 + Docker Compose 单机可复现`。
2. 当前：已对齐，形成 `gateway-service + parking-service + model-service + realtime-service + frontend-app`。
3. 证据：`infra/docker-compose.yml`、`services/*`、`apps/frontend/*`。
4. 判定：已完成。

### 2.2 一致性主链路

1. 目标：Redis 幂等 + Redisson 锁 + MySQL 唯一约束。
2. 当前：已对齐。
3. 证据：`reports/step14_execution.md`、`scripts/test_step14_java_consistency.py`。
4. 判定：已完成。

### 2.3 数据工程主链

1. 目标：PySpark ETL，产出统一特征表，验收必须走 Spark strict。
2. 当前：已对齐，并在 Step26 增强为 raw ingest + Spark analytics。
3. 证据：`scripts/step11_etl.py`、`scripts/test_step19a_spark_strict.py`、`scripts/test_step26_raw_ingest_analytics.py`、`reports/step26_execution.md`。
4. 判定：已完成。

### 2.4 模型与调度

1. 目标：轻量 LSTM + 确定性 Hungarian。
2. 当前：已完成，并可复现。
3. 证据：`scripts/test_step12_model_training.py`、`scripts/test_step19b_hungarian.py`、`reports/step19b_execution.md`。
4. 判定：已完成。

### 2.5 共享计费与收益统计

1. 目标：预约、预估、结算、账单、收益汇总闭环。
2. 当前：已完成，`billing_records` 是唯一收益数据源。
3. 证据：`services/parking-service/src/main/java/com/smartparking/parking/ParkingBusinessExtensions.java`、`reports/step20_execution.md`、`reports/step22_execution.md`。
4. 判定：已完成。

### 2.6 业主端 / 物业端业务页面

1. 目标：业主端预约/计费/导航，物业端监控/收益统计。
2. 当前：已完成，并在 Step27~29 增强为移动优先、地图化、图表化交付。
3. 证据：`apps/frontend/src/pages/*`、`reports/step21_execution.md`、`reports/step27_execution.md`、`reports/step28_execution.md`、`reports/step29_execution.md`。
4. 判定：已完成。

### 2.7 演示入口与默认完成态

1. 目标：一键启动后落到业务页面，不是 RabbitMQ/Grafana。
2. 当前：已完成，并在 Step30 后升级默认完成态与默认验收入口。
3. 证据：`scripts/defense_demo.sh`、`README.md`、`docs/defense_demo_runbook.md`、`reports/step23_execution.md`、`reports/step30_technical_acceptance.md`。
4. 判定：已完成。

## 3. 增强阶段完成项（Step25~30）

### 3.1 Step25 - 文档与完成态口径收敛

1. 完成：统一了 memory-bank、README、runbook、脚本与执行证据口径。
2. 证据：`reports/step25_execution.md`。

### 3.2 Step26 - 近真实数据接入与 Spark 关联分析

1. 完成：新增 `sensor_event_raw`、`lpr_event_raw`、`resident_trip_raw` 与 Spark 分析摘要输出。
2. 证据：`reports/step26_execution.md`、`reports/step26_spark_quality.json`、`reports/step26_occupancy_heatmap_summary.json`、`reports/step26_vehicle_flow_summary.json`、`reports/step26_resident_peak_summary.json`。

### 3.3 Step27 - App 壳层与移动优先业主端

1. 完成：交付 `Vue + Capacitor` Android 壳层、移动优先布局与底部导航。
2. 证据：`reports/step27_execution.md`、`apps/frontend/android/*`、`scripts/test_step27_app_shell.py`。

### 3.4 Step28 - 地图导航增强

1. 完成：交付 Leaflet + OpenStreetMap 页面内地图预览与兼容导航接口。
2. 证据：`reports/step28_execution.md`、`scripts/test_step28_navigation_map.py`。

### 3.5 Step29 - 物业端图表化展示

1. 完成：交付收益趋势、区域对比、占用率趋势、预测对照图。
2. 证据：`reports/step29_execution.md`、`scripts/test_step29_admin_charts.py`。

### 3.6 Step30 - 增强验收与答辩升级

1. 完成：Step24 原回归和 Step26~29 增强闸门已统一通过。
2. 证据：`reports/step30_gate_results.json`、`reports/step30_technical_acceptance.md`。

## 4. 阶段结论

1. Step24：历史主链基线。
2. Step25~29：已完成的增强阶段实现。
3. Step30：历史功能与增强交付基线。
4. Step36：当前稳定默认完成态。

## 5. Post-Step30 发布化缺口

### 5.1 环境模板与统一入口

1. 目标：根目录级 `.env.example`、preflight、统一命令入口。
2. 当前：已由 Step32 补齐。
3. 证据：`.env.example`、`scripts/preflight_check.sh`、`Makefile`、`reports/step32_execution.md`。
4. 判定：已完成。

### 5.2 CI 与回归自动化

1. 目标：把关键回归从“手工执行”升级为 PR 自动执行。
2. 当前：已新增 `.github/workflows/ci.yml`、`make ci-smoke` 与 Step33 轻量 smoke gate。
3. 证据：`.github/workflows/ci.yml`、`scripts/test_step33_ci_smoke.py`、`reports/step33_execution.md`。
4. 判定：已完成。

### 5.3 发布包与交付物管理

1. 目标：形成 release bundle、答辩交付目录与版本化演示资产。
2. 当前：已新增 `make release-bundle`、`scripts/create_release_bundle.sh` 与 `deliverables/` 目录规范。
3. 证据：`deliverables/README.md`、`reports/step34_execution.md`。
4. 判定：已完成。

### 5.4 安全与配置硬化

1. 目标：减少默认凭证、分散配置和潜在敏感项风险。
2. 当前：已通过 `.env.secure.example`、security scan、配置分层和恢复文档收口。
3. 证据：`reports/step35_execution.md`、`reports/step35_gate_results.json`、`reports/step35_security_scan.json`。
4. 判定：已完成。

### 5.5 发布化总验收

1. 目标：在 Step30 基线之上升级新的默认交付完成态。
2. 当前：已通过 Step36 发布化总验收并升级默认完成态。
3. 证据：`reports/step36_gate_results.json`、`reports/step36_technical_acceptance.md`。
4. 判定：已完成。
