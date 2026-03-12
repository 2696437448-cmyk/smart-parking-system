# Step 7 执行报告（MQ 可靠性：重试 + DLQ）

## 执行范围

1. 目标：验证异步调度链路在失败场景下的重试与死信能力。
2. 输入：admin 调度触发接口与 RabbitMQ 拓扑。
3. 不包含：Step 8 实时 UI 与 Step 9 可观测性看板。

## 已实现产物

1. `scripts/setup_rabbitmq.py`
   - 声明持久化交换机/队列/绑定：
     - `dispatch.events` 交换机
     - `dispatch.run` 队列
     - `dispatch.dlq` 队列

2. `services/dispatch_worker.py`
   - 消费 `dispatch.run`
   - 使用 `retry_count` 头进行重试
   - 超过重试阈值后路由到 `dispatch.dlq`

3. `scripts/test_step7_mq_reliability.py`
   - 触发 `force_fail=true` 的调度任务
   - 校验消息进入 DLQ

## 运行闸门

1. 启动环境：
```bash
cd /Users/yanchen/VscodeProject/smart-parking-thesis
docker compose -f infra/docker-compose.yml up -d gateway-service parking-service model-service rabbitmq
```

2. 初始化队列拓扑：
```bash
/Users/yanchen/PycharmProjects/quant-value-regression/.venv/bin/python scripts/setup_rabbitmq.py
```

3. 启动 worker：
```bash
/Users/yanchen/PycharmProjects/quant-value-regression/.venv/bin/python services/dispatch_worker.py \
  --api http://localhost:15672/api \
  --user guest \
  --password guest \
  --max-retry 2 \
  --max-cycles 80
```

4. 执行闸门：
```bash
/Users/yanchen/PycharmProjects/quant-value-regression/.venv/bin/python scripts/test_step7_mq_reliability.py
```

5. 结果：
- 初始化输出：`STEP7_RABBIT_SETUP_OK`
- 闸门输出：`STEP7_GATE_PASS`
- worker 输出：`STEP7_WORKER_RUN_DONE`

6. 收尾：
```bash
docker compose -f infra/docker-compose.yml down
```

## 阻塞与修复

1. 阻塞：生产者与 worker 启动存在异步竞态。
2. 修复：增加短暂等待并限制 worker 循环次数，保证闸门稳定复现。

## 验收映射

1. 验收项 2.3 满足：
   - 消费失败链路可进入 DLQ 且可追踪。
2. 可靠性语义符合“至少一次 + 副作用幂等”。
