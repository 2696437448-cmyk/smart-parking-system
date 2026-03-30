# 技术验收清单（Step36 默认完成态）

## 1. 当前默认验收基线

1. 当前默认稳定完成态为 `Step36`。
2. 历史基线：
   - `Step30`：功能与增强交付基线
   - `Step24`：原始题目主链基线
3. Step36 验收必须同时满足“Step30 历史功能基线保持通过 + Step33/35/34 发布化增强通过”。

## 2. Step24 基线继续要求

1. 业主可携带幂等头创建预约。
2. 物业管理员可手动触发调度任务。
3. 系统可返回预测结果与调度结果。
4. 业主端页面可展示推荐、预约结果、账单与导航。
5. 物业端页面可展示资源监控与日/区域收益统计。
6. 并发预约测试：无超卖、无重复扣费。
7. 模型服务宕机测试：触发降级并返回可解释字段。
8. MQ 故障测试：重试后进入 DLQ 且可追踪。
9. WebSocket 断连测试：自动切换轮询并继续更新。
10. 订单重复完成测试：不重复结算、不重复确认收益。

## 3. Step25 文档收敛验收

1. `progress.md`、`implementation-plan.md`、`gap-matrix.md`、`architecture.md`、`acceptance.md`、README、runbook 口径一致。
2. 不再出现“Step24 已完成”与“Step24 待完成”并存的文档冲突。
3. Step30 已被标记为当前稳定默认完成态。
4. Step24 已降级为历史主链基线说明，而非默认完成态。

## 4. Step26 数据接入与分析增强验收

1. 存在 raw ingest 接口：`sensor-events`、`lpr-events`、`resident-patterns`。
2. MySQL raw 表可接收并保存三类近真实数据。
3. ETL 可从 raw 表跑到 `forecast_feature_table` 与 `dispatch_input_table`。
4. ETL 额外产出占用热度、车辆流向、业主出行高峰摘要。
5. 严格验收时质量报告显示 `engine=spark`。
6. 明文车牌不得落库。

## 5. Step27 App 壳层验收

1. 前端依赖中存在 Capacitor。
2. 存在 Capacitor 配置与 Android 壳层。
3. 业主端具备移动优先布局、底部导航、订单/账单卡片化展示。
4. 同一套 API 同时服务 Web 与 App 壳层。
5. `npm run typecheck`、`npm run build`、Capacitor 壳层检查通过。

## 6. Step28 地图导航增强验收

1. 导航页可展示页面内地图预览。
2. 响应继续兼容 `map_url + eta_minutes + destination`。
3. 响应新增 `region_label`、`slot_display_name`、`route_summary` 等兼容字段。
4. 页面可展示 ETA、目标车位、路线摘要、地图跳转按钮。
5. 外部地图跳转仍可作为 fallback 使用。

## 7. Step29 物业图表化验收

1. 物业端业务页面存在收益趋势图。
2. 物业端业务页面存在区域收益对比图。
3. 物业端业务页面存在占用率趋势图。
4. 物业端业务页面存在预测值 vs 实际值对照图。
5. 图表数据可回溯到 `billing_records`、收益汇总或 ETL/预测输出。
6. Grafana 仍保留为技术诊断视图，不混充业务图表页。

## 8. Step30 增强验收收口（已完成）

1. Step24 原全量回归已继续通过。
2. Step26~29 新增验收已全部通过。
3. 已形成新的增强版技术验收报告与 machine-readable gate results。
4. README / runbook / memory-bank 默认完成态已升级到 Step30。

## 9. Step31 路线收敛验收（已完成）

1. `implementation-plan.md` 已追加 Step31~36。
2. `gap-matrix.md` 已区分“Step30 当前完成态”和“Post-Step30 发布化缺口”。
3. `acceptance.md`、`architecture.md`、README、runbook 对下一阶段表述一致。
4. 未提前把默认完成态从 Step30 升级到未验收的新阶段。

## 10. Step32 环境基线验收（已完成）

1. 根目录存在 `.env.example`。
2. 前端环境模板已包含 `VITE_GATEWAY_BASE_URL`、`VITE_REALTIME_WS_URL`、`VITE_GATEWAY_POLL_URL`。
3. 存在 `scripts/preflight_check.sh`，可在启动前执行本地检查。
4. `scripts/defense_demo.sh` 支持 `preflight` 子命令，`start` 默认先做检查。
5. 根目录存在 `Makefile`，统一常用演示与验收命令。
6. `infra/docker-compose.yml` 允许关键环境变量通过 `.env` 覆盖。
7. `scripts/preflight_check.sh --static` 或 `make preflight-static` 可在无 Docker daemon 环境下完成静态校验。

## 11. Step33 CI 与回归自动化验收（已完成）

1. 存在 `.github/workflows/ci.yml`。
2. CI 至少覆盖 `make ci-smoke`、OpenAPI 校验、前端 `typecheck`、前端 `build`。
3. 存在 `scripts/test_step33_ci_smoke.py` 作为轻量 smoke gate。
4. 本地可运行 `make ci-smoke` 与 CI 入口保持一致。
5. Step30 gate report 仍保持 `overall_passed=true`，未因 CI 引入退化。

## 12. Step34 发布包与交付物验收（已完成）

1. 存在 `scripts/create_release_bundle.sh`。
2. 存在 `make release-bundle` 入口。
3. 存在 `deliverables/README.md` 与 `bundles/`、`screenshots/`、`recordings/` 目录规范。
4. 本地可生成版本化交付包 tar.gz。
5. 交付包至少包含 README、runbook、OpenAPI、关键脚本、memory-bank 核心文档与 Step30/31/32/33 关键证据。

## 13. Step35 安全与配置硬化验收（已完成）

1. 存在 `.env.secure.example`。
2. 存在 `scripts/security_scan.py` 与 `scripts/test_step35_security_config.py`。
3. 存在 `docs/security_hardening.md`，覆盖配置分层、凭证轮换与恢复建议。
4. `make security-scan` 可通过。
5. demo 默认值与 secure 模板已明确分层，`defense_demo.sh` 不再直接打印默认密码。

## 14. Step36 发布化总验收（已完成）

1. Step30 历史功能基线报告仍保持 `overall_passed=true`。
2. `make ci-smoke` 通过。
3. `make security-scan` 通过。
4. `make release-bundle` 通过。
5. 存在最新 bundle 与 sidecar manifest。
6. `reports/step36_gate_results.json` 显示 `overall_passed=true`。
7. README / runbook / memory-bank 默认完成态已升级到 Step36。

## 15. Git 管理验收

1. 仓库可 clone 并读取完整项目文档、执行脚本与增强阶段材料。
2. 每步继续满足 `branch created`、`commit exists`、`PR merged`、`tag created`。
3. `progress.md` 继续记录 `branch`、`commit_id`、`PR链接/编号`、`tag`、`rollback_tag`。

## 16. Step37 提示词体系与前后端现代化验收（已完成）

1. 存在 `memory-bank/project-prompt-library.md`，且包含 Product / Data Science / AI / Algorithm / Frontend / UI / Backend 六个方向。
2. 每个提示词章节均包含 `When to use`、`Read first`、`Project constraints`、`Expected output`、`Common anti-patterns`、`Repo-specific checklist`。
3. `memory-bank/prompt-templates.md` 已明确要求结构优化、UI 改版、接口重构、性能优化、规划类任务先读取新提示词库。
4. 前端已拆分为角色化布局，Owner / Admin 不再共用单一演示壳。
5. 前端已引入统一 API 访问层与页面级数据模块，不再由主要页面直接管理全部请求细节。
6. 样式体系已从单一大样式表重构为分层样式入口。
7. 路由已改为按页懒加载，Admin 图表页与导航页的重依赖不再全部进入首屏主包。
8. 后端新增 owner / admin 视图聚合接口，但旧接口继续兼容。
9. `scripts/test_step37_prompt_frontend_modernization.py` 可通过。
