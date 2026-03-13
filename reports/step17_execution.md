# Step 17 执行报告（可观测性与性能证据补齐）

## 执行范围

1. 目标：补齐 Step17 要求的可观测性三视图与性能对比证据（P95/P99、错误率、吞吐）。
2. 输入：Step9 可观测性基线、Step15 网关熔断、Step16 前端工程化。
3. 不包含：Step18 全量验收与论文阶段收口。

## 已实现产物

1. Prometheus 抓取增强
   - 更新 `infra/prometheus/prometheus.yml`。
   - 新增 `gateway-service` 抓取任务（`/actuator/prometheus`）。

2. Grafana 三视图（正常/故障/恢复）
   - `infra/grafana/dashboards/step17-normal-state.json`
   - `infra/grafana/dashboards/step17-fault-state.json`
   - `infra/grafana/dashboards/step17-recovery-state.json`

3. 性能采样与报告脚本
   - `scripts/step17_collect_performance.py`（场景压测采样）
   - `scripts/step17_build_report.py`（汇总 md/csv）
   - `scripts/test_step17_observability_performance.py`（Step17 闸门）

4. 性能证据文件
   - `reports/step17_perf_baseline.json`
   - `reports/step17_perf_fault.json`
   - `reports/step17_perf_recovery.json`
   - `reports/step17_performance_summary.md`
   - `reports/step17_performance_summary.csv`

## 执行命令与结果

1. 组合配置与环境启动

```bash
cd /Users/yanchen/VscodeProject/smart-parking-thesis
docker compose -f infra/docker-compose.yml config
docker compose -f infra/docker-compose.yml up -d gateway-service parking-service model-service realtime-service rabbitmq prometheus grafana
```

结果：`COMPOSE_OK`，相关容器全部启动

2. baseline 场景（正常态）

```bash
python3 scripts/test_step9_observability.py --mode baseline
python3 scripts/step17_collect_performance.py --scenario baseline --requests 320 --concurrency 20 --warmup 20 --output reports/step17_perf_baseline.json
```

结果：`STEP9_BASELINE_OK`、`STEP17_PERF_BASELINE_PASS`

3. fault 场景（故障态）

```bash
docker compose -f infra/docker-compose.yml stop model-service
python3 scripts/test_step9_observability.py --mode fault
python3 scripts/step17_collect_performance.py --scenario fault --requests 320 --concurrency 20 --warmup 20 --output reports/step17_perf_fault.json
```

结果：`STEP9_GATE_PASS`、`STEP17_PERF_FAULT_PASS`

4. recovery 场景（恢复态）

```bash
docker compose -f infra/docker-compose.yml start model-service
python3 scripts/test_step9_observability.py --mode baseline
python3 scripts/step17_collect_performance.py --scenario recovery --requests 320 --concurrency 20 --warmup 20 --output reports/step17_perf_recovery.json
```

结果：`STEP9_BASELINE_OK`、`STEP17_PERF_RECOVERY_PASS`

5. 汇总与闸门

```bash
python3 scripts/step17_build_report.py \
  --baseline reports/step17_perf_baseline.json \
  --fault reports/step17_perf_fault.json \
  --recovery reports/step17_perf_recovery.json \
  --md-output reports/step17_performance_summary.md \
  --csv-output reports/step17_performance_summary.csv
python3 scripts/test_step17_observability_performance.py
```

结果：`STEP17_REPORT_PASS`、`STEP17_GATE_PASS`

## 核心指标结果（来自报告）

1. baseline
   - 吞吐：290.7134 rps
   - 错误率：0.0000
   - 降级率：0.0344
   - P95：29.41 ms
   - P99：1015.77 ms

2. fault
   - 吞吐：1608.0153 rps
   - 错误率：0.0000
   - 降级率：1.0000
   - P95：18.84 ms
   - P99：23.22 ms

3. recovery
   - 吞吐：277.9952 rps
   - 错误率：0.0000
   - 降级率：0.0406
   - P95：30.79 ms
   - P99：1024.09 ms

## 验收映射

1. 对齐 `implementation-plan.md` Step17：
   - 已形成 Grafana 三视图 + Prometheus 抓取证据。
   - 已形成可复现性能对比报告（P95/P99、错误率、吞吐）。

2. 对齐 `acceptance.md` 定稿条目：
   - “性能证据对齐”已具备可复现实验产物与脚本。

## 风险与说明

1. P99 在 baseline/recovery 场景存在秒级长尾（约 1s），与模型路径偶发慢请求有关。
2. fault 场景因降级短路，延迟更低且吞吐更高，属于预期现象。
3. Step18 建议补一轮不同并发参数（如 10/30/50）验证长尾稳定性。
