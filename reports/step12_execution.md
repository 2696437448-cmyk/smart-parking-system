# Step 12 执行报告（模型训练补齐：LSTM + 基线对比）

## 执行范围

1. 目标：补齐可复现训练与评估闭环，输出 LSTM 轻量模型与传统基线模型对比结果。
2. 输入：`data/processed/forecast_feature_table.csv`（Step 11 ETL 产物）。
3. 不包含：Step 13 的模型注册表与在线热切换。

## 已实现产物

1. 训练脚本：`scripts/step12_train_models.py`
   - 训练模型：`lstm_lite`
   - 对比模型：`baseline_last_value`
   - 输出指标：`MAE`、`RMSE`、`MAPE`
   - 可复现参数：`seed`、`sequence_len`、`train_ratio`、`epochs`

2. 基线脚本：`scripts/step12_baseline_model.py`
   - 独立执行传统基线评估，用于论文对照实验。

3. 闸门脚本：`scripts/test_step12_model_training.py`
   - 训练结果结构校验
   - 两次同参运行可复现性校验
   - OpenAPI 合同回归校验

4. 训练产物：
   - `artifacts/models/lstm_lite_v1.json`
   - `artifacts/models/baseline_last_value_v1.json`
   - `reports/step12_model_metrics.json`
   - `reports/step12_model_comparison.csv`
   - `reports/step12_model_comparison.md`

## 执行命令与结果

1. 训练与对比：

```bash
cd /Users/yanchen/VscodeProject/smart-parking-thesis
python3 scripts/step12_train_models.py
```

结果摘要：
- `train_samples=672`
- `test_samples=168`
- baseline test: `MAE=0.12410714`, `RMSE=0.1607738`, `MAPE=21.52126104`
- lstm_lite test: `MAE=0.09250858`, `RMSE=0.11655648`, `MAPE=16.93389441`

2. Step 12 闸门：

```bash
python3 scripts/test_step12_model_training.py
```

结果：
- 输出：`STEP12_GATE_PASS`

## 指标对比结论

1. 在当前 fallback 数据集上，`lstm_lite` 在测试集三个指标均优于 `baseline_last_value`。
2. 指标改进（test split）：
   - MAE 相对下降约 `25.46%`
   - RMSE 相对下降约 `27.50%`
   - MAPE 相对下降约 `21.32%`

## 合同一致性说明

1. 训练脚本内置 `DemandGapRecord` 预览输出字段：`region_id/ts/supply/demand/gap`。
2. 闸门脚本同时执行 OpenAPI 校验，确保 Step 12 后接口合同未退化。

## 阻塞与修复

1. 历史阻塞：OpenAPI 校验依赖 `PyYAML`。
2. 修复状态：已补依赖并通过回归，Step 12 闸门可连续执行。
