# Step 15 执行报告（网关治理对齐：Spring Cloud Gateway + Resilience4j）

## 执行范围

1. 目标：将 `gateway-service` 从单文件 Java 代理升级为 Spring Cloud Gateway + Resilience4j，并固化模型服务降级语义。
2. 输入：Step 6 降级契约、Step 14 Java 业务后端、冻结 API 合同。
3. 不包含：Step 16 前端工程化、Step 17 压测证据补齐。

## 已实现产物

1. 网关服务工程化升级（`services/gateway-service`）
   - 新增 `pom.xml`（Spring Boot + Spring Cloud Gateway + Resilience4j）。
   - 新增 `GatewayServiceApplication.java`。
   - 新增 `GatewayRoutesConfig.java`（owner/admin 路由 + model/dispatch 路由 + 熔断 fallback）。
   - 新增 `TraceIdGlobalFilter.java`（全链路 `X-Trace-Id` 注入与回传）。
   - 新增 `ModelFallbackController.java`（`fallback_reason/fallback_strategy/trace_id` 语义固化）。
   - 新增 `application.yml`（connect/read 超时与 circuitbreaker 参数）。
   - 删除旧入口：`GatewayMain.java`。

2. 编排调整（`infra/docker-compose.yml`）
   - `gateway-service` 切换为 Maven 运行 Spring Boot。
   - 复用 `m2-cache`，避免重复依赖下载。
   - 保留 `PARKING_BASE_URL`、`MODEL_BASE_URL`、超时环境变量口径。

3. Step15 闸门脚本
   - 新增 `scripts/test_step15_gateway_governance.py`：
     - 模型服务停机时验证 `/predict` 与 `/optimize` 降级字段。
     - 验证响应头 `X-Trace-Id` 与 payload `trace_id` 一致。
     - 验证 `/actuator/circuitbreakers` 含 `modelServiceCb`。

4. 回归脚本稳健性修复（避免重复执行误判）
   - `scripts/test_step3_gateway.py`：模型路由断言改为按当前合同校验 `records/model_version`。
   - `scripts/test_step4_consistency.py`：固定时间窗改为动态时间窗，避免历史数据碰撞。
   - `scripts/test_step14_java_consistency.py`：固定时间窗改为动态时间窗，避免重复执行冲突。

## 执行命令与结果

1. Compose 语法校验

```bash
cd /Users/yanchen/VscodeProject/smart-parking-thesis
docker compose -f infra/docker-compose.yml config
```

结果：`COMPOSE_OK`

2. 启动关键服务

```bash
docker compose -f infra/docker-compose.yml up -d mysql redis rabbitmq parking-service model-service realtime-service gateway-service
```

结果：容器启动成功

3. Step 6 + Step 15 闸门（模型停机场景）

```bash
docker compose -f infra/docker-compose.yml stop model-service
python3 scripts/test_step6_resilience.py
python3 scripts/test_step15_gateway_governance.py
docker compose -f infra/docker-compose.yml start model-service
```

结果：`STEP6_GATE_PASS`、`STEP15_GATE_PASS`

4. 关键回归

```bash
python3 scripts/test_step3_gateway.py
python3 scripts/test_step4_consistency.py
python3 scripts/test_step14_java_consistency.py
python3 scripts/test_step7_mq_reliability.py --rabbit-api http://localhost:15672/api --user guest --password guest --gateway http://localhost:8080
python3 scripts/test_step8_realtime_channel.py --mode fallback --ws-host localhost --ws-port 8090 --ws-path /ws/status --poll-url http://localhost:8080/api/v1/admin/realtime/status
python3 scripts/validate_openapi.py --spec openapi/smart-parking.yaml
```

结果：`STEP3_GATE_PASS`、`STEP4_GATE_PASS`、`STEP14_GATE_PASS`、`STEP7_GATE_PASS`、`STEP8_GATE_PASS`、`openapi_validation_passed`

## 闸门判定

1. 对齐 `implementation-plan.md` Step 15：
   - 网关治理能力已切换为 Spring Cloud Gateway + Resilience4j。
   - 模型服务停机场景可触发熔断降级，返回固定降级语义。
2. 定稿一致性：
   - `fallback_reason/fallback_strategy/trace_id` 契约保持稳定。
   - `X-Trace-Id` 全链路透传保持可追踪。

## 阻塞与修复

1. 阻塞：回归脚本存在固定时间窗，重复执行时会因历史数据导致误报失败。
2. 修复：将 Step3/4/14 脚本按“合同 + 动态时间窗”重构，保证闸门可重复执行。
3. 剩余风险：尚未补齐 Step17 压测报告与 Step16 前端工程化证据。
