# 技术定稿差距矩阵（阶段版）

> 目的：统一记录“技术定稿要求 vs 当前实现 vs 证据路径 vs 验收结论”。

## 1. 架构与服务形态

1. 定稿要求：`Java 主业务微服务 + Python 算法服务`。
2. 当前实现：`gateway-service`（Java/Spring Cloud Gateway）+ `parking-service`（Java）+ `model-service`（Python）+ `realtime-service`（伴生）+ `frontend-app`（Vue3+TS+Pinia）。
3. 证据路径：
   - `infra/docker-compose.yml`
   - `services/gateway-service/src/main/java/com/smartparking/gateway/*`
   - `services/parking-service/src/main/java/com/smartparking/parking/ParkingServiceApplication.java`
   - `apps/frontend/src/*`
4. 差距判定：已对齐。

## 2. 一致性主链路

1. 定稿要求：Redis 幂等 + Redisson 锁 + MySQL 唯一约束。
2. 当前实现：写路径已切换为 Redis 幂等 + Redisson 锁 + MySQL 唯一约束。
3. 证据路径：
   - `scripts/test_step14_java_consistency.py`
   - `reports/step14_execution.md`
4. 差距判定：已对齐。

## 3. 数据工程

1. 定稿要求：PySpark 多源 ETL，产出统一特征表。
2. 当前实现：Step11 ETL 已落地并产出两张特征表，支持 external/fallback 双路径。
3. 证据路径：
   - `scripts/step11_etl.py`
   - `reports/step11_execution.md`
4. 差距判定：已对齐（当前执行路径为 Spark 优先 + Python fallback）。

## 4. 模型训练与论文对比

1. 定稿要求：轻量 LSTM 训练 + 传统基线模型对比。
2. 当前实现：训练脚本、模型产物、统一指标对比（MAE/RMSE/MAPE）完整。
3. 证据路径：
   - `scripts/step12_train_models.py`
   - `scripts/step12_baseline_model.py`
   - `reports/step12_model_comparison.md`
4. 差距判定：已对齐。

## 5. 模型管理（注册与热切换）

1. 定稿要求：模型注册表 + 激活接口 + 在线热切换回滚。
2. 当前实现：注册、激活、回滚、历史查询均已落地。
3. 证据路径：
   - `scripts/test_step13_model_registry.py`
   - `reports/step13_execution.md`
4. 差距判定：已对齐。

## 6. 网关治理

1. 定稿要求：Spring Cloud Gateway + Resilience4j，固化超时/熔断/降级语义。
2. 当前实现：Gateway 路由 + CircuitBreaker + fallback 语义完整。
3. 证据路径：
   - `scripts/test_step15_gateway_governance.py`
   - `reports/step15_execution.md`
4. 差距判定：已对齐。

## 7. 前端工程化

1. 定稿要求：Vue3 + TypeScript + Pinia 工程化前端。
2. 当前实现：项目化前端 + WebSocket 主通道 + Polling 兜底。
3. 证据路径：
   - `apps/frontend/package.json`
   - `scripts/test_step16_frontend_engineering.py`
   - `reports/step16_execution.md`
4. 差距判定：已对齐。

## 8. 可观测性与性能证据

1. 定稿要求：Prometheus + Grafana + 结构化日志 + P95/P99 压测对比。
2. 当前实现：已补齐 gateway 指标抓取、三视图看板、baseline/fault/recovery 指标对比。
3. 证据路径：
   - `infra/prometheus/prometheus.yml`
   - `infra/grafana/dashboards/step17-*.json`
   - `reports/step17_performance_summary.md`
4. 差距判定：已对齐。

## 9. 阶段结论

1. 技术定稿要求与当前实现：`初步对齐`（可持续优化）。
2. 阶段验收依据：`reports/step18_technical_acceptance.md` 与 `reports/step18_gate_results.json`。
3. 当前冻结状态：Step0~Step18 已验收能力不允许退化，后续仅做增强与修复。
