# Step 8 执行报告（实时通道）

## 执行范围

1. 目标：实现 WebSocket 主通道与轮询兜底通道。
2. 输入：Step 7 后端拓扑与 Step 8 验收标准。
3. 不包含：完整 Vue 工程构建链与 Step 9 可观测性看板。

## 已实现产物

1. `services/realtime_service.py`
   - 新增 WebSocket 推送端点：`GET /ws/status`
   - 新增健康检查端点：`GET /actuator/health`
   - 推送载荷字段：`channel`, `mode`, `occupancy_rate`, `updated_at`, `trace_id`

2. `services/parking_service.py`
   - 新增轮询兜底端点：
     - `GET /api/v1/admin/realtime/status`
   - 返回 degraded 模式快照。

3. `scripts/test_step8_realtime_channel.py`
   - realtime 模式：校验 WebSocket 消息。
   - fallback 模式：停 ws 服务后校验轮询响应。

4. `apps/frontend/realtime_dashboard_demo.html`
   - Vue3 演示页面，显示 `realtime/degraded` 状态徽标。
   - WebSocket 异常时自动切轮询。

5. `infra/docker-compose.yml`
   - 增加 `realtime-service` 容器（端口 `8090`）。
   - frontend 依赖新增 `realtime-service`。

## 运行闸门

1. 启动环境：
```bash
cd /Users/yanchen/VscodeProject/smart-parking-thesis
docker compose -f infra/docker-compose.yml up -d gateway-service parking-service model-service realtime-service
```

2. 实时通道校验：
```bash
/Users/yanchen/PycharmProjects/quant-value-regression/.venv/bin/python \
  scripts/test_step8_realtime_channel.py --mode realtime
```

3. 注入故障（停 ws 服务）：
```bash
docker compose -f infra/docker-compose.yml stop realtime-service
```

4. 轮询兜底校验：
```bash
/Users/yanchen/PycharmProjects/quant-value-regression/.venv/bin/python \
  scripts/test_step8_realtime_channel.py --mode fallback
```

5. 结果：
- realtime 输出：`STEP8_WEBSOCKET_OK`
- fallback 输出：`STEP8_GATE_PASS`

6. 收尾：
```bash
docker compose -f infra/docker-compose.yml down
```

## 阻塞与修复

1. 阻塞：容器内 websocket 依赖版本漂移风险。
2. 修复：服务端与闸门客户端均使用标准库协议处理，避免额外依赖。

## 验收映射

1. 验收项 2.4 满足：
   - websocket 不可用时自动切轮询且页面持续更新。
2. 前端可显式展示通道状态，便于答辩演示。
