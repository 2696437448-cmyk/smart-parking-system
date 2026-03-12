# 架构说明

## 1. 服务边界

1. `gateway-service`：统一路由、trace 透传、错误封装、降级兜底。
2. `parking-service`：预约一致性、调度触发、轮询兜底接口。
3. `model-service`：预测、优化、模型激活。
4. `realtime-service`：WebSocket 实时推送与实时指标。

## 2. 主数据流

1. 传感器与事件数据 -> ETL -> 特征表。
2. 业主预约请求 -> 一致性管线（幂等/锁/唯一约束）。
3. 业务服务调用模型服务 -> 预测/优化结果。
4. 调度事件入 MQ -> 消费重试 -> DLQ。
5. 看板实时优先 WebSocket，异常时切轮询。

## 3. 可靠性链路

1. 幂等校验。
2. 细粒度锁。
3. 数据库唯一约束。
4. 上游故障降级响应。
5. MQ 重试与 DLQ。

## 4. 可观测性链路

1. 服务暴露 `/metrics` 给 Prometheus 抓取。
2. Grafana 读取 Prometheus 展示状态与趋势。
3. 网关与业务日志统一输出 JSON，保留 `trace_id`。

## 5. 当前态与目标态

### 5.1 当前态（Step 10 已验收）

1. 拓扑为“3 核心服务 + 1 实时伴生服务”。
2. 已通过闸门：Step 0~10（数据基线、合同冻结、一致性、容错、MQ、实时、可观测性、技术总验收）。
3. 关键运行参数：
   - `UPSTREAM_CONNECT_TIMEOUT_MS=10000`
   - `UPSTREAM_TIMEOUT_MS=2500`
   - Grafana 对外端口 `13000:3000`

### 5.2 目标态（技术定稿完整版）

1. `parking-service` 迁移并对齐为 Java 主业务服务（Spring Boot）。
2. 一致性主链路对齐为：Redis 幂等 + Redisson 锁 + MySQL 唯一约束。
3. 模型工程补齐：PySpark ETL、LSTM 训练、基线模型对比、模型注册与热切换。
4. 前端工程化对齐：Vue3 + TypeScript + Pinia。

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
10. Step 11~18：定稿对齐补齐阶段（待执行）。
