# 答辩演示手册（Step24 默认脚本）

## 1. 目标与时长

1. 目标：在 8~12 分钟内稳定完成业务页面 + 技术链路双线演示。
2. 节奏：
   - 启动环境并打开业务页面
   - 展示业主端预约 / 账单 / 导航
   - 展示物业端监控 / 收益统计
   - 演示故障注入与降级
   - 运行 Step24 默认验收收口

## 2. 演示前检查

1. Docker Desktop 已运行。
2. Python 可执行路径可用：
   - `/Users/yanchen/PycharmProjects/quant-value-regression/.venv/bin/python`
3. Node 与 npm 可用。
4. 端口可用：
   - `8080`, `8081`, `8000`, `8090`, `4173`, `15672`, `9090`, `13000`

## 3. 一键命令

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

4. 运行默认 Step24 全量验收
```bash
./scripts/defense_demo.sh acceptance
```

5. 全流程回放
```bash
./scripts/defense_demo.sh full
```

6. 停止清理
```bash
./scripts/defense_demo.sh stop
```

## 4. 默认展示地址

1. 业主端：`http://localhost:4173/owner/dashboard`
2. 物业端：`http://localhost:4173/admin/monitor`
3. 诊断地址（仅备用）：
   - Gateway health：`http://localhost:8080/actuator/health`
   - RabbitMQ：`http://localhost:15672`
   - Grafana：`http://localhost:13000`

## 5. 推荐演示顺序

1. 业主端业务链路
   - 查看推荐车位
   - 创建预约
   - 查看预估金额
   - 完成订单并展示最终账单
   - 打开导航页（ETA + 地图跳转）

2. 物业端业务链路
   - 查看资源监控摘要
   - 查看日收益与区域收益统计
   - 展示实时状态与降级标签

3. 技术故障链路
   - Step6：停 `model-service`，展示降级响应。
   - Step7：强制失败调度事件进入重试 / DLQ。
   - Step8：停 `realtime-service`，展示页面自动切换轮询。
   - Step9 / Step17：切到 Grafana 展示正常态 / 故障态 / 恢复态。

4. 验收收口
   - 运行 `./scripts/defense_demo.sh acceptance`
   - 强调 Step24 已覆盖旧 Step18 基线 + 新增业务闭环

## 6. 讲解话术（简版）

1. 开场
   - “项目先完成工程化基线，再继续补齐原始题目中的共享计费、导航和业务页面。”

2. 业主端
   - “这里展示从推荐、预约到账单和导航的完整业主流程。”

3. 物业端
   - “这里展示的是业务监控与收益统计，不是中间件后台。”

4. 故障演示
   - “技术看板用于说明系统在异常情况下如何自动降级并保持业务可用。”

5. 收口
   - “默认验收入口已经升级为 Step24，Step18 仅保留为历史工程基线证据。”
