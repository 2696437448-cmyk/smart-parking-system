# Step 5 执行证据（模型服务核心）

## 执行范围

- 目标：实现轻量 LSTM 风格预测与调度优化接口。
- 状态：通过（`STEP5_GATE_PASS`）。

## 已实现产物

- `services/model_service.py`
  - `POST /internal/v1/model/predict`
  - `POST /internal/v1/dispatch/optimize`
  - `POST /internal/v1/model/activate`
  - 轻量 LSTM 风格递推预测逻辑
  - Demo 规模匈牙利风格分配（暴力枚举实现）

- `scripts/test_step5_model_core.py`
  - 模型激活、预测、优化闸门校验
  - 输出字段/形状/范围断言
  - 车位分配唯一性校验

- `infra/docker-compose.yml`
  - model-service 从 `stub_server.py` 切换为 `model_service.py`。

## 校验命令与结果

```bash
docker compose -f infra/docker-compose.yml up -d gateway-service parking-service model-service
python scripts/test_step5_model_core.py
docker compose -f infra/docker-compose.yml down
```

结果：通过（`STEP5_GATE_PASS`）

## 调试记录

1. 首次运行失败：模型服务启动瞬态导致连接 reset。
2. 修复：闸门脚本增加健康检查等待与重试。

## 交付物

- `services/model_service.py`
- `scripts/test_step5_model_core.py`
- `infra/docker-compose.yml`
