# 答辩演示手册（Step40 默认完成态）

## 1. 当前演示基线

1. 当前默认演示基线为 `Step40`。
2. 含义：主链业务闭环、近真实数据接入、App 壳层、地图导航增强、物业端图表化、发布化基线、dashboard 合同收敛、view-model 下沉、聚合层模块化与综合验收均已通过。
3. 历史基线：
   - `Step36`：发布化稳定锚点
   - `Step30`：功能与增强交付基线
   - `Step24`：主链基线

## 2. 目标与时长

1. 目标：在 10~15 分钟内完成“业务页面 + dashboard 合同解释 + 数据接入 + 技术链路 + 综合验收”的完整演示。
2. 节奏：
   - 启动环境并打开业务页面
   - 展示业主端推荐 / 订单 / 账单 / 导航的连续旅程
   - 展示物业端经营驾驶舱、实时标签与降级说明
   - 说明 Step38/39 如何收敛合同、状态表达和聚合层
   - 运行默认 Step40 验收收口

## 3. 演示前检查

1. Docker Desktop 已运行。
2. Python 可执行路径可用。
3. Node 与 npm 可用。
4. 端口可用：`8080`, `8081`, `8000`, `8090`, `4173`, `15672`, `9090`, `13000`, `13306`。
5. 建议先运行 `./scripts/defense_demo.sh preflight` 或 `make preflight`。
6. 若当前机器只做脚本/仓库检查，还未启动 Docker，可先运行 `make preflight-static`。

## 4. 一键命令

1. 启动环境并拉起前端业务入口
```bash
./scripts/defense_demo.sh preflight
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

4. 运行默认 Step40 综合验收
```bash
./scripts/defense_demo.sh acceptance
# 或
make acceptance
# 或
python3 scripts/test_step40_release_acceptance.py
```

5. 运行 Step38 / Step39 增量 gate
```bash
make step38-check
make step39-check
make step40-check
```

6. 如需回放 Step36 发布化稳定基线
```bash
./scripts/defense_demo.sh acceptance-step36
# 或
make acceptance-step36
```

7. 如需回放 Step30 / Step24 历史基线
```bash
./scripts/defense_demo.sh acceptance-step30
./scripts/defense_demo.sh acceptance-step24
```

8. 停止清理
```bash
./scripts/defense_demo.sh stop
```

9. 导出当前交付包
```bash
make release-bundle
```

## 5. 默认展示地址

1. 统一登录：`http://localhost:4173/login`
2. 业主演示账号：`owner_demo / demo123`
3. 物业演示账号：`admin_demo / admin123`
4. 诊断地址（仅备用）：
   - Gateway health：`http://localhost:8080/actuator/health`
   - RabbitMQ：`http://localhost:15672`
   - Grafana：`http://localhost:13000`

## 6. 推荐演示顺序

1. 业主端业务链路
   - 查看推荐车位与统一页面状态提示
   - 创建预约并进入订单页
   - 查看预估金额与计费规则
   - 完成订单并展示最终账单
   - 打开导航页并展示页面内地图预览与外部地图 fallback

2. 物业端业务链路
   - 查看经营摘要、趋势图与 highlights
   - 展示实时 / 降级标签、来源、更新时间、失败原因
   - 查看占用率趋势与预测值 vs 实际值图表
   - 强调 Grafana / RabbitMQ 仍是技术诊断页，不混充业务页

3. 合同与架构解释链路
   - 说明 `/api/v1/owner/dashboard` 与 `/api/v1/admin/dashboard` 已进入 OpenAPI
   - 展示前端 `useOwnerDashboardView` / `useAdminDashboardView` 等页面级数据编排层
   - 说明 `ParkingDashboardViewModules.java` 如何拆分 query / assembler / view service

4. 技术故障链路
   - Step6：停 `model-service`，展示降级响应。
   - Step7：强制失败调度事件进入重试 / DLQ。
   - Step8：停 `realtime-service`，展示页面自动切换轮询。
   - Step9 / Step17：切到 Grafana 展示正常态 / 故障态 / 恢复态。

5. 验收收口
   - 运行 `./scripts/defense_demo.sh acceptance`
   - 强调默认完成态已从 Step36 升级为 Step40
   - 如需交付归档，再执行 `make release-bundle`
