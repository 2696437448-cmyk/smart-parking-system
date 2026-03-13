# 技术定稿差距矩阵（持续追加）

> 目的：统一记录“技术定稿要求 vs 当前实现 vs 证据路径 vs 下一步闸门”，避免后续偏航。

## 1. 架构与服务形态

1. 定稿要求：`Java 主业务微服务 + Python 算法服务`。
2. 当前实现：`gateway-service`（Java）+ `parking-service`（Java）+ `model-service`（Python）+ `realtime-service`（伴生）。
3. 证据路径：
   - `infra/docker-compose.yml`
   - `services/parking-service/src/main/java/com/smartparking/parking/ParkingServiceApplication.java`
   - `reports/step14_execution.md`
4. 差距判定：已对齐（阶段化定义为“3 核心 + 1 伴生”）。
5. 下一步闸门：Step 15（网关治理能力补齐）。

## 2. 一致性主链路

1. 定稿要求：Redis 幂等 + Redisson 锁 + MySQL 唯一约束。
2. 当前实现：写路径已切换为 Redis 幂等 + Redisson 锁 + MySQL 唯一约束。
3. 证据路径：
   - `services/parking-service/src/main/java/com/smartparking/parking/ParkingServiceApplication.java`
   - `scripts/test_step14_java_consistency.py`
   - `reports/step14_execution.md`
4. 差距判定：已对齐。
5. 下一步闸门：Step 18（全量回归验证无退化）。

## 3. 数据工程

1. 定稿要求：PySpark 多源 ETL，产出统一特征表。
2. 当前实现：Step 11 ETL 已落地并生成两张特征表，支持 `external/fallback_raw` 双路径，执行引擎支持 Spark 优先 + Python fallback。
3. 证据路径：
   - `scripts/step11_etl.py`
   - `scripts/test_step11_etl.py`
   - `reports/step11_execution.md`
   - `reports/step11_etl_quality.json`
4. 差距判定：阶段性对齐（当前环境可持续运行；后续可在 Spark 环境补跑同闸门）。
5. 下一步闸门：Step 18（复现实验验收）。

## 4. 模型训练与论文对比

1. 定稿要求：轻量 LSTM 训练 + 至少 1 个传统基线模型对比。
2. 当前实现：已具备可复现训练脚本、模型产物和统一指标对比（MAE/RMSE/MAPE）。
3. 证据路径：
   - `scripts/step12_train_models.py`
   - `scripts/step12_baseline_model.py`
   - `scripts/test_step12_model_training.py`
   - `reports/step12_execution.md`
   - `reports/step12_model_comparison.md`
4. 差距判定：已对齐。
5. 下一步闸门：Step 18（训练与对比复现实验收口）。

## 5. 模型管理（注册与热切换）

1. 定稿要求：模型版本注册表 + 激活接口 + 在线热切换回滚。
2. 当前实现：注册表、激活、回滚、历史查询均已实现并通过闸门。
3. 证据路径：
   - `services/model_service.py`
   - `scripts/step13_sync_model_registry.py`
   - `scripts/test_step13_model_registry.py`
   - `reports/step13_execution.md`
4. 差距判定：已对齐。
5. 下一步闸门：Step 18（跨步骤回归与答辩演示联测）。

## 6. 网关治理

1. 定稿要求：Spring Cloud Gateway + Resilience4j，固化超时/熔断/降级语义。
2. 当前实现：基础网关能力可用，但未完整对齐定稿中的治理组件形态。
3. 证据路径：
   - `services/gateway-service/GatewayMain.java`
   - `reports/step6_execution.md`
4. 差距判定：部分未对齐。
5. 下一步闸门：Step 15。

## 7. 前端工程化

1. 定稿要求：Vue3 + TypeScript + Pinia 工程化前端。
2. 当前实现：单文件 Vue3 演示页（CDN），具备实时/降级演示能力。
3. 证据路径：
   - `apps/frontend/realtime_dashboard_demo.html`
   - `reports/step8_execution.md`
4. 差距判定：部分未对齐。
5. 下一步闸门：Step 16。

## 8. 可观测性与性能证据

1. 定稿要求：Prometheus + Grafana + 结构化日志 + P95/P99 压测对比。
2. 当前实现：可观测性基线已通过，压测对比报告待补齐。
3. 证据路径：
   - `reports/step9_execution.md`
   - `reports/step10_technical_acceptance.md`
4. 差距判定：部分未对齐。
5. 下一步闸门：Step 17。

## 9. 冻结项（禁止回退）

1. API 合同与核心字段冻结：
   - `POST /api/v1/owner/reservations`
   - `POST /api/v1/admin/dispatch/run`
   - `POST /internal/v1/model/predict`
   - `POST /internal/v1/dispatch/optimize`
   - `POST /internal/v1/model/activate`
2. 公共头冻结：`X-Trace-Id`、`Idempotency-Key`。
3. 超时参数冻结：`UPSTREAM_CONNECT_TIMEOUT_MS=10000`、`UPSTREAM_TIMEOUT_MS=2500`（后续仅允许基于压测报告调整）。
4. 已通过闸门冻结：Step 0~14 能力不可退化。
