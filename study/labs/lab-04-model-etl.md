# Lab 04：ETL / 模型 / Registry / 验收

## 理解题

题目：为什么 ETL、训练、registry、在线服务必须分开理解？

参考答案：因为它们分别解决数据整理、模型生成、版本管理和在线推理，不是同一层事情。分开理解后，你才不会把“训练完成”误当成“系统已经接好”。

为什么答案对：这是工程链，而不是单脚本。

## 定位题

题目：如果要找 registry 当前激活版本，你该先看哪里？

参考答案：先看 `artifacts/models/model_registry.json` 的 `active_version`，再回到 `step13_sync_model_registry.py` 看它怎样生成。

为什么答案对：registry 文件就是当前状态快照。

## 字段追踪题

题目：`step12-lstm-lite-v1` 是从哪里写进 registry 的？

参考答案：它先由 `step12_train_models.py` 生成模型文件，再由 `step13_sync_model_registry.py` 读取 artifact 并写入 `models` 字典。

为什么答案对：registry 不是训练脚本直接写死出来的唯一结构，而是同步脚本汇总出的结果。

## 最小验证题

题目：如果只允许你做 3 个动作来验证模型链，选什么？

参考答案：跑 ETL、同步 registry、查看 model registry 接口。若环境允许，再跑 Step40 验收脚本。

为什么答案对：这 3 步能验证数据、版本状态和在线暴露是否都接上了。

## 复述题

题目：解释为什么 Step40 不是“模型训练成功一次”。

参考答案：因为 Step40 验收看的是系统完成态，里面包含历史 gate、release bundle、文档对齐和系统级检查，不只是模型文件能不能生成。
