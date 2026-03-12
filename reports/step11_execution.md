# Step 11 执行报告（数据工程补齐：PySpark ETL）

## 执行范围

1. 目标：实现多源数据对齐并产出统一特征表。
2. 输入：`slot_status.csv`、`vehicle_event.csv`、`resident_pattern.csv`（fallback 路径）。
3. 不包含：Step 12 训练脚本与模型评估对比。

## 已实现产物

1. ETL 主脚本：`scripts/step11_etl.py`
   - 产出：
     - `data/processed/forecast_feature_table.csv`
     - `data/processed/dispatch_input_table.csv`
     - `reports/step11_etl_quality.json`
   - 执行引擎策略：`PySpark 优先 + Python fallback`。
   - source 模式：支持 `external` 与 `fallback_raw` 双路径。

2. 闸门脚本：`scripts/test_step11_etl.py`
   - 校验输出文件存在与非空。
   - 校验两张特征表关键字段完整。
   - 校验时间字段可解析。
   - 校验质量报告 `overall_passed=true`。

## 执行命令与结果

1. Step 11 闸门执行：

```bash
cd /Users/yanchen/VscodeProject/smart-parking-thesis
python3 scripts/test_step11_etl.py
```

2. 结果：
- 闸门输出：`STEP11_GATE_PASS`
- 质量报告：`reports/step11_etl_quality.json`
  - `engine=python`（当前环境未安装 `pyspark`，自动 fallback）
  - `source_mode=fallback_raw`
  - `forecast_feature_table` 行数：`864`
  - `dispatch_input_table` 行数：`864`
  - `overall_passed=true`

## 阻塞与修复

1. 阻塞：执行环境缺少 `pyspark` 依赖。
2. 修复：实现 `engine=auto` 策略，自动降级到 Python 引擎，保持 ETL 闸门可通过。
3. 后续：在 Step 11 强化阶段可安装 `pyspark` 并复跑同一脚本，输出引擎将自动切换为 `spark`。

## 验收映射

1. 对齐 `implementation-plan.md` 的 Step 11 输出要求：
   - `forecast_feature_table` 已生成。
   - `dispatch_input_table` 已生成。
   - ETL 质量报告已生成。
2. 对齐 `acceptance.md` 定稿条目（阶段性）：
   - 数据工程链路已落地并可复现。
