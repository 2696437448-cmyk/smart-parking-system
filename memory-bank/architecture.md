# 架构说明（Step24 目标口径）

## 1. 服务边界

1. `gateway-service`：Spring Cloud Gateway + Resilience4j，负责统一路由、trace 透传、超时熔断、降级兜底与前端跨域放行。
2. `parking-service`：Java 主业务服务，负责预约一致性、推荐、共享计费、账单查询、收益统计、导航目标生成与调度触发。
3. `model-service`：Python 算法服务，负责预测、优化、模型激活与版本管理。
4. `realtime-service`：WebSocket 实时推送与实时指标伴生服务。
5. `frontend-app`：Vue3 + TypeScript + Pinia + Vue Router，交付业主端与物业端业务页面。

## 2. 主数据流

1. 传感器与事件数据 -> Step11 ETL -> `forecast_feature_table`、`dispatch_input_table`。
2. Step19A 验收要求：ETL 严格运行 Spark 主链，`engine=spark` 才能过门。
3. 业主预约请求 -> Gateway -> `parking-service` 一致性链路（Redis 幂等 / Redisson 锁 / MySQL 唯一约束）。
4. `parking-service` 基于计费规则生成预估金额，并为订单写入 `billing_records` 初始记录。
5. 订单完成 -> `parking-service` 按冻结计费语义更新最终账单并确认收益。
6. `parking-service` 聚合 `billing_records` -> 物业日收益 / 区域收益接口。
7. 业务服务调用模型服务 -> 预测供需缺口 / Hungarian 优化结果。
8. 调度事件入 MQ -> 消费重试 -> DLQ。
9. 前端业务页面默认走 Gateway HTTP API；实时状态优先 WebSocket，异常时自动切轮询。

## 3. 可靠性链路

1. Redis 幂等校验（`Idempotency-Key` + TTL）。
2. Redisson 细粒度分布式锁（`slot_id + time_window`）。
3. MySQL 唯一约束兜底写入一致性。
4. Gateway 侧超时 + 熔断 + fallback（固定 `fallback_reason/fallback_strategy/trace_id`）。
5. MQ 重试与 DLQ。
6. 前端连接链路降级（WebSocket -> Polling）。
7. 结算链路幂等：同一订单重复完成不得重复确认收益。

## 4. 业务视图与技术视图分层

1. 业主端视图：推荐车位、预约结果、预估金额、账单详情、导航页。
2. 物业端业务视图：资源监控、调度结果摘要、日收益、区域收益。
3. 技术视图：Prometheus + Grafana 三视图（正常态/故障态/恢复态）。
4. 业务页面不得默认跳到 RabbitMQ/Grafana；监控地址仅作诊断补充。

## 5. 地理与导航链路

1. 引入静态 `geo_catalog` 概念，按 `region_id/slot_id` 维护 `lat/lng/display_name`。
2. `DispatchRequest.location` 旧字段保持兼容；坐标能力通过内部映射和新只读响应类型补充。
3. 导航默认采用“地图跳转 + ETA”模式，不引入复杂实时地图 SDK。

## 6. 当前态与目标态

### 6.1 当前态（Step18 基线）

1. 拓扑已形成“3 核心服务 + 1 实时伴生服务 + 1 前端工程化应用”。
2. Step0~Step18 已作为工程化基线通过验收。
3. 关键运行参数：
   - `UPSTREAM_CONNECT_TIMEOUT_MS=10000`
   - `UPSTREAM_TIMEOUT_MS=2500`
   - Grafana 对外端口 `13000:3000`

### 6.2 目标态（Step24）

1. Spark 严格主链通过。
2. 调度优化为确定性真实 Hungarian。
3. 共享计费、账单、收益汇总闭环完成。
4. 业主端 / 物业端多页面业务前端完成。
5. 默认演示入口与 README / runbook / 脚本统一到业务页面。
6. Step24 成为新的默认全量验收入口；Step18 仅保留为历史证据。

## 7. 关键冻结决策

1. `connect=10000ms/read=2500ms` 作为稳定性优先参数冻结，后续只允许基于压测报告调整。
2. 四服务不是架构偏移，定义为“核心 3 + 伴生 1”的阶段化设计。
3. API 合同与核心字段冻结，后续只能做向后兼容扩展。
4. 计费默认语义冻结：`Asia/Shanghai`、`15 分钟一个计费块`、`不足一个计费块向上取整`、`离场 / 订单完成后确认收益`。
5. 统计粒度冻结：`daily + region summary`。
