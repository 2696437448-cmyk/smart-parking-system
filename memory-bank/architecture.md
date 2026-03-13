# 架构说明

## 1. 服务边界

1. `gateway-service`：Spring Cloud Gateway + Resilience4j，负责统一路由、trace 透传、超时熔断与降级兜底。
2. `parking-service`：Java 主业务服务，负责预约一致性、调度触发、轮询兜底接口。
3. `model-service`：Python 算法服务，负责预测、优化、模型激活与版本管理。
4. `realtime-service`：WebSocket 实时推送与实时指标伴生服务。
5. `frontend-app`：Vue3 + TypeScript + Pinia，看板状态管理与通道切换可视化。

## 2. 主数据流

1. 传感器与事件数据 -> Step 11 ETL -> `forecast_feature_table`、`dispatch_input_table`。
2. ETL 数据源策略：优先 external 子集，缺失时回退 `data/raw` fallback 数据。
3. 业主预约请求 -> Gateway -> 一致性管线（Redis 幂等/Redisson 锁/MySQL 唯一约束）。
4. 业务服务调用模型服务 -> 预测/优化结果。
5. 调度事件入 MQ -> 消费重试 -> DLQ。
6. 前端实时通道优先 WebSocket，异常时自动切轮询。

## 3. 可靠性链路

1. Redis 幂等校验（`Idempotency-Key` + TTL）。
2. Redisson 细粒度分布式锁（`slot_id + time_window`）。
3. MySQL 唯一约束兜底写入一致性。
4. Gateway 侧超时 + 熔断 + fallback（固定 `fallback_reason/fallback_strategy/trace_id`）。
5. MQ 重试与 DLQ。
6. 前端连接链路降级（WebSocket -> Polling）。

## 4. 可观测性链路

1. 服务暴露 `/metrics` 给 Prometheus 抓取。
2. Grafana 读取 Prometheus 展示状态与趋势。
3. 网关与业务日志统一输出 JSON，保留 `trace_id`。

## 5. 当前态与目标态

### 5.1 当前态（Step 16）

1. 拓扑为“3 核心服务 + 1 实时伴生服务 + 1 前端工程化应用”。
2. 已通过闸门：Step 0~16。
3. Step 11~16 关键产物：
   - `data/processed/forecast_feature_table.csv`
   - `data/processed/dispatch_input_table.csv`
   - `artifacts/models/model_registry.json`
   - `services/parking-service/*`
   - `services/gateway-service/*`
   - `apps/frontend/*`
   - `reports/step11_execution.md`
   - `reports/step12_execution.md`
   - `reports/step13_execution.md`
   - `reports/step14_execution.md`
   - `reports/step15_execution.md`
   - `reports/step16_execution.md`
4. 关键运行参数：
   - `UPSTREAM_CONNECT_TIMEOUT_MS=10000`
   - `UPSTREAM_TIMEOUT_MS=2500`
   - Grafana 对外端口 `13000:3000`

### 5.2 目标态（技术定稿完整版）

1. 可观测性与性能证据补齐（Step 17）。
2. 全量验收与论文证据收口（Step 18）。

## 6. 关键冻结决策

1. `connect=10000ms/read=2500ms` 作为稳定性优先参数冻结，后续只允许基于压测报告调整。
2. 四服务不是架构偏移，定义为“核心 3 + 伴生 1”的阶段化设计。
3. API 合同与核心字段冻结，后续只能做向后兼容扩展。

## 7. 里程碑状态

1. Step 0~2：数据健康、骨架与合同冻结完成。
2. Step 3：网关基线通过。
3. Step 4：并发一致性通过。
4. Step 5：模型服务核心通过。
5. Step 6：模型故障降级通过。
6. Step 7：MQ 重试与 DLQ 通过。
7. Step 8：实时通道降级通过。
8. Step 9：可观测性基线通过。
9. Step 10：技术验收全通过（Technical Acceptance Pass）。
10. Step 11：数据工程 ETL 闸门通过。
11. Step 12：模型训练与基线对比闸门通过。
12. Step 13：模型注册与热切换闸门通过。
13. Step 14：Java 业务后端与一致性主链路闸门通过。
14. Step 15：网关治理（Spring Cloud Gateway + Resilience4j）闸门通过。
15. Step 16：前端工程化（Vue3 + TypeScript + Pinia）闸门通过。
16. Step 17~18：定稿对齐收口阶段（待执行）。
