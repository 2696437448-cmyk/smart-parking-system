# 技术验收清单（Step30 默认完成态）

## 1. 当前默认验收基线

1. 当前默认稳定完成态为 `Step30`。
2. `Step24` 继续作为历史主链基线保留，但默认收口入口已升级为 Step30。
3. Step30 验收必须同时满足“Step24 原回归通过 + Step26~29 增强能力通过”。

## 2. Step24 基线继续要求

1. 业主可携带幂等头创建预约。
2. 物业管理员可手动触发调度任务。
3. 系统可返回预测结果与调度结果。
4. 业主端页面可展示推荐、预约结果、账单与导航。
5. 物业端页面可展示资源监控与日/区域收益统计。
6. 并发预约测试：无超卖、无重复扣费。
7. 模型服务宕机测试：触发降级并返回可解释字段。
8. MQ 故障测试：重试后进入 DLQ 且可追踪。
9. WebSocket 断连测试：自动切换轮询并继续更新。
10. 订单重复完成测试：不重复结算、不重复确认收益。

## 3. Step25 文档收敛验收

1. `progress.md`、`implementation-plan.md`、`gap-matrix.md`、`architecture.md`、`acceptance.md`、README、runbook 口径一致。
2. 不再出现“Step24 已完成”与“Step24 待完成”并存的文档冲突。
3. Step30 已被标记为当前稳定默认完成态。
4. Step24 已降级为历史主链基线说明，而非默认完成态。

## 4. Step26 数据接入与分析增强验收

1. 存在 raw ingest 接口：`sensor-events`、`lpr-events`、`resident-patterns`。
2. MySQL raw 表可接收并保存三类近真实数据。
3. ETL 可从 raw 表跑到 `forecast_feature_table` 与 `dispatch_input_table`。
4. ETL 额外产出占用热度、车辆流向、业主出行高峰摘要。
5. 严格验收时质量报告显示 `engine=spark`。
6. 明文车牌不得落库。

## 5. Step27 App 壳层验收

1. 前端依赖中存在 Capacitor。
2. 存在 Capacitor 配置与 Android 壳层。
3. 业主端具备移动优先布局、底部导航、订单/账单卡片化展示。
4. 同一套 API 同时服务 Web 与 App 壳层。
5. `npm run typecheck`、`npm run build`、Capacitor 壳层检查通过。

## 6. Step28 地图导航增强验收

1. 导航页可展示页面内地图预览。
2. 响应继续兼容 `map_url + eta_minutes + destination`。
3. 响应新增 `region_label`、`slot_display_name`、`route_summary` 等兼容字段。
4. 页面可展示 ETA、目标车位、路线摘要、地图跳转按钮。
5. 外部地图跳转仍可作为 fallback 使用。

## 7. Step29 物业图表化验收

1. 物业端业务页面存在收益趋势图。
2. 物业端业务页面存在区域收益对比图。
3. 物业端业务页面存在占用率趋势图。
4. 物业端业务页面存在预测值 vs 实际值对照图。
5. 图表数据可回溯到 `billing_records`、收益汇总或 ETL/预测输出。
6. Grafana 仍保留为技术诊断视图，不混充业务图表页。

## 8. Step30 增强验收收口（已完成）

1. Step24 原全量回归已继续通过。
2. Step26~29 新增验收已全部通过。
3. 已形成新的增强版技术验收报告与 machine-readable gate results。
4. README / runbook / memory-bank 默认完成态已升级到 Step30。

## 9. Git 管理验收

1. 仓库可 clone 并读取完整项目文档、执行脚本与增强阶段材料。
2. 每步继续满足 `branch created`、`commit exists`、`PR merged`、`tag created`。
3. `progress.md` 继续记录 `branch`、`commit_id`、`PR链接/编号`、`tag`、`rollback_tag`。
