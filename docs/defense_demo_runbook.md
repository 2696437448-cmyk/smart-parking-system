# 答辩演示手册（Step30 默认完成态）

## 1. 当前演示基线

1. 当前默认演示基线为 `Step30`。
2. 含义：主链业务闭环、近真实数据接入、App 壳层、地图导航增强、物业端图表化与增强验收均已通过。
3. `Step24` 保留为历史主链基线，可在需要时单独回放，但不再作为默认展示口径。

## 2. 目标与时长

1. 目标：在 10~15 分钟内完成“业务页面 + 数据接入 + 技术链路 + 增强验收”的完整演示。
2. 节奏：
   - 启动环境并打开业务页面
   - 展示业主端预约 / 账单 / 导航 / App 壳层
   - 展示物业端监控 / 收益趋势 / 区域对比 / 预测图表
   - 说明 Step26 raw ingest 与 Spark 关联分析
   - 运行默认 Step30 验收收口

## 3. 演示前检查

1. Docker Desktop 已运行。
2. Python 可执行路径可用。
3. Node 与 npm 可用。
4. 端口可用：`8080`, `8081`, `8000`, `8090`, `4173`, `15672`, `9090`, `13000`, `13306`。

## 4. 一键命令

1. 启动环境并拉起前端业务入口
```bash
./scripts/defense_demo.sh start
```

2. 跑基线与业务闭环检查
```bash
./scripts/defense_demo.sh baseline
```

3. 跑故障注入
```bash
./scripts/defense_demo.sh faults
```

4. 运行默认 Step30 增强验收
```bash
./scripts/defense_demo.sh acceptance
```

5. 如需回放 Step24 主链基线
```bash
./scripts/defense_demo.sh acceptance-step24
```

6. 停止清理
```bash
./scripts/defense_demo.sh stop
```

## 5. 默认展示地址

1. 业主端：`http://localhost:4173/owner/dashboard`
2. 物业端：`http://localhost:4173/admin/monitor`
3. 诊断地址（仅备用）：
   - Gateway health：`http://localhost:8080/actuator/health`
   - RabbitMQ：`http://localhost:15672`
   - Grafana：`http://localhost:13000`

## 6. 推荐演示顺序

1. 业主端业务链路
   - 查看推荐车位
   - 创建预约
   - 查看预估金额
   - 完成订单并展示最终账单
   - 打开导航页并展示页面内地图预览

2. 物业端业务链路
   - 查看资源监控摘要
   - 查看日收益趋势与区域收益对比
   - 查看占用率趋势与预测值 vs 实际值图表
   - 展示实时状态与降级标签

3. 数据接入与分析链路
   - 说明 `sensor_event_raw / lpr_event_raw / resident_trip_raw`
   - 展示 Step26 产出的占用热度、车流摘要、出行高峰摘要
   - 强调严格验收时 ETL 仍以 `engine=spark` 通过

4. 技术故障链路
   - Step6：停 `model-service`，展示降级响应。
   - Step7：强制失败调度事件进入重试 / DLQ。
   - Step8：停 `realtime-service`，展示页面自动切换轮询。
   - Step9 / Step17：切到 Grafana 展示正常态 / 故障态 / 恢复态。

5. 验收收口
   - 运行 `./scripts/defense_demo.sh acceptance`
   - 强调默认完成态已从 Step24 升级为 Step30
