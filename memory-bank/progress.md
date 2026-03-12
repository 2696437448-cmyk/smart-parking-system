# 项目进度日志

## 进度记录模板（从 Step 11 起强制使用）

每次追加记录必须包含以下字段：

1. 完成时间：`YYYY-MM-DD HH:mm`（本地时区）。
2. 当前步骤：如 `Step 11`。
3. 目标与范围：本次仅覆盖的能力边界。
4. 实际改动：关键文件/模块与行为变化。
5. 闸门结果：执行命令、通过/失败标识、证据路径。
6. Git 分支：`branch`。
7. Git 提交：`commit_id`（可多个）。
8. PR 信息：`PR链接/编号`。
9. 标签信息：`tag`。
10. 回滚标签：`rollback_tag`（若无填 `N/A`）。
11. 卡点与修复：阻塞原因、修复动作、剩余风险。
12. 下一阻塞：进入下一步前必须满足的条件。

## 2026-03-11

1. 初始化 memory-bank 文档体系。
2. 冻结技术路线与执行顺序。
3. 增加风险登记（规划乐观、上下文膨胀、数据质量风险）。
4. 加入 Step 0 数据健康闸门与阻塞点优先策略。
5. 完成提示词模板增强（自动生成进度/架构/实验记录）。
6. 完成 `data_health_check.py` 与 schema 配置。

## 2026-03-11 Step 0~2（通过）

1. Step 0：生成 fallback 样例数据并过健康检查（`overall_passed=True`）。
2. Step 1：完成仓库骨架与 compose 结构。
3. Step 2：冻结 OpenAPI 合同并通过校验。
4. 证据：`reports/step0_step2_execution.md`。

## 2026-03-11 Step 3（通过）

1. 实现网关基础路由与 `X-Trace-Id` 透传。
2. 通过 compose 运行态转发测试。
3. 证据：`reports/step3_execution.md`。

## 2026-03-12 Step 4（通过）

1. 实现预约一致性三层防护：幂等、细粒度锁、DB 唯一约束。
2. 并发闸门通过：`STEP4_GATE_PASS`。
3. 证据：`reports/step4_execution.md`。

## 2026-03-12 Step 5（通过）

1. 模型服务实现 `/predict`、`/optimize`、`/activate`。
2. 闸门通过：`STEP5_GATE_PASS`。
3. 证据：`reports/step5_execution.md`。

## 2026-03-12 Step 6（通过）

1. 网关实现模型服务故障降级响应。
2. 闸门通过：`STEP6_GATE_PASS`。
3. 证据：`reports/step6_execution.md`。

## 2026-03-12 Step 7（通过）

1. 完成 RabbitMQ 可靠链路（重试 + DLQ）。
2. 闸门通过：`STEP7_RABBIT_SETUP_OK`、`STEP7_GATE_PASS`。
3. 证据：`reports/step7_execution.md`。

## 2026-03-12 Step 8（通过）

1. 完成 WebSocket 主通道与轮询降级。
2. 闸门通过：`STEP8_WEBSOCKET_OK`、`STEP8_GATE_PASS`。
3. 证据：`reports/step8_execution.md`。

## 2026-03-12 Step 9（通过）

1. 完成 Prometheus + Grafana + 结构化日志。
2. 闸门通过：`STEP9_BASELINE_OK`、`STEP9_GATE_PASS`。
3. 修复：Grafana 端口冲突，改为 `13000`。
4. 证据：`reports/step9_execution.md`。

## 2026-03-12 Step 10 技术验收（通过）

1. 串行执行 Step4~Step9 全部闸门并通过。
2. 合同校验与 compose 校验均通过。
3. 最终结论：`TECHNICAL_ACCEPTANCE_PASS`。
4. 证据：`reports/step10_technical_acceptance.md`。

## 2026-03-12 论文与答辩文档打包（完成）

1. 新增论文证据包：`reports/thesis_evidence_package.md`。
2. 新增答辩演示说明：`docs/defense_demo_runbook.md`。
3. 新增一键演示脚本：`scripts/defense_demo.sh`。
4. README 更新为中文导航与演示命令。

## 2026-03-12 报告中文化（完成）

1. 将历史执行报告统一改为中文：
   - `reports/step0_step2_execution.md`
   - `reports/step3_execution.md`
   - `reports/step4_execution.md`
   - `reports/step5_execution.md`
   - `reports/step6_execution.md`
   - `reports/step7_execution.md`
   - `reports/step8_execution.md`
   - `reports/step9_execution.md`
2. 保持 AI 提示词模板英文不变（`memory-bank/prompt-templates.md`）。

## 2026-03-12 综合方案落地（阶段 0/1 文档冻结完成）

1. 冻结决策：
   - `connect=10000ms/read=2500ms` 稳定性优先。
   - 四服务定义为“3 核心服务 + 1 实时伴生服务”。
2. 扩展计划：在 `implementation-plan.md` 新增 Step 11~18。
3. 扩展验收：在 `acceptance.md` 新增“定稿对齐验收（Step 11~18）”。
4. 新增差距矩阵：`memory-bank/gap-matrix.md`。
5. 证据：本次变更对应 memory-bank 文档更新。

## 2026-03-12 Git 管理补强（通过）

1. 新增 `memory-bank/git-workflow.md`，固化导入、分支、PR、标签与回滚流程。
2. 在 `implementation-plan.md` 增加 `Step G0` 与全步骤 Git 闸门。
3. 模板新增 Git 字段：`branch`、`commit_id`、`PR链接/编号`、`tag`、`rollback_tag`。
4. Git 分支：`N/A`（文档阶段，仓库尚未初始化）。
5. Git 提交：`N/A`。
6. PR：`N/A`。
7. 标签：`N/A`。
8. 回滚标签：`N/A`。
9. 证据：`memory-bank/git-workflow.md` 与相关文档修订。

## 2026-03-12 Step 11（通过）

1. 完成时间：2026-03-12 16:30（Asia/Shanghai）。
2. 当前步骤：Step 11 - 数据工程补齐（PySpark ETL）。
3. 目标与范围：仅完成 ETL 主流程、输出两张特征表与质量报告，不进入 Step 12 训练。
4. 实际改动：
   - 新增 `scripts/step11_etl.py`
   - 新增 `scripts/test_step11_etl.py`
   - 新增 `reports/step11_execution.md`
   - 新增 ETL 产物 `data/processed/*.csv` 与 `reports/step11_etl_quality.json`
   - 更新 `memory-bank/architecture.md`、`memory-bank/gap-matrix.md`
5. 闸门结果：
   - 命令：`python3 scripts/test_step11_etl.py`
   - 结果：`STEP11_GATE_PASS`
   - 证据：`reports/step11_execution.md`
6. Git 分支：`feat/step11-etl`。
7. Git 提交：`d6a4e7f`, `828ecd7`。
8. PR 信息：`https://github.com/2696437448-cmyk/smart-parking-system/pull/new/feat/step11-etl`。
9. 标签信息：`N/A`。
10. 回滚标签：`N/A`。
11. 卡点与修复：
   - 卡点：环境无 `pyspark`。
   - 修复：脚本实现 `PySpark 优先 + Python fallback`，保证当前环境闸门可通过。
12. 下一阻塞：
   - 完成 PR 合并并创建 `step11-pass` 标签；
   - 进入 Step12 前确认训练环境与依赖方案。

## 2026-03-12 Step 12（通过）

1. 完成时间：2026-03-12 17:26（Asia/Shanghai）。
2. 当前步骤：Step 12 - 模型训练补齐（LSTM + 基线对比）。
3. 目标与范围：补齐可复现训练、统一评估指标（MAE/RMSE/MAPE）与论文对比证据，不进入 Step 13 注册表切换实现。
4. 实际改动：
   - 新增 `scripts/step12_train_models.py`
   - 新增 `scripts/step12_baseline_model.py`
   - 新增 `scripts/test_step12_model_training.py`
   - 新增训练产物与对比报告（`artifacts/models/*.json`、`reports/step12_model_*`）
   - 新增执行报告 `reports/step12_execution.md`
   - 新增开发依赖文件 `requirements-dev.txt`（补 PyYAML）
5. 闸门结果：
   - 命令：`python3 scripts/test_step12_model_training.py`
   - 结果：`STEP12_GATE_PASS`
   - 证据：`reports/step12_execution.md`
6. Git 分支：`feat/step12-model-training`。
7. Git 提交：`ed6e2f7`。
8. PR 信息：`https://github.com/2696437448-cmyk/smart-parking-system/pull/new/feat/step12-model-training`。
9. 标签信息：`N/A`（待 PR 合并后打 `step12-pass`）。
10. 回滚标签：`N/A`。
11. 卡点与修复：
   - 卡点：OpenAPI 回归依赖 `PyYAML` 缺失。
   - 修复：安装并固化 `PyYAML==6.0.3`，回归恢复通过。
12. 下一阻塞：
   - 完成 Step12 PR 合并；
   - 进入 Step13 前确认模型注册表文件落地与热切换回滚闸门脚本通过。
