# Step 4 执行证据（预约一致性核心）

## 执行范围

- 目标：实现幂等 + 细粒度锁 + DB 唯一约束，防止超卖。
- 状态：通过（`STEP4_GATE_PASS`）。

## 已实现产物

- `services/parking_service.py`
  - 业主预约接口：`POST /api/v1/owner/reservations`
  - 物业调度触发接口：`POST /api/v1/admin/dispatch/run`
  - 测试调试接口：`GET /internal/debug/reservations`
  - 幂等存储与 TTL 清理（`Idempotency-Key`）
  - 细粒度锁键：`lock:slot:{slot_id}:window:{window_start}|{window_end}`
  - SQLite 唯一约束：`UNIQUE(slot_id, window_start, window_end)`

- `scripts/test_step4_consistency.py`
  - 同车位同时间窗并发竞争测试。
  - 幂等重放测试。
  - 通过 debug 接口验证仅一个有效预约。

- `infra/docker-compose.yml`
  - parking-service 从 `stub_server.py` 切换为 `parking_service.py`。

## 校验命令与结果

```bash
docker compose -f infra/docker-compose.yml up -d gateway-service parking-service model-service
python scripts/test_step4_consistency.py
docker compose -f infra/docker-compose.yml down
```

结果：通过（`STEP4_GATE_PASS`）

## 调试记录

1. 首次断言不一致：
   - 脚本原先只接受 `409`，但锁等待超时路径会返回 `429`。
   - 修复：将 `409` 与 `429` 都作为“失败但合理”的非获胜结果。
2. debug 路由问题：
   - `/internal/debug/...` 未经网关暴露。
   - 修复：脚本改为直连 `localhost:8081` 查询 debug 接口。

## 交付物

- `services/parking_service.py`
- `scripts/test_step4_consistency.py`
- `infra/docker-compose.yml`
