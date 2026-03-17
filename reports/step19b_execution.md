# Step19B 执行报告

## 目标

1. 移除调度 cost 中对 Python `hash()` 的依赖。
2. 将 `/internal/v1/dispatch/optimize` 改为确定性的真实 Hungarian 求解。
3. 增加小样本 brute-force 对照校验，确认最优性。

## 实际改动

1. 更新 `services/model_service.py`：
   - 新增稳定哈希 `_stable_unit()`；
   - 以确定性距离/拥堵/价格构造 cost matrix；
   - 新增 `_hungarian_assign()` 实现；
   - 将策略统一为 `hungarian_optimal`。
2. 新增 `scripts/test_step19b_hungarian.py`。
3. 修复 Python 3.12 下 `importlib + dataclass` 的测试加载问题。

## 验证命令

```bash
python3 scripts/test_step19b_hungarian.py
```

## 验证结果

1. 闸门输出：`STEP19B_GATE_PASS`
2. 同一输入重复运行结果一致。
3. 小规模样本与 brute-force 最优结果一致。
4. 大规模样本不再退化为贪心策略。

## 结论

Step19B 通过，模型服务的调度接口已与“确定性真实 Hungarian”口径对齐。
