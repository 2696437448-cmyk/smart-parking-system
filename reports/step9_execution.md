# Step 9 执行报告（可观测性基线）

## 执行范围

1. 目标：完成指标与看板基线，并验证故障状态指标迁移。
2. 输入：Step 8 实时拓扑与 memory-bank Step 9 定义。
3. 不包含：分布式追踪后端与生产级告警路由。

## 已实现产物

1. 服务 metrics 与结构化日志：
   - `services/parking_service.py`
     - 增加 `/metrics`
     - 增加携带 `trace_id` 的 JSON 结构化日志
   - `services/model_service.py`
     - 增加 `/metrics`
     - 增加携带 `trace_id` 的 JSON 结构化日志
   - `services/realtime_service.py`
     - 增加 `/metrics`
     - 增加 websocket 运行指标（`messages_total`, `active_connections`）

2. 监控配置：
   - `infra/prometheus/prometheus.yml`
   - `infra/grafana/provisioning/datasources/datasource.yml`
   - `infra/grafana/provisioning/dashboards/dashboards.yml`
   - `infra/grafana/dashboards/step9-observability.json`

3. Compose 集成：
   - `infra/docker-compose.yml`
     - 启用 Prometheus 挂载与端口（`9090`）
     - 启用 Grafana 挂载与端口（`13000:3000`）
     - 增加监控服务依赖

4. Step 9 闸门脚本：
   - `scripts/test_step9_observability.py`
     - `baseline`：校验各目标 `up=1`
     - `fault`：停 model-service 后校验状态迁移

## 运行闸门

### A. Step 9 改动后的回归安全检查

```bash
/Users/yanchen/PycharmProjects/quant-value-regression/.venv/bin/python scripts/test_step4_consistency.py
/Users/yanchen/PycharmProjects/quant-value-regression/.venv/bin/python scripts/test_step5_model_core.py
/Users/yanchen/PycharmProjects/quant-value-regression/.venv/bin/python scripts/test_step8_realtime_channel.py --mode realtime
/Users/yanchen/PycharmProjects/quant-value-regression/.venv/bin/python scripts/test_step8_realtime_channel.py --mode fallback
```

结果：
- `STEP4_GATE_PASS`
- `STEP5_GATE_PASS`
- `STEP8_WEBSOCKET_OK`
- `STEP8_GATE_PASS`

### B. Step 9 可观测性闸门

1. 启动：
```bash
docker compose -f infra/docker-compose.yml up -d gateway-service parking-service model-service realtime-service prometheus grafana
```

2. baseline 校验：
```bash
/Users/yanchen/PycharmProjects/quant-value-regression/.venv/bin/python scripts/test_step9_observability.py --mode baseline
```

3. 故障注入：
```bash
docker compose -f infra/docker-compose.yml stop model-service
```

4. fault 校验：
```bash
/Users/yanchen/PycharmProjects/quant-value-regression/.venv/bin/python scripts/test_step9_observability.py --mode fault
```

结果：
- `STEP9_BASELINE_OK`
- `STEP9_GATE_PASS`

5. 收尾：
```bash
docker compose -f infra/docker-compose.yml down
```

## 阻塞与修复

1. 阻塞：Grafana 主机端口 `3000` 被占用。
   - 修复：映射改为 `13000:3000`。

2. 阻塞：引入可观测性后，Step4 并发场景偶发网关上游超时。
   - 修复：将网关超时参数化并按计划对齐（`UPSTREAM_TIMEOUT_MS=2500`）。

## 验收映射

1. 验收项 2.4 仍然成立（Step 8 降级能力未回退）。
2. 验收项 3.3 增强：
   - 服务日志具备结构化 `trace_id` 关联能力。
3. Step 9 目标满足：
   - 指标与看板产物齐备；
   - 故障注入可触发并观测到预期状态迁移。
