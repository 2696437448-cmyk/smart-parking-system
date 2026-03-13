# Step 14 执行报告（业务后端对齐：Java + MySQL/Redis/Redisson）

## 执行范围

1. 目标：将 `parking-service` 从 Python 迁移到 Java Spring Boot，并对齐一致性主链路。
2. 输入：Step 4 预约语义、Step 7 MQ 语义、Step 8 轮询接口语义。
3. 不包含：Step 15 网关治理升级、Step 16 前端工程化。

## 已实现产物

1. Java 服务工程：`services/parking-service`
   - `pom.xml`
   - `src/main/resources/application.yml`
   - `src/main/java/com/smartparking/parking/ParkingServiceApplication.java`

2. 运行编排调整：`infra/docker-compose.yml`
   - parking-service 切换为 Maven + Spring Boot 容器。
   - 注入 MySQL/Redis/RabbitMQ 连接参数。
   - 增加 `m2-cache` 卷，减少重复依赖下载。

3. Step14 闸门脚本：`scripts/test_step14_java_consistency.py`
   - 验证一致性组件链路：`redis + redisson + mysql`。
   - 并发抢占同车位同时间窗：仅 1 个成功，其余冲突/锁超时。
   - 幂等重放命中同 reservation_id，并可在 Redis 调试端点追踪 TTL。
   - 通过 debug 接口验证 DB 唯一约束最终只保留 1 条有效记录。

4. 仓库治理补充：`.gitignore`
   - 排除 `services/parking-service/target/` 与常见本地缓存。

## 一致性主链路落地说明

1. Redis 幂等：
   - `Idempotency-Key` 作为键，存储 payload_hash + 状态码 + 响应体。
   - TTL 由 `IDEMPOTENCY_TTL_SECONDS` 控制（默认 7200s）。

2. Redisson 分布式锁：
   - 锁键：`lock:slot:{slot_id}:window:{window_start}|{window_end}`。
   - 参数：`wait=100ms`、`lease=3s`（可配置）。

3. MySQL 唯一约束兜底：
   - 唯一键：`(slot_id, window_start, window_end, status_active)`。
   - 即使高并发锁竞争异常，数据库仍能阻断重复写入。

## 执行命令与结果

1. Step14 专项闸门：

```bash
cd /Users/yanchen/VscodeProject/smart-parking-thesis
python3 scripts/test_step14_java_consistency.py
```

结果：`STEP14_GATE_PASS`

2. 原 Step4 回归：

```bash
python3 scripts/test_step4_consistency.py
```

结果：`STEP4_GATE_PASS`

3. 原 Step7 回归（含队列初始化与 worker）：

```bash
python3 scripts/setup_rabbitmq.py --api http://localhost:15672/api --user guest --password guest
python3 services/dispatch_worker.py --api http://localhost:15672/api --user guest --password guest --max-retry 2 --max-cycles 240
python3 scripts/test_step7_mq_reliability.py --rabbit-api http://localhost:15672/api --user guest --password guest --gateway http://localhost:8080
```

结果：`STEP7_GATE_PASS`

4. 原 Step8 fallback 回归：

```bash
python3 scripts/test_step8_realtime_channel.py --mode fallback --ws-host localhost --ws-port 8090 --ws-path /ws/status --poll-url http://localhost:8080/api/v1/admin/realtime/status
```

结果：`STEP8_GATE_PASS`

5. OpenAPI 合同回归：

```bash
python3 scripts/validate_openapi.py --spec openapi/smart-parking.yaml
```

结果：`openapi_validation_passed`

## 阻塞与修复

1. 阻塞：Java 发布 RabbitMQ 管理 API 初版出现 `vhost_not_found` 与 `EOF` 问题。
2. 修复：
   - 明确使用 `/api/exchanges/%2F/dispatch.events/publish` 路径。
   - 切换为 Java `HttpClient` 发布并增加容错重试。
   - 对响应空体与非标准返回做兼容处理。
3. 结果：Step7 回归恢复通过，`accepted=true`，DLQ 流转恢复正常。

## 验收映射

1. 对齐 `implementation-plan.md` Step14：
   - Java `parking-service` 已落地。
   - 一致性主链路已对齐为 Redis + Redisson + MySQL。
2. 对齐 `acceptance.md` 定稿条目（阶段性）：
   - “业务后端对齐”“一致性主链路对齐”已具备可复现实证。
