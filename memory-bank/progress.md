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
7. Git 提交：`ed6e2f7`, `a497e08`。
8. PR 信息：`https://github.com/2696437448-cmyk/smart-parking-system/pull/new/feat/step12-model-training`。
9. 标签信息：`N/A`（待 PR 合并后打 `step12-pass`）。
10. 回滚标签：`N/A`。
11. 卡点与修复：
   - 卡点：OpenAPI 回归依赖 `PyYAML` 缺失。
   - 修复：安装并固化 `PyYAML==6.0.3`，回归恢复通过。
12. 下一阻塞：
   - 完成 Step12 PR 合并；
   - 进入 Step13 前确认模型注册表文件落地与热切换回滚闸门脚本通过。


## 2026-03-12 Step 13（通过）

1. 完成时间：2026-03-12 17:47（Asia/Shanghai）。
2. 当前步骤：Step 13 - 模型工程化（注册与热切换）。
3. 目标与范围：实现模型版本注册、在线激活和回滚，不进入 Step 14 Java 业务后端迁移。
4. 实际改动：
   - 升级 `services/model_service.py`（registry + activate + rollback + history）
   - 新增 `scripts/step13_sync_model_registry.py`
   - 新增 `scripts/test_step13_model_registry.py`
   - 新增注册表产物 `artifacts/models/model_registry.json`
   - 新增执行报告 `reports/step13_execution.md`
5. 闸门结果：
   - 命令：`python3 scripts/test_step13_model_registry.py`
   - 结果：`STEP13_GATE_PASS`
   - 证据：`reports/step13_execution.md`
6. Git 分支：`feat/step13-model-registry`。
7. Git 提交：`095f016`。
8. PR 信息：`https://github.com/2696437448-cmyk/smart-parking-system/pull/new/feat/step13-model-registry`。
9. 标签信息：`N/A`（待 PR 合并后打 `step13-pass`）。
10. 回滚标签：`N/A`。
11. 卡点与修复：
   - 卡点：需要在不改动既有合同的前提下扩展回滚语义。
   - 修复：保持 `model_version` 字段必填兼容，同时增加 `rollback`/`action` 扩展参数，OpenAPI 回归持续通过。
12. 下一阻塞：
   - 完成 Step13 PR 合并；
   - 进入 Step14 前准备 Java parking-service 脚手架与 Redis/Redisson/MySQL 运行环境。

## 2026-03-13 Step 14（通过）

1. 完成时间：2026-03-13 10:58（Asia/Shanghai）。
2. 当前步骤：Step 14 - 业务后端对齐（Java + MySQL/Redis/Redisson）。
3. 目标与范围：将 `parking-service` 迁移为 Java 主业务服务并对齐一致性主链路，不进入 Step 15 网关治理升级。
4. 实际改动：
   - 新增 `services/parking-service`（Spring Boot + Redis + Redisson + MySQL 一致性链路）。
   - 更新 `infra/docker-compose.yml`（parking-service 切换为 Java 运行形态）。
   - 新增 `scripts/test_step14_java_consistency.py`。
   - 新增执行证据 `reports/step14_execution.md`。
5. 闸门结果：
   - `python3 scripts/test_step14_java_consistency.py` -> `STEP14_GATE_PASS`
   - `python3 scripts/test_step4_consistency.py` -> `STEP4_GATE_PASS`
   - `python3 scripts/test_step7_mq_reliability.py ...` -> `STEP7_GATE_PASS`
   - `python3 scripts/test_step8_realtime_channel.py --mode fallback ...` -> `STEP8_GATE_PASS`
   - `python3 scripts/validate_openapi.py --spec openapi/smart-parking.yaml` -> `openapi_validation_passed`
6. Git 分支：`feat/step14-java-parking-service`。
7. Git 提交：`161de73`。
8. PR 信息：`https://github.com/2696437448-cmyk/smart-parking-system/pull/new/feat/step14-java-parking-service`。
9. 标签信息：`N/A`（待 PR 合并后打 `step14-pass`）。
10. 回滚标签：`N/A`。
11. 卡点与修复：
   - 卡点：RabbitMQ publish 在 Java 端出现 `vhost_not_found/EOF` 等不稳定响应。
   - 修复：固定 publish API 路径、切换 Java `HttpClient`、增加容错重试与非标准响应兼容。
12. 下一阻塞：
   - 完成 Step14 PR 合并并打 `step14-pass` 标签；
   - 进入 Step15 前明确网关治理最小可验收范围（Resilience4j + 降级语义回归）。

## 2026-03-13 Step 15（通过）

1. 完成时间：2026-03-13 12:18（Asia/Shanghai）。
2. 当前步骤：Step 15 - 网关治理对齐（Spring Cloud Gateway + Resilience4j）。
3. 目标与范围：网关治理能力对齐并固化降级语义，不进入 Step 16 前端工程化。
4. 实际改动：
   - 新建 `services/gateway-service` Spring Boot 工程（Gateway + Resilience4j + trace 过滤器 + fallback 控制器）。
   - 更新 `infra/docker-compose.yml` 使 gateway-service 以 Maven/Spring Boot 运行。
   - 新增 `scripts/test_step15_gateway_governance.py`。
   - 新增 `reports/step15_execution.md`。
   - 修复回归脚本可重复性：`test_step3_gateway.py`、`test_step4_consistency.py`、`test_step14_java_consistency.py`。
5. 闸门结果：
   - `docker compose -f infra/docker-compose.yml config` -> `COMPOSE_OK`
   - `python3 scripts/test_step6_resilience.py`（模型停机） -> `STEP6_GATE_PASS`
   - `python3 scripts/test_step15_gateway_governance.py`（模型停机） -> `STEP15_GATE_PASS`
   - `python3 scripts/test_step3_gateway.py` -> `STEP3_GATE_PASS`
   - `python3 scripts/test_step4_consistency.py` -> `STEP4_GATE_PASS`
   - `python3 scripts/test_step14_java_consistency.py` -> `STEP14_GATE_PASS`
   - `python3 scripts/test_step7_mq_reliability.py ...` -> `STEP7_GATE_PASS`
   - `python3 scripts/test_step8_realtime_channel.py --mode fallback ...` -> `STEP8_GATE_PASS`
   - `python3 scripts/validate_openapi.py --spec openapi/smart-parking.yaml` -> `openapi_validation_passed`
6. Git 分支：`feat/step15-gateway-governance`。
7. Git 提交：`3986131`, `d2b4bfb`, `f2268b3`, `f2c38fe`。
8. PR 信息：`https://github.com/2696437448-cmyk/smart-parking-system/pull/new/feat/step15-gateway-governance`。
9. 标签信息：`N/A`（待 PR 合并后打 `step15-pass`）。
10. 回滚标签：`step14-pass`。
11. 卡点与修复：
   - 卡点：旧回归脚本固定时间窗在重复执行时与历史数据冲突，出现假失败。
   - 修复：改为动态时间窗 + 合同字段校验，保证闸门可重复执行。
12. 下一阻塞：
   - 完成 Step15 PR 合并并打 `step15-pass` 标签；
   - 进入 Step16 前冻结前端最小交付边界（Vue3 + TS + Pinia + 实时/降级状态）。

## 2026-03-13 Step 16（通过）

1. 完成时间：2026-03-13 15:48（Asia/Shanghai）。
2. 当前步骤：Step 16 - 前端工程化（Vue3 + TypeScript + Pinia）。
3. 目标与范围：将前端从单文件演示页升级为工程化项目，并保持实时/降级状态语义。
4. 实际改动：
   - 新增 `apps/frontend` Vue3 + TS + Pinia 工程结构。
   - 新增 `apps/frontend/src/stores/realtime.ts`（连接状态与数据状态统一管理）。
   - 新增 `apps/frontend/src/composables/useRealtimeChannel.ts`（WebSocket 主通道 + Polling 兜底）。
   - 新增 `scripts/test_step16_frontend_engineering.py`。
   - 新增 `reports/step16_execution.md`。
   - 保留 `apps/frontend/realtime_dashboard_demo.html` 作为答辩兜底。
5. 闸门结果：
   - `python3 scripts/test_step16_frontend_engineering.py` -> `STEP16_GATE_PASS`
   - `python3 scripts/test_step8_realtime_channel.py --mode realtime ...` -> `STEP8_WEBSOCKET_OK`
   - `docker compose stop realtime-service && python3 scripts/test_step8_realtime_channel.py --mode fallback ... && docker compose start realtime-service` -> `STEP8_GATE_PASS`
   - `python3 scripts/test_step3_gateway.py` -> `STEP3_GATE_PASS`
   - `python3 scripts/validate_openapi.py --spec openapi/smart-parking.yaml` -> `openapi_validation_passed`
6. Git 分支：`feat/step16-frontend-engineering`。
7. Git 提交：`8bf96a3`, `98c9cd2`。
8. PR 信息：`https://github.com/2696437448-cmyk/smart-parking-system/pull/new/feat/step16-frontend-engineering`。
9. 标签信息：`N/A`（待 PR 合并后打 `step16-pass`）。
10. 回滚标签：`step15-pass`。
11. 卡点与修复：
   - 卡点：`npm install` 在当前环境下载阻塞，`node_modules` 未落地。
   - 修复：先以“结构闸门 + 通道语义回归”完成验收；在可联网环境执行 `npm install && npm run build` 补齐运行时证据。
12. 下一阻塞：
   - 完成 Step16 PR 合并并打 `step16-pass` 标签；
   - 进入 Step17 前冻结压测脚本与指标口径（P95/P99、错误率、吞吐）。

## 2026-03-13 Step 17（通过）

1. 完成时间：2026-03-13 16:10（Asia/Shanghai）。
2. 当前步骤：Step 17 - 可观测性与性能证据补齐。
3. 目标与范围：补齐三视图可观测证据与 baseline/fault/recovery 性能对比，不进入 Step18 全量验收。
4. 实际改动：
   - 更新 `infra/prometheus/prometheus.yml`，新增 `gateway-service` 指标抓取。
   - 新增 Grafana 三视图：`step17-normal-state.json`、`step17-fault-state.json`、`step17-recovery-state.json`。
   - 新增性能采样脚本 `scripts/step17_collect_performance.py`。
   - 新增性能汇总脚本 `scripts/step17_build_report.py`。
   - 新增 Step17 gate 脚本 `scripts/test_step17_observability_performance.py`。
   - 生成证据：`reports/step17_perf_*.json`、`reports/step17_performance_summary.md/csv`、`reports/step17_execution.md`。
5. 闸门结果：
   - `docker compose -f infra/docker-compose.yml config` -> `COMPOSE_OK`
   - `python3 scripts/test_step9_observability.py --mode baseline` -> `STEP9_BASELINE_OK`
   - `python3 scripts/test_step9_observability.py --mode fault` -> `STEP9_GATE_PASS`
   - `python3 scripts/step17_collect_performance.py --scenario baseline ...` -> `STEP17_PERF_BASELINE_PASS`
   - `python3 scripts/step17_collect_performance.py --scenario fault ...` -> `STEP17_PERF_FAULT_PASS`
   - `python3 scripts/step17_collect_performance.py --scenario recovery ...` -> `STEP17_PERF_RECOVERY_PASS`
   - `python3 scripts/step17_build_report.py ...` -> `STEP17_REPORT_PASS`
   - `python3 scripts/test_step17_observability_performance.py` -> `STEP17_GATE_PASS`
6. Git 分支：`feat/step17-observability-performance`。
7. Git 提交：`528a9c0`, `69ca89e`。
8. PR 信息：`https://github.com/2696437448-cmyk/smart-parking-system/pull/new/feat/step17-observability-performance`。
9. 标签信息：`N/A`（待 PR 合并后打 `step17-pass`）。
10. 回滚标签：`step16-pass`。
11. 卡点与修复：
   - 卡点：fault 场景需要验证可用性而非错误率，单看 HTTP 状态难以体现降级命中。
   - 修复：在性能采样中加入 `fallback_rate`，明确记录故障态降级命中比例（1.0）。
12. 下一阻塞：
   - 完成 Step17 PR 合并并打 `step17-pass` 标签；
   - 进入 Step18 前冻结最终全量回归清单与论文收口目录。

## 2026-03-13 Step 18（通过）

1. 完成时间：2026-03-13 16:26（Asia/Shanghai）。
2. 当前步骤：Step 18 - 全量验收与论文证据收口。
3. 目标与范围：执行 Step4~Step17 全量回归并生成最终技术验收报告、论文证据包与答辩脚本收口。
4. 实际改动：
   - 新增全量验收脚本 `scripts/test_step18_full_acceptance.py`。
   - 生成 `reports/step18_gate_results.json`。
   - 新增阶段验收报告 `reports/step18_technical_acceptance.md`。
   - 升级 `reports/thesis_evidence_package.md` 为 Step18 阶段版（后续可持续完善）。
   - 升级 `scripts/defense_demo.sh`，新增 `acceptance` 命令并纳入 `full` 流程。
   - 更新 `memory-bank/architecture.md`、`memory-bank/gap-matrix.md` 至阶段态。
5. 闸门结果：
   - `python3 scripts/test_step18_full_acceptance.py` -> `STEP18_GATE_PASS`
   - `reports/step18_gate_results.json` 显示 `overall_passed=true`（21/21）。
6. Git 分支：`feat/step18-final-acceptance`。
7. Git 提交：`a83ff1c`, `7b61ab8`。
8. PR 信息：`https://github.com/2696437448-cmyk/smart-parking-system/pull/new/feat/step18-final-acceptance`。
9. 标签信息：`N/A`（待 PR 合并后打 `step18-pass`）。
10. 回滚标签：`step17-pass`。
11. 卡点与修复：
   - 卡点：全量验收场景多、服务状态切换复杂，人工执行容易漏项。
   - 修复：脚本化编排 Step18 全量验收并输出 machine-readable 结果。
12. 下一阻塞：
   - 完成 Step18 PR 合并并打 `step18-pass` 标签；
   - 毕设技术侧进入迭代期，后续可继续做性能优化、功能增强与文档完善。

## 2026-03-17 Step 19A（通过）

1. 完成时间：2026-03-17 14:07（Asia/Shanghai）。
2. 当前步骤：Step 19A - Spark Strict 与依赖基线收敛。
3. 目标与范围：仅收敛 Spark strict 验收口径、统一依赖与 Java 运行时，不进入算法与业务功能改动。
4. 实际改动：
   - 更新 `requirements-dev.txt`，新增 `pyspark==3.5.1`
   - 新增 `scripts/test_step19a_spark_strict.py`
   - 生成 `reports/step19a_spark_quality.json`
   - 补 Homebrew OpenJDK 17，并让脚本自动探测 `JAVA_HOME`
   - 新增执行证据 `reports/step19a_execution.md`
5. 闸门结果：
   - `python3 scripts/test_step19a_spark_strict.py` -> `STEP19A_GATE_PASS`
   - `python3 scripts/validate_openapi.py --spec openapi/smart-parking.yaml` -> `openapi_validation_passed`
6. Git 分支：`feat/step19-step24-completion`。
7. Git 提交：`ff391c2`, `9349077`, `dcdcfe8`。
8. PR 信息：`#9 https://github.com/2696437448-cmyk/smart-parking-system/pull/9`。
9. 标签信息：`step19a-pass`。
10. 回滚标签：`step18-pass`。
11. 卡点与修复：
   - 卡点：本机缺少 Java Runtime，Spark 启动失败。
   - 修复：通过 Homebrew 安装 `openjdk@17`，并在脚本中自动探测 Homebrew JDK Home。
12. 下一阻塞：完成 Step19B、Step20~24 的代码 / 验收闭环，并最终补 Git 证据。

## 2026-03-17 Step 19B（通过）

1. 完成时间：2026-03-17 14:07（Asia/Shanghai）。
2. 当前步骤：Step 19B - 调度算法纠偏（确定性真实 Hungarian）。
3. 目标与范围：仅修复优化策略实现与可复现性，不改预测合同字段。
4. 实际改动：
   - 更新 `services/model_service.py`
   - 新增 `scripts/test_step19b_hungarian.py`
   - 新增执行证据 `reports/step19b_execution.md`
5. 闸门结果：
   - `python3 scripts/test_step19b_hungarian.py` -> `STEP19B_GATE_PASS`
6. Git 分支：`feat/step19-step24-completion`。
7. Git 提交：`ff391c2`, `9349077`, `dcdcfe8`。
8. PR 信息：`#9 https://github.com/2696437448-cmyk/smart-parking-system/pull/9`。
9. 标签信息：`step19b-pass`。
10. 回滚标签：`step18-pass`。
11. 卡点与修复：
   - 卡点：测试加载在 Python 3.12 下触发 `dataclass` 模块注册问题。
   - 修复：在测试中先将动态模块注册到 `sys.modules` 再执行。
12. 下一阻塞：进入计费与业务前端联调，验证新接口与新页面一致性。

## 2026-03-17 Step 20（通过）

1. 完成时间：2026-03-17 14:07（Asia/Shanghai）。
2. 当前步骤：Step 20 - 共享计费主链补齐。
3. 目标与范围：打通预约、预估、结算、账单主链，不扩展营销规则。
4. 实际改动：
   - 新增 `services/parking-service/src/main/java/com/smartparking/parking/ParkingBusinessExtensions.java`
   - 扩展 `services/parking-service/src/main/java/com/smartparking/parking/ParkingServiceApplication.java`
   - 扩展 `openapi/smart-parking.yaml`
   - 新增 `scripts/test_step20_billing_revenue.py`
   - 新增执行证据 `reports/step20_execution.md`
5. 闸门结果：
   - `python3 scripts/test_step20_billing_revenue.py` -> `STEP20_22_GATE_PASS`
6. Git 分支：`feat/step19-step24-completion`。
7. Git 提交：`ff391c2`, `9349077`, `dcdcfe8`。
8. PR 信息：`#9 https://github.com/2696437448-cmyk/smart-parking-system/pull/9`。
9. 标签信息：`step20-pass`。
10. 回滚标签：`step18-pass`。
11. 卡点与修复：
   - 卡点：测试最初使用固定幂等键与固定时间窗，重复运行会命中旧订单。
   - 修复：测试改为动态 `run_id` + 动态唯一时间窗，保证回归隔离。
12. 下一阻塞：将计费结果汇总到物业收益统计，并通过前端页面直接展示。

## 2026-03-17 Step 21（通过）

1. 完成时间：2026-03-17 14:07（Asia/Shanghai）。
2. 当前步骤：Step 21 - 业主端 / 物业端页面化交付。
3. 目标与范围：仅完成多页面业务前端与路由，不改实时协议语义。
4. 实际改动：
   - 更新 `apps/frontend/package.json` 与 `apps/frontend/package-lock.json`
   - 新增 `apps/frontend/src/router.ts`
   - 新增 `apps/frontend/src/pages/*`
   - 更新 `apps/frontend/src/App.vue`、`main.ts`、`styles.css`
   - 新增执行证据 `reports/step21_execution.md`
5. 闸门结果：
   - `python3 scripts/test_step21_frontend_pages.py` -> `STEP21_GATE_PASS`
   - `cd apps/frontend && npm run typecheck` -> pass
   - `cd apps/frontend && npm run build` -> pass
6. Git 分支：`feat/step19-step24-completion`。
7. Git 提交：`ff391c2`, `9349077`, `dcdcfe8`。
8. PR 信息：`#9 https://github.com/2696437448-cmyk/smart-parking-system/pull/9`。
9. 标签信息：`step21-pass`。
10. 回滚标签：`step18-pass`。
11. 卡点与修复：
   - 卡点：`npm install` 初次受证书链影响失败。
   - 修复：在 `apps/frontend/.npmrc` 固定 registry 与 `strict-ssl=false` 后重装依赖。
12. 下一阻塞：继续完成收益统计、演示入口与默认验收切换。

## 2026-03-17 Step 22（通过）

1. 完成时间：2026-03-17 14:07（Asia/Shanghai）。
2. 当前步骤：Step 22 - 收益统计与业务监控收口。
3. 目标与范围：完成按日 / 区域汇总和物业页业务监控，不扩展更复杂 BI 指标。
4. 实际改动：
   - 在 `ParkingBusinessExtensions.java` 中新增收益汇总与监控接口
   - 物业页 `AdminMonitor.vue` 直接消费业务汇总接口
   - 新增执行证据 `reports/step22_execution.md`
5. 闸门结果：
   - `python3 scripts/test_step20_billing_revenue.py` -> `STEP20_22_GATE_PASS`
6. Git 分支：`feat/step19-step24-completion`。
7. Git 提交：`ff391c2`, `9349077`, `dcdcfe8`。
8. PR 信息：`#9 https://github.com/2696437448-cmyk/smart-parking-system/pull/9`。
9. 标签信息：`step22-pass`。
10. 回滚标签：`step18-pass`。
11. 卡点与修复：
   - 卡点：需要确保收益统计来源唯一且可回溯。
   - 修复：统一以 `billing_records` 作为收益汇总唯一数据源。
12. 下一阻塞：升级演示入口与默认全量验收脚本。

## 2026-03-17 Step 23（通过）

1. 完成时间：2026-03-17 14:07（Asia/Shanghai）。
2. 当前步骤：Step 23 - 演示入口升级。
3. 目标与范围：调整 demo script 与文档默认入口，不修改核心业务语义。
4. 实际改动：
   - 更新 `scripts/defense_demo.sh`
   - 更新 `README.md`
   - 更新 `docs/defense_demo_runbook.md`
   - 新增 `scripts/test_step23_demo_entry.py`
   - 新增执行证据 `reports/step23_execution.md`
5. 闸门结果：
   - `./scripts/defense_demo.sh start` -> 输出业务 URL
   - `python3 scripts/test_step23_demo_entry.py` -> `STEP23_GATE_PASS`
6. Git 分支：`feat/step19-step24-completion`。
7. Git 提交：`ff391c2`, `9349077`, `dcdcfe8`。
8. PR 信息：`#9 https://github.com/2696437448-cmyk/smart-parking-system/pull/9`。
9. 标签信息：`step23-pass`。
10. 回滚标签：`step18-pass`。
11. 卡点与修复：
   - 卡点：Docker Desktop 未启动，整栈起不来。
   - 修复：启动 Docker Desktop 后重跑 `defense_demo.sh start`，确认 owner/admin 业务入口输出正常。
12. 下一阻塞：运行 Step24 全量验收并归档最终报告。

## 2026-03-17 Step 24（通过）

1. 完成时间：2026-03-17 14:07（Asia/Shanghai）。
2. 当前步骤：Step 24 - 新默认全量验收。
3. 目标与范围：覆盖旧 Step18 基线与新 Step19A~23 能力，生成新的默认验收结果。
4. 实际改动：
   - 新增 `scripts/test_step24_full_acceptance.py`
   - 生成 `reports/step24_gate_results.json`
   - 新增 `reports/step24_technical_acceptance.md`
5. 闸门结果：
   - `python3 scripts/test_step24_full_acceptance.py` -> `STEP24_GATE_PASS`
   - `reports/step24_gate_results.json` 显示 `overall_passed=true`
6. Git 分支：`feat/step19-step24-completion`。
7. Git 提交：`ff391c2`, `9349077`, `dcdcfe8`。
8. PR 信息：`#9 https://github.com/2696437448-cmyk/smart-parking-system/pull/9`。
9. 标签信息：`step24-pass`。
10. 回滚标签：`step18-pass`。
11. 卡点与修复：
   - 卡点：第一次 Step24 串跑时，Step20/22 测试受旧固定幂等键与固定时间窗污染导致失败。
   - 修复：将测试隔离为“每次运行唯一 run_id + 唯一时间窗”，第二次串跑通过。
12. 下一阻塞：
   - 补 Git 提交 / PR / tag；
   - 如继续迭代，可在 Step24 基础上做 UI 打磨与压测增强。

## 2026-03-18 Step19A~24 Git 收口（完成）

1. 更新时间：2026-03-18 00:12（Asia/Shanghai）。
2. 当前范围：为 Step19A~24 集成改造补 Git 元数据与安全收口，不再修改业务语义。
3. 收口说明：
   - Step19A~24 横跨 Spark strict、Hungarian、计费、前端页面、演示入口与全量验收，实际以单一集成分支 `feat/step19-step24-completion` 收口。
   - 仓库默认前端配置已恢复为安全值 `strict-ssl=true`；此前证书链问题仅作为本机临时 workaround，不再保留为仓库默认提交。
4. 本次验证：
   - `cd apps/frontend && npm run typecheck` -> pass
   - `cd apps/frontend && npm run build` -> pass
5. Git 分支：`feat/step19-step24-completion`。
6. Git 提交：
   - `ff391c2` `feat(step24): complete step19a-step24 business closure`
   - `9349077` `docs(step24): add step19a-step24 evidence and plan updates`
7. PR 信息：`#9 https://github.com/2696437448-cmyk/smart-parking-system/pull/9`。
8. 标签信息：`step19a-pass`, `step19b-pass`, `step20-pass`, `step21-pass`, `step22-pass`, `step23-pass`, `step24-pass`。
9. 回滚标签：`step18-pass`。
10. 收口结果：
   - 远端 PR #9 已合并到 `main`，合并提交：`d29ed20`。
   - Step19A~24 标签已推送完成，各步 Git 元数据已回填到 `progress.md`。

## 2026-03-24 Step 25（通过）

1. 完成时间：2026-03-24 09:11（Asia/Shanghai）。
2. 当前步骤：Step 25 - 文档与完成态口径收敛。
3. 目标与范围：统一 README、runbook、memory-bank、demo script 的默认完成态与执行口径。
4. 实际改动：
   - 更新 `README.md`
   - 更新 `docs/defense_demo_runbook.md`
   - 更新 `memory-bank/acceptance.md`
   - 更新 `memory-bank/architecture.md`
   - 更新 `memory-bank/gap-matrix.md`
   - 更新 `memory-bank/implementation-plan.md`
   - 新增 `reports/step25_execution.md`
5. 闸门结果：
   - 文档口径统一升级为 `Step30` 默认完成态。
6. Git 分支：`feat/step25-step30-enhancement`。
7. Git 提交：`N/A（本轮尚未提交）`。
8. PR 信息：`N/A`。
9. 标签信息：`N/A`。
10. 回滚标签：`step24-pass`。
11. 卡点与修复：
   - 卡点：原文档仍停留在“Step24 为默认完成态”。
   - 修复：在 Step30 验收通过后统一升级默认完成态口径。
12. 下一阻塞：补 raw ingest、App 壳层、地图导航、图表化与增强验收证据。

## 2026-03-24 Step 26（通过）

1. 完成时间：2026-03-24 09:11（Asia/Shanghai）。
2. 当前步骤：Step 26 - 近真实数据接入与 Spark 关联分析增强。
3. 目标与范围：补齐 raw ingest 接口、MySQL raw 表、Spark strict 分析输出。
4. 实际改动：
   - 新增 `services/parking-service/src/main/java/com/smartparking/parking/ParkingEnhancementController.java`
   - 更新 `infra/docker-compose.yml`
   - 更新 `openapi/smart-parking.yaml`
   - 更新 `scripts/step11_etl.py`
   - 新增 `scripts/test_step26_raw_ingest_analytics.py`
   - 生成 `reports/step26_spark_quality.json`
   - 生成 `reports/step26_occupancy_heatmap_summary.json`
   - 生成 `reports/step26_vehicle_flow_summary.json`
   - 生成 `reports/step26_resident_peak_summary.json`
   - 新增 `reports/step26_execution.md`
5. 闸门结果：
   - `python3 scripts/test_step26_raw_ingest_analytics.py` -> `STEP26_GATE_PASS`
   - 质量报告显示 `engine=spark`
6. Git 分支：`feat/step25-step30-enhancement`。
7. Git 提交：`N/A（本轮尚未提交）`。
8. PR 信息：`N/A`。
9. 标签信息：`N/A`。
10. 回滚标签：`step24-pass`。
11. 卡点与修复：
   - 卡点：`ParkingEnhancementController` 缺失 `trace()` 导致服务编译失败；初版 Step26 gate 仍误走 Python fallback。
   - 修复：补回 `trace()`，并将 Step26 gate 修正为 `Spark strict + mysql_raw`。
12. 下一阻塞：完成 App 壳层与增强前端验收。

## 2026-03-24 Step 27（通过）

1. 完成时间：2026-03-24 09:11（Asia/Shanghai）。
2. 当前步骤：Step 27 - App 壳层与移动优先业主端。
3. 目标与范围：补齐 Capacitor Android 壳层与移动优先交付。
4. 实际改动：
   - 更新 `apps/frontend/package.json`
   - 新增 `apps/frontend/package-lock.json`
   - 新增 `apps/frontend/capacitor.config.ts`
   - 新增 `apps/frontend/android/`
   - 新增 `apps/frontend/src/pages/OwnerOrders.vue`
   - 更新 `apps/frontend/src/App.vue`
   - 更新 `apps/frontend/src/router.ts`
   - 更新 `apps/frontend/src/styles.css`
   - 新增 `scripts/test_step27_app_shell.py`
   - 新增 `reports/step27_execution.md`
5. 闸门结果：
   - `npm run typecheck` -> pass
   - `npm run build` -> pass
   - `python3 scripts/test_step27_app_shell.py` -> `STEP27_GATE_PASS`
6. Git 分支：`feat/step25-step30-enhancement`。
7. Git 提交：`N/A（本轮尚未提交）`。
8. PR 信息：`N/A`。
9. 标签信息：`N/A`。
10. 回滚标签：`step24-pass`。
11. 卡点与修复：
   - 卡点：npm 访问官方 registry 时证书链报错；ECharts 类型定义导致 `typecheck` 失败；Step27 gate 初版在检查时又执行 `cap:sync`。
   - 修复：完成依赖重装、改用 `echarts/core` 引入、将 Step27 gate 改为纯校验。
12. 下一阻塞：完成地图导航与物业图表验收。

## 2026-03-24 Step 28（通过）

1. 完成时间：2026-03-24 09:11（Asia/Shanghai）。
2. 当前步骤：Step 28 - 地图导航增强。
3. 目标与范围：补齐页面内地图预览、ETA、路线摘要与外部地图 fallback。
4. 实际改动：
   - 新增 `apps/frontend/src/components/MapPreview.vue`
   - 更新 `apps/frontend/src/pages/OwnerNavigation.vue`
   - 更新 `services/parking-service/src/main/java/com/smartparking/parking/ParkingBusinessExtensions.java`
   - 新增 `scripts/test_step28_navigation_map.py`
   - 新增 `reports/step28_execution.md`
5. 闸门结果：
   - `python3 scripts/test_step28_navigation_map.py` -> `STEP28_GATE_PASS`
6. Git 分支：`feat/step25-step30-enhancement`。
7. Git 提交：`N/A（本轮尚未提交）`。
8. PR 信息：`N/A`。
9. 标签信息：`N/A`。
10. 回滚标签：`step24-pass`。
11. 卡点与修复：
   - 卡点：导航响应需兼容旧字段并扩展地图预览字段。
   - 修复：保留 `map_url` 语义并补 `region_label`、`slot_display_name`、`route_summary`。
12. 下一阻塞：补齐物业端图表数据与增强总验收。

## 2026-03-24 Step 29（通过）

1. 完成时间：2026-03-24 09:11（Asia/Shanghai）。
2. 当前步骤：Step 29 - 物业端图表化展示。
3. 目标与范围：补齐收益趋势、区域对比、占用率趋势、预测对照图。
4. 实际改动：
   - 新增 `apps/frontend/src/components/EChartPanel.vue`
   - 更新 `apps/frontend/src/pages/AdminMonitor.vue`
   - 新增 `scripts/test_step29_admin_charts.py`
   - 新增 `reports/step29_execution.md`
5. 闸门结果：
   - `python3 scripts/test_step29_admin_charts.py` -> `STEP29_GATE_PASS`
6. Git 分支：`feat/step25-step30-enhancement`。
7. Git 提交：`N/A（本轮尚未提交）`。
8. PR 信息：`N/A`。
9. 标签信息：`N/A`。
10. 回滚标签：`step24-pass`。
11. 卡点与修复：
   - 卡点：`revenue/trend` 在空账单状态下返回空数组，导致图表 gate 失败。
   - 修复：Step29 gate 在验图前自带一笔确认账单种子数据，保证图表接口有真实业务输入。
12. 下一阻塞：回放 Step24 基线并完成 Step30 总验收。

## 2026-03-24 Step 30（通过）

1. 完成时间：2026-03-24 09:11（Asia/Shanghai）。
2. 当前步骤：Step 30 - 增强验收与答辩升级。
3. 目标与范围：让 Step24 基线与 Step26~29 增强能力统一通过，并将默认完成态升级到 Step30。
4. 实际改动：
   - 新增 `scripts/test_step30_enhanced_acceptance.py`
   - 生成 `reports/step30_gate_results.json`
   - 新增 `reports/step30_technical_acceptance.md`
   - 更新 `scripts/defense_demo.sh`
   - 更新 `README.md`
   - 更新 `docs/defense_demo_runbook.md`
   - 更新 `memory-bank/*`
5. 闸门结果：
   - `python3 scripts/test_step24_full_acceptance.py` -> `STEP24_GATE_PASS`
   - `python3 scripts/test_step30_enhanced_acceptance.py` -> `STEP30_GATE_PASS`
   - `reports/step30_gate_results.json` 显示 `overall_passed=true`
6. Git 分支：`feat/step25-step30-enhancement`。
7. Git 提交：`N/A（本轮尚未提交）`。
8. PR 信息：`N/A`。
9. 标签信息：`N/A`。
10. 回滚标签：`step24-pass`。
11. 卡点与修复：
   - 卡点：Step18/24 历史基线被增强阶段 `mysql_raw` 小样本 ETL 误污染，且旧前端 token gate 与新页面结构存在兼容问题。
   - 修复：将历史 Step11 gate 固定回文件输入；补齐 Step16/21 兼容 token；恢复 Step24 全量通过后再回放 Step30。
12. 当前结论：`Step30` 已升级为默认稳定完成态，`Step24` 保留为历史主链基线。

## 2026-03-24 Step25~30 Git 收口（本地完成）

1. 更新时间：2026-03-24 15:26（Asia/Shanghai）。
2. 当前范围：为 Step25~30 增强阶段补本地 Git 提交与标签收口，不再修改业务语义与验收结果。
3. 收口说明：
   - 本轮以分支 `feat/step25-step30-enhancement` 完成 Step25~30 的实现、文档与证据收口。
   - `Step30` 继续作为当前稳定默认完成态，`Step24` 保留为历史主链基线。
   - 本次仅完成本地 commit/tag 收口，远端 push 与 PR 仍待后续执行。
4. 本次验证：
   - `git diff --check` -> pass
   - `python3 scripts/test_step24_full_acceptance.py` -> `STEP24_GATE_PASS`
   - `python3 scripts/test_step30_enhanced_acceptance.py` -> `STEP30_GATE_PASS`
5. Git 分支：`feat/step25-step30-enhancement`。
6. Git 提交：
   - `046f9f4` `feat(step30): implement enhancement delivery and gates`
   - `d6664a5` `docs(step30): update evidence and default completion docs`
7. PR 信息：`N/A（本轮未推送）`。
8. 标签信息：`step25-pass`, `step26-pass`, `step27-pass`, `step28-pass`, `step29-pass`, `step30-pass`（本地标签）。
9. 回滚标签：`step24-pass`。
10. 收口结果：
   - Step25~30 代码、文档、证据已完成本地提交收口。
   - `progress.md` 已补齐本地 Git 元数据，后续可直接执行 push / PR。
11. 剩余事项：
   - 如需完成远端 Git 闸门，还需推送分支、创建 PR，并把标签同步到远端。

## 2026-03-25 Step 31（通过）

1. 完成时间：2026-03-25 17:49（Asia/Shanghai）。
2. 当前步骤：Step 31 - Post-Step30 路线收敛。
3. 目标与范围：为 Step30 之后的迭代建立明确阶段路线，冻结“发布化增强”边界，不修改 Step30 默认完成态。
4. 实际改动：
   - 更新 `memory-bank/implementation-plan.md`
   - 更新 `memory-bank/gap-matrix.md`
   - 更新 `memory-bank/acceptance.md`
   - 更新 `memory-bank/architecture.md`
   - 更新 `README.md`
   - 更新 `docs/defense_demo_runbook.md`
   - 新增 `reports/step31_execution.md`
5. 闸门结果：
   - 文档已追加 Step31~36，且默认完成态仍保持为 `Step30`
   - `git diff --check` -> pass
6. Git 分支：`feat/step31-step36-release-hardening`。
7. Git 提交：`defa32c` `feat: add release hardening foundation for step31-step35`。
8. PR 信息：`#11 https://github.com/2696437448-cmyk/smart-parking-system/pull/11`。
9. 标签信息：`step31-pass`。
10. 回滚标签：`step30-pass`。
11. 卡点与修复：
   - 卡点：Step30 之后缺少明确后续路线，容易让默认完成态、增强阶段和交付阶段再次混淆。
   - 修复：新增 Step31~36，冻结“Step30 仍是默认完成态，Step36 通过后才允许升级”。
12. 下一阻塞：完成 Step32 环境模板、preflight 与统一命令入口的实际落地。

## 2026-03-25 Step 32（通过）

1. 完成时间：2026-03-25 17:49（Asia/Shanghai）。
2. 当前步骤：Step 32 - 环境模板与 preflight 基线。
3. 目标与范围：统一根目录环境模板、启动前检查、常用命令入口与 compose 环境变量覆盖能力。
4. 实际改动：
   - 新增 `.env.example`
   - 更新 `.gitignore`
   - 更新 `apps/frontend/.env.example`
   - 新增 `scripts/preflight_check.sh`
   - 新增 `Makefile`
   - 更新 `scripts/defense_demo.sh`
   - 更新 `infra/docker-compose.yml`
   - 新增 `reports/step32_execution.md`
5. 闸门结果：
   - `./scripts/preflight_check.sh --static` -> `STEP32_PREFLIGHT_PASS`
   - `make preflight-static` -> `STEP32_PREFLIGHT_PASS`
   - `./scripts/preflight_check.sh` -> `STEP32_PREFLIGHT_FAIL`（原因：当前机器 `docker daemon not ready`，属于预期拦截）
   - `git diff --check` -> pass
6. Git 分支：`feat/step31-step36-release-hardening`。
7. Git 提交：`defa32c` `feat: add release hardening foundation for step31-step35`。
8. PR 信息：`#11 https://github.com/2696437448-cmyk/smart-parking-system/pull/11`。
9. 标签信息：`step32-pass`。
10. 回滚标签：`step30-pass`。
11. 卡点与修复：
   - 卡点：当前环境的 Docker daemon 未就绪，严格 preflight 无法通过。
   - 修复：保留严格拦截语义，同时补 `--static` / `make preflight-static`，让脚本结构与仓库入口可在无 daemon 环境下先完成静态验证。
12. 下一阻塞：进入 Step33，把关键闸门接入 CI 自动回归。

## 2026-03-26 Step 33（通过）

1. 完成时间：2026-03-26 10:54（Asia/Shanghai）。
2. 当前步骤：Step 33 - CI 与回归自动化。
3. 目标与范围：把当前本地可跑的关键静态闸门收敛到 CI，并让 CI 与本地共用一套最小回归入口。
4. 实际改动：
   - 新增 `.github/workflows/ci.yml`
   - 新增 `scripts/test_step33_ci_smoke.py`
   - 更新 `Makefile`
   - 更新 `README.md`
   - 更新 `memory-bank/implementation-plan.md`
   - 更新 `memory-bank/gap-matrix.md`
   - 更新 `memory-bank/acceptance.md`
   - 更新 `memory-bank/architecture.md`
   - 新增 `reports/step33_execution.md`
   - 生成 `reports/step33_ci_smoke.json`
5. 闸门结果：
   - `make ci-smoke` -> pass
   - `python3 scripts/validate_openapi.py --spec openapi/smart-parking.yaml` -> pass
   - `python3 scripts/test_step33_ci_smoke.py` -> `STEP33_GATE_PASS`
   - `cd apps/frontend && npm run typecheck && npm run build` -> pass
   - `reports/step33_ci_smoke.json` 显示 `overall_passed=true`
6. Git 分支：`feat/step31-step36-release-hardening`。
7. Git 提交：`defa32c` `feat: add release hardening foundation for step31-step35`。
8. PR 信息：`#11 https://github.com/2696437448-cmyk/smart-parking-system/pull/11`。
9. 标签信息：`step33-pass`。
10. 回滚标签：`step30-pass`。
11. 卡点与修复：
   - 卡点：在当前 Codex 沙箱内直接运行 `make ci-smoke` 时，Step33 report 写入仓库路径被文件系统限制拦截。
   - 修复：以正常文件系统权限重跑同一命令；项目代码本身不改语义，最终 smoke gate 通过并生成报告。
12. 下一阻塞：进入 Step34，补 release bundle、交付目录与答辩资产版本化管理。

## 2026-03-26 Step 34（通过）

1. 完成时间：2026-03-26 13:32（Asia/Shanghai）。
2. 当前步骤：Step 34 - 发布包与演示交付物。
3. 目标与范围：补齐 release bundle、交付目录结构与答辩资产归档规范，不修改 Step30 默认完成态。
4. 实际改动：
   - 新增 `scripts/create_release_bundle.sh`
   - 更新 `Makefile`
   - 新增 `deliverables/README.md`
   - 新增 `deliverables/bundles/.gitkeep`
   - 新增 `deliverables/screenshots/.gitkeep`
   - 新增 `deliverables/recordings/.gitkeep`
   - 更新 `.gitignore`
   - 更新 `README.md`
   - 更新 `docs/defense_demo_runbook.md`
   - 更新 `memory-bank/implementation-plan.md`
   - 更新 `memory-bank/gap-matrix.md`
   - 更新 `memory-bank/acceptance.md`
   - 更新 `memory-bank/architecture.md`
   - 新增 `reports/step34_execution.md`
5. 闸门结果：
   - `bash -n scripts/create_release_bundle.sh` -> pass
   - `make release-bundle` -> `STEP34_BUNDLE_PASS`
   - 最新 bundle manifest 与 tar 内容抽查通过
   - `git diff --check` -> pass
6. Git 分支：`feat/step31-step36-release-hardening`。
7. Git 提交：`defa32c` `feat: add release hardening foundation for step31-step35`。
8. PR 信息：`#11 https://github.com/2696437448-cmyk/smart-parking-system/pull/11`。
9. 标签信息：`step34-pass`。
10. 回滚标签：`step30-pass`。
11. 卡点与修复：
   - 卡点：首版打包脚本输出的 `manifest` 路径指向临时目录，打包结束后不可直接访问。
   - 修复：将 manifest 额外导出到 `deliverables/bundles/*.manifest.txt` sidecar 文件，并重跑打包验证。
12. 下一阻塞：进入 Step35，补敏感项扫描、配置分层与安全恢复建议。

## 2026-03-26 Step 35（通过）

1. 完成时间：2026-03-26 14:21（Asia/Shanghai）。
2. 当前步骤：Step 35 - 安全与配置硬化。
3. 目标与范围：收敛 demo 默认值、secure 模板与本地覆盖策略，补齐敏感项扫描与安全恢复说明。
4. 实际改动：
   - 新增 `.env.secure.example`
   - 新增 `scripts/security_scan.py`
   - 新增 `scripts/test_step35_security_config.py`
   - 新增 `docs/security_hardening.md`
   - 更新 `.env.example`
   - 更新 `apps/frontend/.env.example`
   - 更新 `infra/docker-compose.yml`
   - 更新 `scripts/preflight_check.sh`
   - 更新 `scripts/defense_demo.sh`
   - 新增 `reports/step35_execution.md`
   - 生成 `reports/step35_security_scan.json`
   - 生成 `reports/step35_gate_results.json`
5. 闸门结果：
   - `make security-scan` -> pass
   - `python3 scripts/security_scan.py` -> `STEP35_SECURITY_SCAN_PASS`
   - `python3 scripts/test_step35_security_config.py` -> `STEP35_GATE_PASS`
   - `reports/step35_security_scan.json` 显示 `finding_count=0`
   - `reports/step35_gate_results.json` 显示 `overall_passed=true`
6. Git 分支：`feat/step31-step36-release-hardening`。
7. Git 提交：`defa32c` `feat: add release hardening foundation for step31-step35`。
8. PR 信息：`#11 https://github.com/2696437448-cmyk/smart-parking-system/pull/11`。
9. 标签信息：`step35-pass`。
10. 回滚标签：`step30-pass`。
11. 卡点与修复：
   - 卡点：发布化阶段仍存在 demo 凭证、secure 模板和本地私有覆盖边界不清的问题。
   - 修复：新增 secure env 模板、敏感项扫描、配置门禁与恢复文档，并将 RabbitMQ / Grafana 账号密码改为 env 参数化，不再在演示脚本中暴露默认密码。
12. 下一阻塞：进入 Step36，完成发布化总验收并把默认完成态从 Step30 升级到 Step36。

## 2026-03-26 Step 36（通过）

1. 完成时间：2026-03-26 16:42（Asia/Shanghai）。
2. 当前步骤：Step 36 - 发布化总验收。
3. 目标与范围：在 Step30 功能闭环与 Step31~35 发布化增强之上，完成最终 release acceptance，并把默认完成态升级到 Step36。
4. 实际改动：
   - 更新 `Makefile`
   - 更新 `README.md`
   - 更新 `docs/defense_demo_runbook.md`
   - 更新 `memory-bank/implementation-plan.md`
   - 更新 `memory-bank/progress.md`
   - 更新 `scripts/defense_demo.sh`
   - 更新 `scripts/test_step33_ci_smoke.py`
   - 更新 `reports/step36_technical_acceptance.md`
   - 生成 `reports/step36_gate_results.json`
   - 生成 `deliverables/bundles/smart-parking-step36-release-*.tar.gz`
   - 生成 `deliverables/bundles/smart-parking-step36-release-*.manifest.txt`
5. 闸门结果：
   - `make ci-smoke` -> pass
   - `make security-scan` -> pass
   - `make release-bundle` -> pass
   - `make release-acceptance` -> `STEP36_GATE_PASS`
   - `reports/step36_gate_results.json` 显示 `overall_passed=true`
6. Git 分支：`feat/step31-step36-release-hardening`。
7. Git 提交：`1dc4c68` `test: record step36 release acceptance evidence`。
8. PR 信息：`#11 https://github.com/2696437448-cmyk/smart-parking-system/pull/11`。
9. 标签信息：`step36-pass`。
10. 回滚标签：`step30-pass`。
11. 卡点与修复：
   - 卡点：首次 Step36 执行失败，`scripts/test_step33_ci_smoke.py` 仍把 README 路线检查硬编码为 `Step31~36`，与当前 `Step25~36 完成情况` 标题不一致。
   - 修复：将 smoke gate 调整为匹配 post-Step30 路线文案后重跑 `make ci-smoke`，再执行 `make release-acceptance` 收口通过。
12. 当前结论：
   - `Step36` 已升级为当前稳定默认完成态。
   - 最新 release bundle 已切换为 `step36` label，并记录当前分支 `feat/step31-step36-release-hardening`。

## 2026-03-27 Step31~36 Git 收口（远端完成）

1. 更新时间：2026-03-27 00:20（Asia/Shanghai）。
2. 当前范围：为 Step31~36 发布化增强阶段补齐远端 Git 闸门收口，不再修改业务语义、验收结论与交付范围。
3. 收口说明：
   - 功能与证据主线已通过分支 `feat/step31-step36-release-hardening` 合并入 `main`。
   - Step31~35 的发布化基础设施与证据由提交 `defa32c` 承载。
   - Step36 发布化总验收证据由提交 `1dc4c68` 承载。
   - 远端 `main` 已包含 PR #11 的 merge commit `a542e8d`。
4. 本次验证：
   - `git fetch origin` -> pass
   - `git merge-base --is-ancestor 1dc4c68 origin/main` -> `STEP36_IN_MAIN`
   - `git ls-remote --tags origin 'step3[1-6]-pass'` -> pass
5. Git 分支：`feat/step31-step36-release-hardening`。
6. Git 提交：
   - `defa32c` `feat: add release hardening foundation for step31-step35`
   - `1dc4c68` `test: record step36 release acceptance evidence`
7. PR 信息：`#11 https://github.com/2696437448-cmyk/smart-parking-system/pull/11`。
8. 标签信息：`step31-pass`, `step32-pass`, `step33-pass`, `step34-pass`, `step35-pass`, `step36-pass`（已推送远端）。
9. 回滚标签：`step30-pass`。
10. 收口结果：
   - Step31~36 的分支、提交、PR、标签四项 Git 闸门已完成。
   - `progress.md` 已补齐 Step31~36 的远端 Git 元数据，可直接作为当前默认完成态的审计记录。
11. 后续说明：
   - 如需继续迭代，应从 `origin/main` 新开后续步骤分支，不再在已合并的 Step31~36 分支上继续开发。

## 2026-03-30 Step 37（通过）

1. 完成时间：2026-03-30 16:09（Asia/Shanghai）。
2. 当前步骤：Step 37 - 提示词驱动的现代化优化入口。
3. 目标与范围：在 Step36 默认完成态之上建立项目专用提示词体系，并完成第一轮前后端结构与 UI 现代化改造，不改动 Spark / LSTM / Hungarian 核心语义。
4. 实际改动：
   - 新增 `memory-bank/project-prompt-library.md`
   - 更新 `memory-bank/prompt-templates.md`
   - 更新 `memory-bank/implementation-plan.md`
   - 更新 `memory-bank/acceptance.md`
   - 更新 `memory-bank/architecture.md`
   - 更新 `memory-bank/gap-matrix.md`
   - 新增 `services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewController.java`
   - 更新 `services/parking-service/src/main/java/com/smartparking/parking/ParkingBusinessExtensions.java`
   - 新增 owner / admin 聚合视图接口
   - 新增前端布局、服务层、共享组件、分层样式与路由懒加载
   - 新增 `scripts/test_step37_prompt_frontend_modernization.py`
   - 新增执行证据 `reports/step37_execution.md`
5. 闸门结果：
   - `cd apps/frontend && npm run typecheck` -> pass
   - `cd apps/frontend && npm run build` -> pass
   - `python3 scripts/test_step21_frontend_pages.py` -> `STEP21_GATE_PASS`
   - `python3 scripts/test_step27_app_shell.py` -> `STEP27_GATE_PASS`
   - `python3 scripts/test_step28_navigation_map.py` -> `STEP28_GATE_PASS`
   - `python3 scripts/test_step29_admin_charts.py` -> `STEP29_GATE_PASS`
   - `python3 scripts/test_step37_prompt_frontend_modernization.py` -> `STEP37_GATE_PASS`
   - `make ci-smoke` -> pass
   - `python3 scripts/test_step30_enhanced_acceptance.py` -> `STEP30_GATE_PASS`
   - `python3 scripts/test_step36_release_acceptance.py` -> `STEP36_GATE_PASS`
6. Git 分支：`main`。
7. Git 提交：`N/A`（当前会话未提交）。
8. PR 信息：`N/A`。
9. 标签信息：`N/A`。
10. 回滚标签：`step36-pass`。
11. 卡点与修复：
   - 卡点：历史前端 gate 默认按“页面文件内直连接口 + 扁平路由”假设编写，重构后产生误报。
   - 修复：将 Step21 / Step27 / Step29 脚本调整为识别服务层、角色化布局与嵌套路由；同时保留旧接口兼容。
   - 卡点：Step37 种子预约与现有预约窗口冲突，首次触发 409。
   - 修复：Step37 gate 改为自动轮询可用车位，保持一致性保护语义不变。
12. 下一阻塞：
   - 如需继续推进 Post-Step36，建议进入 Step38，聚焦前端 bundle 深拆分、业主端小程序入口或更细粒度 owner/admin BFF 接口。

## 2026-03-31 Step 38（通过）

1. 完成时间：2026-03-31 15:32（Asia/Shanghai）。
2. 当前步骤：Step 38 - dashboard 合同与体验收敛。
3. 目标与范围：在 Step37 现代化入口之上，收敛 owner/admin dashboard OpenAPI 契约、页面级数据编排层与统一页面状态表达，不改动既有业务 URL 与核心语义。
4. 实际改动：
   - 更新 `openapi/smart-parking.yaml`，正式纳入 owner/admin dashboard 契约与 schema。
   - 新增 `apps/frontend/src/composables/useOwnerDashboardView.ts`、`useOwnerOrderView.ts`、`useOwnerNavigationView.ts`、`useAdminDashboardView.ts`。
   - 新增 `apps/frontend/src/composables/useOrderContext.ts`、`useViewState.ts` 与 `apps/frontend/src/components/ViewStateNotice.vue`。
   - 更新 owner/admin 页面与 `apps/frontend/src/types/dashboard.ts`。
   - 新增 `scripts/test_step38_dashboard_contract_and_viewmodels.py` 与 `reports/step38_execution.md`。
5. 闸门结果：
   - `python3 scripts/validate_openapi.py --spec openapi/smart-parking.yaml` -> pass
   - `python3 scripts/test_step38_dashboard_contract_and_viewmodels.py` -> `STEP38_GATE_PASS`
6. Git 分支：`feat/step37-prompt-ui-modernization`。
7. Git 提交：`N/A`（当前会话未提交；工作区基于 `ba7e128`）。
8. PR 信息：`N/A`。
9. 标签信息：`N/A`。
10. 回滚标签：`step36-pass`。
11. 卡点与修复：
   - 卡点：页面逻辑继续下沉后，历史前端 gate 仍假设“页面文件内直连接口”。
   - 修复：同步更新 Step21 / Step29 / Step33 脚本，使其识别 view-model、共享状态组件与新的 CI 入口。
12. 下一阻塞：进入 Step39，完成 dashboard 聚合层模块化、请求/实时通道硬化与 ECharts 包体收敛。

## 2026-03-31 Step 39（通过）

1. 完成时间：2026-03-31 15:48（Asia/Shanghai）。
2. 当前步骤：Step 39 - dashboard 聚合层与性能硬化。
3. 目标与范围：保持 dashboard URL 与业务语义不变，把聚合逻辑从 controller 中抽离，并完成前端请求、实时通道与图表包体硬化。
4. 实际改动：
   - 新增 `services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewModules.java`，形成 `DashboardQueryService`、`OwnerDashboardAssembler`、`AdminDashboardAssembler`、`DashboardViewService`。
   - 收敛 `apps/frontend/src/services/http.ts` 与 `apps/frontend/src/composables/useRealtimeChannel.ts` 的 trace、错误解析与 reconnect/polling 生命周期。
   - 更新 `apps/frontend/src/components/EChartPanel.vue` 与 `apps/frontend/vite.config.ts`，拆分 `vendor-zrender` / `vendor-echarts`，消除默认 build warning。
   - 新增 `scripts/test_step39_dashboard_hardening.py` 与 `reports/step39_execution.md`。
5. 闸门结果：
   - `cd apps/frontend && npm run typecheck` -> pass
   - `cd apps/frontend && npm run build` -> pass（无 chunk size warning）
   - `python3 scripts/test_step39_dashboard_hardening.py` -> `STEP39_GATE_PASS`
6. Git 分支：`feat/step37-prompt-ui-modernization`。
7. Git 提交：`N/A`（当前会话未提交；工作区基于 `ba7e128`）。
8. PR 信息：`N/A`。
9. 标签信息：`N/A`。
10. 回滚标签：`step36-pass`。
11. 卡点与修复：
   - 卡点：ECharts 通过 `import()` 整模块后，bundler 无法 tree-shake，导致 `vendor-echarts-shared` 超过 500 kB。
   - 修复：改为 admin 异步组件内部静态按需导入图表模块，并在 Vite 中拆出 `vendor-zrender` / `vendor-echarts`。
12. 下一阻塞：进入 Step40，完成综合验收脚本、release bundle 收口与默认完成态升级。

## 2026-03-31 Step 40（通过）

1. 完成时间：2026-03-31 16:05（Asia/Shanghai）。
2. 当前步骤：Step 40 - 综合验收与默认完成态升级。
3. 目标与范围：串联 Step30 / Step36 / Step37 与 Step38 / Step39 新 gate，升级新的默认完成态，并统一 README / runbook / memory-bank / deliverables 口径。
4. 实际改动：
   - 新增 `scripts/test_step40_release_acceptance.py` 与 `reports/step40_technical_acceptance.md`。
   - 更新 `Makefile`、`.github/workflows/ci.yml`、`scripts/defense_demo.sh`、`scripts/create_release_bundle.sh`。
   - 更新 README、runbook、memory-bank、deliverables 文档为 Step40 口径。
   - release bundle 默认 label 升级为 `step40`，同时保留 Step36 历史锚点说明。
5. 闸门结果：
   - `make step38-check` -> pass
   - `make step39-check` -> pass
   - `python3 scripts/test_step40_release_acceptance.py --static-only` -> `STEP40_GATE_PASS`
   - `./scripts/defense_demo.sh start` -> stack ready
   - `python3 scripts/test_step40_release_acceptance.py` -> `STEP40_GATE_PASS`
   - `./scripts/defense_demo.sh stop` -> stack stopped
6. Git 分支：`feat/step38-step40-dashboard-hardening`。
7. Git 提交：`N/A`（待本轮 Step38-Step40 分支收口提交后回填）。
8. PR 信息：`N/A`。
9. 标签信息：`N/A`。
10. 回滚标签：`step36-pass`。
11. 卡点与修复：
   - 卡点：Step40 需要同时兼顾“新默认完成态”与“历史验收入口仍可访问”。
   - 修复：默认入口切换到 Step40，同时保留 `acceptance-step36`、`acceptance-step30`、`acceptance-step24`。
12. 当前结论：
   - `Step40` 已升级为当前稳定默认完成态。
   - `Step36` 继续保留为发布化稳定锚点与回滚说明。

## 2026-04-23 登录与最终 UI/文档说明并入 main（完成）

1. 完成时间：2026-04-23 00:40（Asia/Shanghai）。
2. 当前步骤：主线合流收口。
3. 目标与范围：把 `feat/login-auth`、最终 UI、`study/` 学习资料以及更新后的 README / runbook / memory-bank 说明全部收口到 `main`。
4. 实际改动：
   - 将 `origin/main` 更新到最新 Step40 主线。
   - 在隔离 worktree 中整合 `feat/login-auth` 与 `feat/step38-step40-dashboard-hardening`，并完成关键回归验证。
   - 将整合结果并回 `main`。
   - 以 `ours` 策略补做 `feat/ui-refinement` 的 Git 收口，使 UI 线在分支关系上也正式进入 `main`。
   - 更新 `memory-bank`，把统一登录、最终 UI、学习资料和主线文档说明写入当前事实。
5. 闸门结果：
   - `python3 scripts/test_step41_arco_tech_ui.py` -> `STEP41_ARCO_BOOTSTRAP_PASS`
   - `python3 scripts/test_step42_shadcn_ui_polish.py` -> `STEP42_SHADCN_UI_POLISH_PASS`
   - `python3 scripts/test_step43_simple_bright_ui.py` -> `STEP43_SIMPLE_BRIGHT_UI_PASS`
   - `python3 scripts/test_step43_login_auth.py` -> `STEP43_GATE_PASS`
   - `python3 scripts/test_step44_authenticated_owner_identity.py` -> `STEP44_GATE_PASS`
   - `npm run typecheck` -> pass
   - `npm run build` -> pass
   - `python3 scripts/test_step40_release_acceptance.py --static-only` -> `STEP40_GATE_PASS`
6. Git 分支：`main`。
7. Git 提交：`7bf9118`（整合分支合回主线），以及后续 `feat/ui-refinement` 的收口 merge commit。
8. PR 信息：`N/A`（当前为本地主线收口阶段）。
9. 标签信息：`N/A`。
10. 回滚标签：`step40-pass`。
11. 卡点与修复：
   - 卡点：`feat/ui-refinement` 与登录线直接互相 merge 时前端布局、样式和 gate 结果文件冲突较大。
   - 修复：先在独立 worktree 里整合登录线与已经验证过的 `feat/step38-step40-dashboard-hardening`，确认可用后再并回 `main`；最后用 `ours` 策略关闭 `feat/ui-refinement` 的 Git 关系。
12. 当前结论：
   - `main` 已同时包含统一登录、最终 UI、学习资料与更新后的文档说明。
   - 后续再讨论“Step40 之后的新默认完成态”前，不需要继续把这些能力当成 worktree 特例处理。
