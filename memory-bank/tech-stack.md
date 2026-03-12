# 技术选型定稿

## 1. 最终技术栈

1. 后端网关/业务：Java 17 + Spring Boot 3 + Spring Cloud Gateway
2. 算法服务：Python 3.11 + FastAPI + PySpark + PyTorch + SciPy
3. 前端：Vue3 + TypeScript + Pinia + ECharts
4. 数据与中间件：MySQL 8、Redis 7、RabbitMQ 3
5. 可观测性：Prometheus + Grafana + 结构化 JSON 日志
6. 部署方式：Docker Compose（单机可复现）

## 2. 选型原因

1. 就业匹配度高：Java 后端 + 分布式可靠性模式。
2. 题目一致性高：Python 生态适合数据处理与模型落地。
3. 复杂度可控：3 核心服务 + 1 实时伴生服务，避免过度微服务拆分。
4. 答辩稳定：单机 Docker 回放风险低。

## 3. 明确取舍

1. 本期不引入 gRPC，降低跨语言联调复杂度。
2. 前端固定 Vue3，不开 React 分支。
3. 不做完整 MLOps 平台，仅做轻量模型版本激活机制。

## 4. 可靠性默认参数

1. 网关上游连接超时：`UPSTREAM_CONNECT_TIMEOUT_MS=10000`
2. 网关上游请求超时：`UPSTREAM_TIMEOUT_MS=2500`
3. 锁等待：`wait=100ms`，锁租约：`lease=3s`
4. 幂等 TTL：2 小时
5. MQ 语义：至少一次 + 消费端幂等 + 重试 + DLQ

## 5. 冻结决策（2026-03-12）

1. 超时参数冻结为 `connect=10000ms`、`read=2500ms`。
   - 决策原因：在 Step 4~Step 10 的集成与回归过程中，较小 `connect` 超时会放大容器启动抖动和网络瞬时波动，导致非业务性失败。
   - 执行原则：优先保证闸门稳定通过与答辩复现稳定性，再基于压测数据微调。

2. 服务拓扑冻结为“3 核心服务 + 1 实时伴生服务”。
   - 核心服务：`gateway-service`、`parking-service`、`model-service`。
   - 伴生服务：`realtime-service`，职责仅为实时推送与通道演示，不承载交易核心写路径。
   - 决策原因：将实时连接管理与核心交易链路解耦，降低故障扩散。

3. 对齐口径：技术定稿目标仍保持 `Java 主业务微服务 + Python 算法服务`，当前实现作为阶段性中间态，不改变最终目标。
