# Step 6 执行报告（跨服务容错）

## 执行范围

1. 目标：验证 `model-service` 不可用时，Java 网关降级行为。
2. 输入：Step 5 模型接口与冻结合同。
3. 不包含：Step 7 MQ 可靠性与 Step 8 实时通道。

## 已实现产物

1. `services/gateway-service/GatewayMain.java`
   - 为以下路径增加降级响应：
     - `POST /internal/v1/model/predict`
     - `POST /internal/v1/dispatch/optimize`
     - `POST /internal/v1/model/activate`
   - 降级响应统一包含：
     - `fallback_reason=model_service_unavailable`
     - `fallback_strategy=default_rule`
     - `trace_id`

2. `scripts/test_step6_resilience.py`
   - 模型服务故障注入闸门脚本。

## 运行闸门

1. 启动环境：
```bash
cd /Users/yanchen/VscodeProject/smart-parking-thesis
docker compose -f infra/docker-compose.yml up -d gateway-service parking-service model-service
```

2. 注入故障：
```bash
docker compose -f infra/docker-compose.yml stop model-service
```

3. 执行闸门：
```bash
/Users/yanchen/PycharmProjects/quant-value-regression/.venv/bin/python scripts/test_step6_resilience.py
```

4. 结果：
- 闸门输出：`STEP6_GATE_PASS`
- 降级响应保留 trace 透传。

5. 收尾：
```bash
docker compose -f infra/docker-compose.yml down
```

## 阻塞与修复

1. 阻塞：沙箱环境下 Docker socket 访问受限。
2. 修复：使用已批准的提权命令执行闸门。

## 验收映射

1. 验收项 2.2 满足：
   - 模型服务故障时返回“降级可用”而非硬 5xx。
2. 降级字段语义可直接用于前端提示。
