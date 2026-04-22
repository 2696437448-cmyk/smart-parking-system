# Chain 04：ETL / 模型 / Registry / 在线推理 / 验收链

## 这条链解决什么业务问题

它解决的是：原始停车数据怎样被整理成特征表、训练成模型、登记到 registry、在线提供预测与优化能力，最后再被 Step40 验收脚本纳入系统完成态。

## 学完后你必须会说的 3 句话

1. ETL、训练、registry、在线推理是四个不同阶段，不是一段脚本包打天下。
2. `_forecast()` 和 `_optimize()` 解决的是不同问题：一个做预测，一个做分配优化。
3. Step40 验收验证的是整套系统完成态，而不是单纯某个模型文件是否存在。

## 预备知识

- 知道 CSV / JSON 文件是什么
- 知道“模型文件”和“注册表文件”不是一回事
- 知道验收脚本是系统级检查，不只是单元测试

## 不要先看的文件

- 全量数学推导
- 所有历史 step 报告
- 与当前主线无关的旧模型实验文件

## 场景故事

停车系统不只是页面和接口。后台还要把原始车位状态、车辆事件和居民出行规律整理出来，再训练轻量模型，用 registry 管理版本，最后由 model-service 在在线请求里调用。为了保证当前完成态可证明，Step40 还要把这套链纳入验收。

## 跟读路线

### Step 1：先看 ETL 最终产出了什么

打开：`scripts/step11_etl.py`

重点看：`--forecast-output`、`--dispatch-output`、`report["outputs"]`

这一步要回答的问题：ETL 到底输出了哪些关键文件？

参考答案：最关键的是 `data/processed/forecast_feature_table.csv` 和 `data/processed/dispatch_input_table.csv`，同时还会输出质量报告和若干 Step26 摘要 JSON。

### Step 2：看训练脚本产出了哪些模型文件

打开：`scripts/step12_train_models.py`

重点看：`baseline_last_value_v1.json`、`lstm_lite_v1.json`

这一步要回答的问题：训练脚本是不是只训练一个模型？

参考答案：不是。它会产出 `baseline_last_value_v1.json` 和 `lstm_lite_v1.json`，用于基线对比和轻量 LSTM 模型。

### Step 3：看 registry 为什么存在

打开：`scripts/step13_sync_model_registry.py`
再看：`artifacts/models/model_registry.json`

重点看：`active_version`、`models`

这一步要回答的问题：为什么不能把模型版本直接写死在 `model_service.py` 里？

参考答案：因为 registry 让模型服务可以读取当前可用模型和激活版本，后续也方便切换、回滚和记录历史，而不是把版本硬编码进逻辑里。

### Step 4：看 model-service 的在线职责

打开：`services/model_service.py`

重点看：`_forecast()`、`_optimize()`、`_hungarian_assign()`、`_switch_model()`

这一步要回答的问题：为什么说 model-service 不是只做预测？

参考答案：因为 `_forecast()` 负责按区域和 horizon 预测供需，而 `_optimize()` 会基于请求构建分配问题，并在内部调用 `_hungarian_assign()` 做匹配优化。

### Step 5：看 `_hungarian_assign()` 在什么位置发挥作用

打开：`services/model_service.py`

重点看：`_optimize()` 调用 `_hungarian_assign(cost_matrix)`

这一步要回答的问题：Hungarian 算法在项目里是独立脚本，还是在线逻辑的一部分？

参考答案：它是在线优化逻辑的一部分，由 `_optimize()` 在处理 dispatch 请求时调用。

### Step 6：看 Step40 为什么是系统完成态

打开：`scripts/test_step40_release_acceptance.py`
再看：`reports/step40_technical_acceptance.md`

重点看：它会跑哪些 gate、检查哪些报告和交付物

这一步要回答的问题：Step40 验收为什么不是“模型训练成功一次”就算通过？

参考答案：因为 Step40 验收会检查 Step36/38/39 相关 gate、release bundle、文档对齐、报告内容等，它是系统完成态的收口，而不是单点脚本通过。

## 代码理解题

### 1. `forecast_feature_table.csv` 和 `dispatch_input_table.csv` 的角色有什么不同？

参考答案：前者更偏模型训练 / 预测特征，后者更偏调度输入。它们来自同一轮 ETL，但服务于不同后续环节。

### 2. 为什么 Step12 同时保留 baseline 和 lstm_lite？

参考答案：因为系统需要一个传统基线做对比，帮助说明轻量模型是否真的带来更好效果。

### 3. `_switch_model()` 为什么重要？

参考答案：因为它体现了模型版本不是写死的，服务端可以在 registry 基础上切换或回滚激活版本。

## 定位训练题

### 1. 如果要找 registry 当前激活模型写在哪里，你该先看哪里？

参考答案：先看 `artifacts/models/model_registry.json` 里的 `active_version`，再看 `step13_sync_model_registry.py` 如何生成它，最后再看 `model_service.py` 如何读取它。

### 2. 如果要找在线优化算法入口，你该看哪里？

参考答案：`model_service.py` 里的 `_optimize()`，因为它内部会构造 cost matrix 并调用 `_hungarian_assign()`。

## 字段追踪题

题目：`active_version` 最终会影响什么？

参考答案：它决定 model-service 当前优先加载和使用哪个模型版本；`_switch_model()`、registry 读取逻辑和模型信息接口都会围绕这个字段工作。

## 最小验证

```bash
python3 scripts/step11_etl.py
python3 scripts/step12_train_models.py
python3 scripts/step13_sync_model_registry.py
curl http://localhost:8000/internal/v1/model/registry
python3 scripts/test_step40_release_acceptance.py
```

## 常见误解

- 误解：模型线就是训练一个 LSTM 文件
  纠正：真实链路至少包含 ETL、训练、registry、在线服务和验收。
- 误解：registry 只是多余 JSON
  纠正：它承担模型版本管理和激活状态表达。
- 误解：Step40 就是模型通过了
  纠正：Step40 是系统级完成态验收，不是单算法成功。

## 1 分钟复述稿

“原始停车数据先经过 `step11_etl.py`，被整理成 `forecast_feature_table.csv` 和 `dispatch_input_table.csv`。接着 `step12_train_models.py` 用这些特征训练出 baseline 和 `lstm_lite` 两类模型文件。然后 `step13_sync_model_registry.py` 把可用模型整理进 `model_registry.json`，并标出当前 `active_version`。在线阶段由 `model_service.py` 读取 registry，其中 `_forecast()` 负责预测，`_optimize()` 负责分配优化，后者内部还会调用 `_hungarian_assign()`。最后 `test_step40_release_acceptance.py` 把这条链纳入系统级验收，所以这不是一个单脚本故事，而是一整条工程链。”

## 学完后应该留下什么记录

- 一张从 raw data 到 Step40 的链路图
- 一个模型文件和 registry 的区别说明
- 一次 ETL / registry / Step40 的验证记录
