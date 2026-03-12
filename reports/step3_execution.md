# Step 3 执行证据（网关基线）

## 执行范围

- Step 3 目标：实现网关 trace 透传与基础路由映射。
- 状态：通过。

## 已实现产物

- `services/gateway-service/GatewayMain.java`
  - Java 单文件网关运行时。
  - `X-Trace-Id` 注入与透传。
  - 路由映射：
    - `/api/v1/owner/**` -> parking-service
    - `/api/v1/admin/**` -> parking-service
    - `/internal/v1/model/**` -> model-service
    - `/internal/v1/dispatch/**` -> model-service
  - 健康检查：`/actuator/health`
  - 转发头过滤：剔除 hop-by-hop 受限头。

- `services/stub_server.py`
  - 用于转发联调验证的 HTTP 桩服务。

- `infra/docker-compose.yml`
  - 完成 Step 3 所需 gateway/parking/model 连线。

- `scripts/test_step3_gateway.py`
  - 自动化闸门脚本，校验健康检查与路由转发。
  - 头字段校验改为大小写不敏感。

## 校验命令与结果

1. Compose 静态校验：

```bash
docker compose -f infra/docker-compose.yml config
```

结果：通过

2. 运行态闸门：

```bash
docker compose -f infra/docker-compose.yml up -d gateway-service parking-service model-service
python scripts/test_step3_gateway.py
docker compose -f infra/docker-compose.yml down
```

结果：通过（`STEP3_GATE_PASS`）

## 调试记录

1. 初始阻塞：Docker daemon 不可用。
2. 运行问题 1：网关返回 `502`，根因为转发了 `Connection` 受限头。
   - 修复：在网关中过滤 hop-by-hop/受限头。
3. 运行问题 2：测试脚本对 `X-Trace-Id` 头大小写敏感。
   - 修复：改为大小写不敏感匹配。

## 交付物

- `services/gateway-service/GatewayMain.java`
- `services/stub_server.py`
- `infra/docker-compose.yml`
- `scripts/test_step3_gateway.py`
