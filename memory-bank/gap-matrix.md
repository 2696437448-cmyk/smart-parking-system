# 技术定稿差距矩阵（持续追加）

> 目的：统一记录“技术定稿要求 vs 当前实现 vs 证据路径 vs 下一步闸门”，避免后续偏航。

## 1. 架构与服务形态

1. 定稿要求：`Java 主业务微服务 + Python 算法服务`。
2. 当前实现：Java 网关 + Python 业务/模型 + Python 实时伴生服务。
3. 证据路径：
   - `infra/docker-compose.yml`
   - `services/gateway-service/GatewayMain.java`
   - `services/parking_service.py`
4. 差距判定：部分未对齐。
5. 下一步闸门：Step 14（Java parking-service 对齐）。

## 2. 一致性主链路

1. 定稿要求：Redis 幂等 + Redisson 锁 + MySQL 唯一约束。
2. 当前实现：内存幂等 + 进程锁 + SQLite 唯一约束。
3. 证据路径：`services/parking_service.py`。
4. 差距判定：未对齐。
5. 下一步闸门：Step 14（主链路迁移并并发回归）。

## 3. 模型训练与论文对比

1. 定稿要求：轻量 LSTM 训练 + 至少 1 个传统基线模型对比。
2. 当前实现：LSTM-like 推理逻辑与调度接口，暂无完整训练与对比产物。
3. 证据路径：
   - `services/model_service.py`
   - `reports/step5_execution.md`
4. 差距判定：未对齐。
5. 下一步闸门：Step 12（训练/评估闭环）。

## 4. 数据工程

1. 定稿要求：PySpark 多源 ETL，产出统一特征表。
2. 当前实现：Step 0 fallback 数据与健康检查已完成，ETL 主流程待补齐。
3. 证据路径：
   - `scripts/generate_fallback_data.py`
   - `scripts/data_health_check.py`
4. 差距判定：部分未对齐。
5. 下一步闸门：Step 11（ETL 正式化）。

## 5. 前端工程化

1. 定稿要求：Vue3 + TypeScript + Pinia 工程化前端。
2. 当前实现：单文件 Vue3 演示页（CDN），具备实时/降级演示。
3. 证据路径：`apps/frontend/realtime_dashboard_demo.html`。
4. 差距判定：部分未对齐。
5. 下一步闸门：Step 16（前端项目化）。

## 6. 可观测性与性能

1. 定稿要求：Prometheus + Grafana + 结构化日志 + P95/P99 压测对比。
2. 当前实现：可观测性基线已通过，压测对比报告待补齐。
3. 证据路径：
   - `reports/step9_execution.md`
   - `reports/step10_technical_acceptance.md`
4. 差距判定：部分未对齐。
5. 下一步闸门：Step 17（性能证据补齐）。

## 7. 冻结项（禁止回退）

1. API 合同与核心字段冻结：
   - `POST /api/v1/owner/reservations`
   - `POST /api/v1/admin/dispatch/run`
   - `POST /internal/v1/model/predict`
   - `POST /internal/v1/dispatch/optimize`
   - `POST /internal/v1/model/activate`
2. 公共头冻结：`X-Trace-Id`、`Idempotency-Key`。
3. 超时参数冻结：`UPSTREAM_CONNECT_TIMEOUT_MS=10000`、`UPSTREAM_TIMEOUT_MS=2500`（后续仅允许基于压测报告调整）。
4. 已通过闸门冻结：Step 0~10 能力不可退化。
