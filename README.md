# 智慧停车毕设项目

该仓库用于毕业设计《智慧停车调度与共享系统》的完整工程实现与答辩复现。

## 当前执行流程

项目采用 "vibe coding" 交付流水线：

1. 冻结题目边界与约束。
2. 建立 `memory-bank` 文档上下文。
3. 先产出无代码实施计划。
4. 按步骤逐项实现，每步都过测试闸门并记录进度。
5. 将工程产物同步沉淀为论文与答辩产物。

## 建议阅读顺序

1. `memory-bank/prd.md`
2. `memory-bank/data-spec.md`
3. `memory-bank/tech-stack.md`
4. `memory-bank/risk-register.md`
5. `memory-bank/implementation-plan.md`

## 环境依赖安装

```bash
python3 -m pip install -r requirements-dev.txt
```

说明：`scripts/validate_openapi.py` 依赖 `PyYAML`，执行全量回归前请先安装以上依赖。

## Step 0 数据健康检查命令

```bash
python3 scripts/data_health_check.py \
  --project-root . \
  --schema-config config/data_health_schema.yaml \
  --json-output reports/data_health_report.json \
  --md-output reports/data_health_report.md
```

## Step16 前端工程命令

```bash
cd apps/frontend
npm install
npm run dev
```

默认访问：`http://localhost:5173`

## Step17 性能证据命令

```bash
# baseline
python3 scripts/step17_collect_performance.py --scenario baseline --output reports/step17_perf_baseline.json

# fault（先停 model-service）
python3 scripts/step17_collect_performance.py --scenario fault --output reports/step17_perf_fault.json

# recovery（恢复 model-service 后）
python3 scripts/step17_collect_performance.py --scenario recovery --output reports/step17_perf_recovery.json

# 汇总报告
python3 scripts/step17_build_report.py \
  --baseline reports/step17_perf_baseline.json \
  --fault reports/step17_perf_fault.json \
  --recovery reports/step17_perf_recovery.json \
  --md-output reports/step17_performance_summary.md \
  --csv-output reports/step17_performance_summary.csv
```

## 论文与答辩入口

1. 论文证据包：
   - `reports/thesis_evidence_package.md`
2. 答辩演示脚本说明：
   - `docs/defense_demo_runbook.md`
3. 一键答辩脚本：
   - `scripts/defense_demo.sh`

### 常用命令

```bash
# 启动演示环境
./scripts/defense_demo.sh start

# 跑基线闸门（合同 + 一致性 + 模型）
./scripts/defense_demo.sh baseline

# 跑故障注入序列（降级、DLQ、实时通道、可观测性）
./scripts/defense_demo.sh faults

# 一次性完整回放
./scripts/defense_demo.sh full

# 清理环境
./scripts/defense_demo.sh stop
```
