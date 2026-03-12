# 论文证据包（答辩可直接使用）

## 1. 项目基线

1. 项目根目录：`/Users/yanchen/VscodeProject/smart-parking-thesis`
2. 技术形态：`Java 网关 + Python 业务/模型/实时服务 + Vue3 演示页 + RabbitMQ + Prometheus + Grafana + Docker Compose`
3. 数据基线：`data/raw` fallback 数据已通过 Step 0 健康闸门。

## 2. 工程证据索引（可映射到论文章节）

1. 数据质量证据
   - `reports/data_health_report.json`
   - `reports/data_health_report.md`

2. 接口合同证据
   - `openapi/smart-parking.yaml`
   - `scripts/validate_openapi.py`

3. 可靠性证据
   - `reports/step4_execution.md`
   - `reports/step6_execution.md`
   - `reports/step7_execution.md`
   - `reports/step8_execution.md`

4. 可观测性证据
   - `reports/step9_execution.md`
   - `infra/prometheus/prometheus.yml`
   - `infra/grafana/dashboards/step9-observability.json`

5. 总验收证据
   - `reports/step10_technical_acceptance.md`

## 3. 实验记录模板（问题-方法-实验-结论）

### 3.1 Step 4 一致性

1. 问题：并发预约可能超卖。
2. 方法：幂等 + 锁 + DB 唯一约束。
3. 实验：`python scripts/test_step4_consistency.py`。
4. 结论：并发下无超卖，闸门通过。

### 3.2 Step 6 降级可用性

1. 问题：模型服务故障导致核心流程中断。
2. 方法：网关降级返回 `fallback_reason/fallback_strategy`。
3. 实验：停模型服务后运行 `test_step6_resilience.py`。
4. 结论：降级成功，业务可解释可用。

### 3.3 Step 7 MQ 可靠性

1. 问题：异步消息失败与重复消费。
2. 方法：重试 + DLQ + 消费幂等语义。
3. 实验：`setup_rabbitmq.py` + `dispatch_worker.py` + `test_step7_mq_reliability.py`。
4. 结论：失败消息可追踪进入 DLQ。

### 3.4 Step 8 实时通道鲁棒性

1. 问题：WebSocket 中断造成页面静止。
2. 方法：WebSocket 主通道 + 轮询兜底。
3. 实验：先 realtime，再停 realtime-service 后 fallback。
4. 结论：页面可自动切换并持续更新。

### 3.5 Step 9 可观测性

1. 问题：故障态缺少可视证据。
2. 方法：Prometheus 指标 + Grafana 看板 + trace_id 日志。
3. 实验：baseline/fault 两阶段脚本。
4. 结论：故障前后状态转移可被明确观测。

## 4. 论文图表清单（建议）

1. 数据质量统计图（空值率、重复率、解析成功率）。
2. 系统与调度流程图（含降级与异常流）。
3. 可靠性实验对比表（场景/注入动作/预期/结果）。

## 5. 复现命令摘要

```bash
cd /Users/yanchen/VscodeProject/smart-parking-thesis
python scripts/validate_openapi.py --spec openapi/smart-parking.yaml
docker compose -f infra/docker-compose.yml config
./scripts/defense_demo.sh full
```

## 6. 答辩速讲提纲

1. 一致性：Step4 证明并发下无超卖。
2. 可用性：Step6 证明模型故障可降级不硬失败。
3. 可靠性：Step7 证明重试与 DLQ 完整链路。
4. 用户体验：Step8 证明实时通道异常自动切换。
5. 可运维性：Step9 证明指标与日志闭环可观测。
