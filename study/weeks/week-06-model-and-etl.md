# 第 6 周：模型与 ETL

## 本周目标

- 理解这个项目里数据是怎么变成预测和调度结果的
- 看懂 `ETL -> 特征表 -> 模型 -> 在线服务` 这条链
- 学会区分“学术名词”和“工程实现”

## 你会先看哪些文件

- `scripts/step11_etl.py`
- `scripts/step12_train_models.py`
- `scripts/step13_sync_model_registry.py`
- `services/model_service.py`
- `data/raw/slot_status.csv`
- `data/raw/vehicle_event.csv`
- `data/raw/resident_pattern.csv`
- `data/processed/forecast_feature_table.csv`

## 这部分代码到底在做什么

很多新手一看到“LSTM”就会以为这部分一定最难。  
其实这个项目里的算法线并不是“炫模型”，而是很工程化地把问题拆成了 4 段：

1. `ETL`
   把原始数据整理成可用于建模和调度的特征表
2. `训练`
   用轻量 LSTM-lite 和 baseline 对比，生成模型产物
3. `注册表`
   把可用模型整理进 model registry，支持激活和回滚
4. `在线服务`
   接收请求，做预测、调度优化，并返回结果

### ETL 在干什么

`step11_etl.py` 读取三类原始数据：

- 车位占用
- 车辆进出
- 居民出行模式

然后把它们转成两个更适合后续使用的表：

- `forecast_feature_table.csv`
- `dispatch_input_table.csv`

### 模型服务在干什么

`model_service.py` 在线上做两件核心事：

1. 预测某区域未来供需
2. 基于 cost 矩阵，用 Hungarian 算法做分配优化

所以你可以把它理解成：

- 预测：告诉你未来可能多紧张
- 优化：告诉你应该怎么分配车位

## 一条必须跟读的调用链

这周建议你跟 `预测 + 调度` 这条链：

1. 原始数据先由 `step11_etl.py` 处理
2. 生成 `forecast_feature_table.csv`
3. `step12_train_models.py` 用特征表训练 `lstm_lite`
4. `step13_sync_model_registry.py` 把模型写进注册表
5. `model_service.py` 启动后加载 registry
6. 收到预测请求时调用 `_forecast()`
7. 收到调度请求时调用 `_optimize()`
8. `_optimize()` 内部使用 `_hungarian_assign()` 计算最优分配

## 给新手的概念解释

### 什么是 ETL

ETL 可以简单理解成：  
把原始数据清洗、整理、转换成后续系统能直接使用的结构。

### 什么是 LSTM-lite

这里不是完整大规模深度学习系统，而是一个轻量、可解释、依赖少的实现。  
你可以先把它理解成“一个简化版时序预测模型”。

### 什么是 Hungarian 算法

它常用于“分配问题”。  
比如这里：多个请求、多个车位，怎样整体分配才更优。  
你暂时不需要深入数学证明，只需要知道它解决的是“全局最优匹配”。

### 什么是模型注册表

模型注册表就是一份“当前有哪些模型、哪个是激活版本、历史切换记录是什么”的清单。  
这让模型服务不需要把版本写死在代码里。

## 本周可直接运行的命令

```bash
# 1. 跑 ETL
python3 scripts/step11_etl.py

# 2. 训练模型
python3 scripts/step12_train_models.py

# 3. 同步模型注册表
python3 scripts/step13_sync_model_registry.py

# 4. 查看模型服务 registry 接口
curl http://localhost:8000/internal/v1/model/registry
```

## 本周小练习

1. 找出 `step11_etl.py` 最终产出的两个核心输出文件。
2. 用自己的话写出 `_forecast()` 的输入和输出分别是什么。
3. 找出 `_optimize()` 内部在哪里调用了 Hungarian 算法。
4. 比较 `baseline_last_value` 和 `lstm_lite`，写一句话说明两者区别。

## 本周完成标准

- 你能说出 ETL、训练、注册表、在线推理四者的关系
- 你知道这个项目的模型线是“预测 + 优化”组合
- 你知道模型切换不是写死在代码里的，而是由 registry 管理

## 可选加深阅读

- `artifacts/models/model_registry.json`
- `artifacts/models/lstm_lite_v1.json`
- `scripts/test_step19b_hungarian.py`
- `reports/step19b_execution.md`

## 继续深入

模型链的详细带读请继续：

- `../chains/chain-04-etl-model-registry-acceptance.md`
- `../labs/lab-04-model-etl.md`

