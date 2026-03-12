# 技术验收清单

## 1. 功能性

1. 业主可携带幂等头创建预约。
2. 物业管理员可手动触发调度任务。
3. 系统可返回预测结果与调度结果。
4. 看板可展示占用趋势与收益概览。

## 2. 可靠性

1. 并发预约测试：无超卖、无重复扣费。
2. 模型服务宕机测试：触发降级并返回可解释字段。
3. MQ 故障测试：重试后进入 DLQ 且可追踪。
4. WebSocket 断连测试：自动切换轮询并继续更新。

## 3. 工程证据

1. Docker 一键启动可在干净环境复现。
2. API 合同文档与运行时字段一致。
3. 网关/业务/模型日志可关联 `trace_id`。
4. 性能或对比报告有可复现实验证据。

## 4. 论文证据

1. 数据统计图。
2. 模型与调度流程图。
3. 基线模型与 LSTM 对比表。
4. 故障注入与降级演示记录。

## 5. 定稿对齐验收（Step 11~18）

1. 业务后端对齐：`parking-service` 已切换为 Java 主业务实现，核心写路径不再依赖内存幂等。
2. 一致性主链路对齐：写接口满足 Redis 幂等 + Redisson 锁 + MySQL 唯一约束。
3. 数据工程对齐：PySpark ETL 可稳定产出 `forecast_feature_table` 与 `dispatch_input_table`。
4. 模型工程对齐：存在 LSTM 训练脚本、训练产物与基线模型对比结果。
5. 模型管理对齐：模型版本注册、激活、热切换与回滚均可验证。
6. 前端工程对齐：Vue3 + TypeScript + Pinia 工程化项目可运行，保持实时/降级状态展示。
7. 性能证据对齐：存在 JMeter 或 k6 的 P95/P99、错误率、吞吐对比报告。
8. 回归完整性：原 Step 4~10 闸门全部通过且无能力退化。

## 6. Git 管理验收

1. 仓库可 clone 并读取完整项目文档与执行脚本。
2. 标签完整：至少包含 `step10-pass-baseline` 与后续 `stepNN-pass`。
3. 每步有对应证据提交：`memory-bank/progress.md` 与 `reports/stepNN_execution.md`。
4. 每步 Git 闸门完整：`branch created`、`commit exists`、`PR merged`、`tag created`。
