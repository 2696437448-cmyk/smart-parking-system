# 第 3 周：模型、ETL 与验收

这一周容易让新手紧张，因为会看到 `ETL`、`LSTM-lite`、`Hungarian`、`registry` 这些词。  
但你这周不需要先攻数学，而是先把工程链路看清楚。

## 这周只学什么

只回答 3 个问题：

1. 原始数据是怎样变成模型可用输入的
2. 模型服务在线上到底负责什么
3. 当前默认完成态是靠什么脚本和口径来验收的

## 这周配套讲义

按这个顺序读：

1. [第 6 周：模型与 ETL](../weeks/week-06-model-and-etl.md)
2. [第 7 周：验收、报告与答辩表达](../weeks/week-07-acceptance-and-defense.md)
3. [新手常用命令](../appendix/commands.md)

## 先看哪些文件

- `scripts/step11_etl.py`
- `scripts/step12_train_models.py`
- `scripts/step13_sync_model_registry.py`
- `services/model_service.py`
- `artifacts/models/model_registry.json`
- `reports/step40_technical_acceptance.md`
- `scripts/test_step40_release_acceptance.py`

如果你愿意配合数据文件一起看，再补：

- `data/raw/slot_status.csv`
- `data/raw/vehicle_event.csv`
- `data/raw/resident_pattern.csv`
- `data/processed/forecast_feature_table.csv`

## 这周不要先看

- LSTM 的完整数学推导
- Hungarian 算法证明
- 所有历史 step 的全部报告
- 大量无关的实验产物

## 带读节奏

### 第 1 次：先看工程链，不先看算法细节

先把这 4 段记住：

1. `ETL`
2. `训练`
3. `注册表`
4. `在线服务`

只要你先把这四段关系搞清楚，后面再看模型名词就不会慌。

### 第 2 次：跟 ETL -> 训练 -> registry

按这个顺序读：

1. `step11_etl.py`
2. `step12_train_models.py`
3. `step13_sync_model_registry.py`
4. `artifacts/models/model_registry.json`

关注点：

- 输入是什么
- 生成了什么文件
- 激活模型版本是怎么记录的

### 第 3 次：跟 model-service 在线职责

重点看：

- `_forecast()`
- `_optimize()`
- `_hungarian_assign()`
- `_switch_model()`

只要先知道：

- `_forecast()` 是预测未来供需
- `_optimize()` 是做分配优化
- registry 是让模型版本别写死在代码里

就够了。

### 第 4 次：看验收口径

这一步很重要，因为很多新手会读代码，但不会讲“系统怎么证明自己可用”。

先看：

1. `reports/step40_technical_acceptance.md`
2. `scripts/test_step40_release_acceptance.py`

你要形成的认识是：  
`Step40` 不是随口说的版本名，而是当前默认完成态和验收口径。

## 这周必须跑或验证的命令

至少做其中 3 件：

```bash
python3 scripts/step11_etl.py
python3 scripts/step12_train_models.py
python3 scripts/step13_sync_model_registry.py
curl http://localhost:8000/internal/v1/model/registry
python3 scripts/test_step40_release_acceptance.py
```

如果本机环境不完整，也至少读懂这些命令分别是在验证哪一段。

## 这周必须会说的主链

1. 原始数据进入 ETL
2. ETL 生成特征表和调度输入
3. 训练脚本生成模型产物
4. registry 记录当前可用模型和激活版本
5. `model_service.py` 启动后加载 registry
6. 在线请求进入 `_forecast()` 或 `_optimize()`
7. 默认完成态由 Step40 验收脚本校验

## 这周复述题

1. ETL、训练、registry、在线服务四者分别负责什么？
2. 为什么 registry 比把模型版本写死在代码里更合理？
3. `_forecast()` 和 `_optimize()` 分别解决什么问题？

## 这周定位题

1. 找出 `step11_etl.py` 最终写出的核心输出文件。
2. 找出 `model_service.py` 中调用 Hungarian 分配的关键位置。
3. 找出当前默认完成态是由哪个验收脚本代表的。

## 这周完成标准

- 你能说出 ETL、训练、registry、在线服务的关系
- 你知道模型服务不是只做预测，还做调度优化
- 你知道当前默认验收是 Step40，而不是随便跑一个旧脚本
- 你至少完成一次脚本运行或接口/脚本级验证

## 卡住时怎么退回

1. 回看本页“这周必须会说的主链”
2. 回看 [第 6 周讲义](../weeks/week-06-model-and-etl.md)
3. 只重读 `step11_etl.py -> step12_train_models.py -> step13_sync_model_registry.py`
4. 最后再回到 `model_service.py`

## 详细深读与练习

如果你准备真正跟模型链和验收链，请继续：

- `../chains/chain-04-etl-model-registry-acceptance.md`
- `../labs/lab-04-model-etl.md`

