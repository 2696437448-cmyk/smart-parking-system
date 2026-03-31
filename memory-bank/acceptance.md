# 技术验收清单（Step40 默认完成态）

## 1. 当前默认验收基线

1. 当前默认稳定完成态为 `Step40`。
2. 历史基线：
   - `Step36`：发布化稳定锚点
   - `Step30`：功能与增强交付基线
   - `Step24`：原始题目主链基线
3. Step40 验收必须同时满足“Step36 发布化稳定性保持通过 + Step37 现代化能力保持通过 + Step38/39 新 gate 通过”。

## 2. 历史主链继续要求

1. 业主可携带幂等头创建预约。
2. 物业管理员可手动触发调度任务。
3. 系统可返回预测结果与调度结果。
4. 业主端页面可展示推荐、预约结果、账单与导航。
5. 物业端页面可展示资源监控与日/区域收益统计。
6. 并发预约测试无超卖、无重复扣费。
7. 模型服务宕机测试触发降级并返回可解释字段。
8. MQ 故障测试重试后进入 DLQ 且可追踪。
9. WebSocket 断连测试可自动切换轮询并继续更新。
10. 订单重复完成测试不重复结算、不重复确认收益。

## 3. Step30 / Step36 / Step37 历史增强继续要求

1. Step30 原增强验收仍保持 `overall_passed=true`。
2. Step36 发布化总验收仍可通过，且可继续生成 release bundle。
3. Step37 提示词文档、角色化布局、聚合接口与前端现代化入口仍可通过。
4. 默认验收升级到 Step40 后，不删除 Step36 / Step30 / Step24 的历史验收入口。

## 4. Step38 dashboard 合同与体验收敛要求

1. `openapi/smart-parking.yaml` 包含 `/api/v1/owner/dashboard` 与 `/api/v1/admin/dashboard`。
2. owner/admin dashboard schema 覆盖 `summary/highlights/sections`、`billing_rule`、`latest_order`、`diagnostic_links`、`degraded_metadata`、`trace_id`、`service`。
3. 前端存在页面级数据编排层：owner dashboard、owner order、owner navigation、admin dashboard。
4. Owner/Admin 页面统一表达 `loading / error / empty / degraded / stale`。
5. `scripts/test_step38_dashboard_contract_and_viewmodels.py` 可通过。

## 5. Step39 dashboard 聚合层与性能硬化要求

1. dashboard URL 与业务语义保持不变，但组装逻辑已抽离为独立 query / assembler / view service。
2. `requestJson` 对非 JSON 错误响应、trace 透传与错误对象统一处理。
3. `useRealtimeChannel` 已收敛 reconnect / polling 生命周期，避免重复轮询。
4. `npm run build` 不再出现 ECharts 500 kB chunk warning。
5. 若本地 runtime 可用，owner/admin dashboard 聚合接口 smoke 可返回 200 与顶层 `trace_id/service`。
6. `scripts/test_step39_dashboard_hardening.py` 可通过。

## 6. Step40 综合验收升级要求

1. 默认验收入口升级为 `python3 scripts/test_step40_release_acceptance.py` 与 `./scripts/defense_demo.sh acceptance`。
2. README / runbook / memory-bank / deliverables 口径已统一到 Step40。
3. `reports/step40_technical_acceptance.md` 与 `reports/step40_gate_results.json` 已生成。
4. 最新 release bundle 默认 label 为 `step40`，并包含 Step38/39/40 脚本、报告与文档。
5. `step36-pass` 继续保留为回滚锚点说明，直到下一轮更高等级验收替代。

## 7. 历史阶段验收摘要（已完成）

1. Step25：文档与完成态口径收敛。
2. Step26：raw ingest 与 Spark 分析增强。
3. Step27：App 壳层与移动优先业主端。
4. Step28：地图导航增强。
5. Step29：物业图表化。
6. Step30：增强验收收口。
7. Step31：路线收敛。
8. Step32：环境基线。
9. Step33：CI 与回归自动化。
10. Step34：发布包与交付物。
11. Step35：安全与配置硬化。
12. Step36：发布化总验收。
13. Step37：提示词体系与前后端现代化入口。

## 8. Git 管理验收

1. 仓库可 clone 并读取完整项目文档、执行脚本与增强阶段材料。
2. 每步继续满足 `branch created`、`commit exists`、`PR merged`、`tag created`。
3. `progress.md` 继续记录 `branch`、`commit_id`、`PR链接/编号`、`tag`、`rollback_tag`。

## 17. Step38 dashboard 合同与 view-model 验收（已完成）

1. dashboard OpenAPI 契约已正式收口。
2. 前端存在 owner/admin 页面级 view-model 与共享状态表达能力。
3. `scripts/test_step38_dashboard_contract_and_viewmodels.py` 通过。
4. 执行证据：`reports/step38_execution.md`、`reports/step38_gate_results.json`。

## 18. Step39 dashboard 硬化验收（已完成）

1. `ParkingDashboardViewModules.java` 完成聚合层拆分。
2. `requestJson` 与 `useRealtimeChannel` 完成统一硬化。
3. 前端 build 无 ECharts chunk warning。
4. `scripts/test_step39_dashboard_hardening.py` 通过。
5. 执行证据：`reports/step39_execution.md`、`reports/step39_gate_results.json`。

## 19. Step40 综合验收（已完成）

1. Step30 报告仍保持 `overall_passed=true`。
2. Step36 发布化总验收仍可通过。
3. Step37 现代化入口能力继续保留。
4. Step38 / Step39 新 gate 通过。
5. 最新 bundle 为 `step40` label。
6. README / runbook / memory-bank / deliverables 默认完成态已升级到 Step40。
7. `reports/step40_gate_results.json` 显示 `overall_passed=true` 后，Step40 成为新的默认完成态。
