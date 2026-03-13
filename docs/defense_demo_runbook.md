# 答辩演示手册（脚本化）

## 1. 目标与时长

1. 目标：在 8~12 分钟内稳定完成技术演示。
2. 节奏：
   - 启动与基线验证
   - 故障注入演示
   - 可观测性切换展示
   - 阶段验收收口

## 2. 演示前检查

1. Docker Desktop 已运行。
2. Python 可执行路径可用：
   - `/Users/yanchen/PycharmProjects/quant-value-regression/.venv/bin/python`
3. 端口可用：
   - `8080`, `8081`, `8000`, `8090`, `15672`, `9090`, `13000`

## 3. 一键命令

1. 启动环境
```bash
./scripts/defense_demo.sh start
```

2. 跑基线
```bash
./scripts/defense_demo.sh baseline
```

3. 跑故障注入
```bash
./scripts/defense_demo.sh faults
```

4. 全流程回放
```bash
./scripts/defense_demo.sh full
```

5. 停止清理
```bash
./scripts/defense_demo.sh stop
```

## 4. 故障注入顺序（推荐）

1. Step 6 模型故障降级
   - 动作：停止 model-service。
   - 预期：接口返回降级字段，不 500。

2. Step 7 MQ 失败重试与 DLQ
   - 动作：触发强制失败调度事件。
   - 预期：重试后进入 DLQ。

3. Step 8 实时通道中断
   - 动作：停止 realtime-service。
   - 预期：自动切换轮询，页面继续更新。

4. Step 9 可观测性状态迁移
   - 动作：先 baseline，再停 model-service。
   - 预期：Prometheus 指标状态迁移正确。

## 5. 讲解话术（简版）

1. 开场
   - "本项目采用合同先行 + 闸门式交付，先保证稳定再追求复杂度。"

2. 基线
   - "先验证合同一致与核心能力（Step4/Step5）。"

3. 故障演示
   - "接下来依次演示降级、DLQ、实时通道兜底。"

4. 可观测性
   - "通过指标和日志展示故障前后状态转移。"

5. 收口
   - "所有技术闸门已在 Step10 验收报告中闭环。"

## 6. 现场展示建议文件

1. `reports/thesis_evidence_package.md`
2. `reports/step10_technical_acceptance.md`
3. `memory-bank/progress.md`
