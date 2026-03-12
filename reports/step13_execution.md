# Step 13 执行报告（模型工程化：注册表 + 热切换 + 回滚）

## 执行范围

1. 目标：实现模型版本注册、激活切换与在线回滚（不重启服务）。
2. 输入：Step 12 训练产物（`artifacts/models/*.json`）。
3. 不包含：Step 14（Java parking-service 迁移）。

## 已实现产物

1. 模型服务增强：`services/model_service.py`
   - 新增模型注册表加载与持久化。
   - 新增激活历史记录（`activation_history`）。
   - `POST /internal/v1/model/activate` 支持：
     - 正常激活（`status=active`）
     - 自动回滚（`rollback=true`, `status=rolled_back`）
   - 新增 `GET /internal/v1/model/registry` 查询当前注册版本与激活状态。
   - 预测接口返回当前 `model_version`，可用于联调验证切换是否生效。

2. 注册表同步脚本：`scripts/step13_sync_model_registry.py`
   - 从 Step12 训练产物生成/更新：`artifacts/models/model_registry.json`。
   - 自动合并内置版本（`v0.1-lstm-lite`、`v0.2-lstm-lite`）与训练版本。

3. 闸门脚本：`scripts/test_step13_model_registry.py`
   - 校验注册表包含关键版本。
   - 校验在线激活后 `predict` 命中新版本。
   - 校验自动回滚后 `predict` 恢复上一版本。
   - 校验无重启（进程持续存活）与注册表历史持久化。
   - 联动 OpenAPI 合同校验，确认接口契约未退化。

## 执行命令与结果

1. 生成注册表：

```bash
cd /Users/yanchen/VscodeProject/smart-parking-thesis
python3 scripts/step13_sync_model_registry.py
```

结果：
- `status=ok`
- `output=artifacts/models/model_registry.json`
- `active_version=step12-lstm-lite-v1`
- `model_count=4`

2. Step13 闸门：

```bash
python3 scripts/test_step13_model_registry.py
```

结果：
- 输出：`STEP13_GATE_PASS`

3. 合同回归：

```bash
python3 scripts/validate_openapi.py --spec openapi/smart-parking.yaml
```

结果：
- 输出：`openapi_validation_passed spec=openapi/smart-parking.yaml`

## 版本切换与回滚演示结果

1. 初始激活：`step12-lstm-lite-v1`
2. 激活切换：`step12-baseline-v1`
3. 再切换：`step12-lstm-lite-v1`
4. 自动回滚：恢复到 `step12-baseline-v1`
5. 全过程模型服务进程未重启，符合在线热切换要求。

## 验收映射

1. 对齐 `implementation-plan.md` Step13：
   - 模型注册表：已实现并持久化。
   - 激活接口增强：已实现并支持回滚语义。
   - 在线热切换：已通过无重启闸门验证。
2. 对齐 `acceptance.md` 定稿条目（阶段性）：
   - “模型管理对齐：版本注册、激活、热切换与回滚”已具备可复现证据。
