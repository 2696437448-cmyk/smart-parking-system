# 实施计划（执行单元）

默认单步粒度为 0.5~1 天，每步必须包含测试与回滚策略。

## 规划护栏

1. 算法核心或跨服务集成步骤，统一预留 1.5 倍缓冲。
2. 每步编码前必须明确“可能卡点”。
3. 未完成 Step 0 数据基线，禁止进入后续开发。
4. 已通过闸门不可回退；每步完成后必须做回归抽查。
5. Git 闸门强制执行：`branch created`、`commit exists`、`PR merged`、`tag created`。
6. Step 18 仅定义为“工程化基线完成态”；对齐最初题目需求的最终态从 Step19A 开始继续推进。

## 全步骤通用 Git 闸门（强制）

1. 每步必须在独立分支执行：`feat/stepNN-*`。
2. 每步至少 2 次提交（代码 + 证据文档）。
3. 每步必须通过 PR 合并到 `main`。
4. 每步必须打 `stepNN-pass` 标签。
5. 任一 Git 闸门未过，本步视为失败，禁止进入下一步。

## Step 0 - 数据健康基线

- 目标：在编码前确认数据可用性。
- 输入：数据源与 `data-spec.md`。
- 输出：健康报告（空值率、重复率、schema 偏差、时间连续性）。
- 测试：脚本成功运行并生成报告。
- 回滚：数据不可用时切换 fallback 样例集。

## Step 1 - 仓库骨架搭建

- 目标：建立单仓结构与本地运行基线。
- 输入：`prd.md`, `tech-stack.md`。
- 输出：gateway/parking/model/frontend/infra 目录。
- 测试：`docker compose config` 通过。
- 回滚：回退骨架目录变更。

## Step 2 - 接口合同冻结

- 目标：冻结核心请求/响应 schema 和公共头。
- 输入：PRD 与验收标准。
- 输出：OpenAPI 文档与共享 DTO 说明。
- 测试：合同校验脚本通过。
- 回滚：回退 OpenAPI 版本。

## Step 3 - 网关基线

- 目标：完成 trace 透传与基础路由。
- 输入：Step 2 冻结合同。
- 输出：owner/admin/model 路由连通。
- 测试：本地 compose 转发与健康检查通过。
- 回滚：临时改为直连后端。

## Step 4 - 预约一致性核心

- 目标：实现幂等 + 锁 + 唯一约束，防超卖。
- 输入：预约接口合同。
- 输出：并发下无重复有效预约。
- 测试：并发脚本验证。
- 回滚：保留幂等 + DB 唯一兜底。

## Step 5 - 模型服务核心

- 目标：实现轻量 LSTM 预测与匈牙利调度接口。
- 输入：特征 schema 与调度 schema。
- 输出：`/predict` 与 `/optimize` 稳定返回。
- 测试：输出形状、字段、有效性测试通过。
- 回滚：保留同 schema 的基线模型路径。

## Step 6 - 跨服务容错

- 目标：Java -> Python 调用具备超时/熔断/降级语义。
- 输入：模型服务联调路径。
- 输出：降级响应含 `fallback_reason`/`fallback_strategy`。
- 测试：停模型服务后业务仍可解释可用。
- 回滚：临时退化为超时捕获。

## Step 7 - MQ 可靠性

- 目标：异步调度链路具备重试与 DLQ。
- 输入：admin 调度触发接口。
- 输出：交换机、队列、DLQ 与幂等消费。
- 测试：强制消费失败并验证 DLQ。
- 回滚：特性开关切回同步路径。

## Step 8 - 实时通道

- 目标：WebSocket 主通道 + 轮询兜底。
- 输入：物业看板实时需求。
- 输出：前端可显示 `realtime/degraded` 状态。
- 测试：停 ws 服务后自动切轮询。
- 回滚：保留轮询单通道。

## Step 9 - 可观测性基线

- 目标：指标、看板、结构化日志闭环。
- 输入：各服务 metrics 端点。
- 输出：Prometheus + Grafana 三段式可展示视图。
- 测试：故障注入前后指标状态转移正确。
- 回滚：保留 Prometheus 抓取与原始日志。

## Step 10 - 技术总验收

- 目标：串行执行全部验收场景并归档证据。
- 输入：`acceptance.md` 清单。
- 输出：技术验收报告、关键截图与复现命令。
- 测试：验收项通过率达到要求。
- 回滚：定位失败步骤并定向重开。

## Step G0 - Git Onboarding & Baseline Sync

- 目标：建立项目 Git 管理基线并完成远端同步。
- 输入：当前项目目录与目标仓库地址。
- 输出：`main` 分支基线提交、远端 `origin`、`step10-pass-baseline` 标签。
- 测试：`git status` 干净、`git remote -v` 正确、`git tag` 含基线标签。
- Git 闸门：`branch created`、`commit exists`、`PR merged`、`tag created`。
- 失败回滚：`main` 推送失败时切换 `migration/full-import` 分支 + PR，禁止强推覆盖。

## Step 11 - 数据工程补齐（PySpark ETL）

- 目标：实现多源数据对齐并产出统一特征表。
- 输入：`slot_status`、`vehicle_event`、`resident_pattern` 与外部公开数据子集。
- 输出：`forecast_feature_table`、`dispatch_input_table`、ETL 质量报告。
- 测试：字段完整、时间对齐、空值与重复率达标；fallback 双路径可运行。
- Git 闸门：`branch created`、`commit exists`、`PR merged`、`tag created`。
- 回滚：保留 Step 0 fallback 数据与最小 ETL 规则，先恢复可复现性。

## Step 12 - 模型训练补齐（LSTM + 基线对比）

- 目标：形成可复现训练与评估流程。
- 输入：Step 11 特征表。
- 输出：LSTM 训练脚本与权重、基线模型脚本、统一指标对比表（MAE/RMSE/MAPE）。
- 测试：训练可复现，指标结果可追踪，推理接口字段保持合同一致。
- Git 闸门：`branch created`、`commit exists`、`PR merged`、`tag created`。
- 回滚：保留上一个稳定模型版本与基线模型推理路径。

## Step 13 - 模型工程化（注册与热切换）

- 目标：模型版本可管理、可激活、可回滚。
- 输入：Step 12 训练产物。
- 输出：模型注册表、版本激活接口增强、在线热切换机制。
- 测试：激活后新请求命中新版本；回滚可在不重启服务情况下恢复。
- Git 闸门：`branch created`、`commit exists`、`PR merged`、`tag created`。
- 回滚：回退到最近稳定 `model_version` 并锁定激活接口。

## Step 14 - 业务后端对齐（Java + MySQL/Redis/Redisson）

- 目标：对齐技术定稿中的 Java 主业务服务。
- 输入：当前 `parking-service` 业务语义与合同。
- 输出：Java `parking-service`，一致性主链路为 Redis 幂等 + Redisson 锁 + MySQL 唯一约束。
- 测试：并发预约零超卖、幂等命中可追踪、写路径不再依赖内存幂等。
- Git 闸门：`branch created`、`commit exists`、`PR merged`、`tag created`。
- 回滚：保留 Python 服务作为短期兜底分支，按合同切换路由。

## Step 15 - 网关治理对齐（Spring Cloud Gateway + Resilience4j）

- 目标：对齐网关治理能力并固化降级语义。
- 输入：当前路由与降级字段约定。
- 输出：支持超时、熔断、降级策略的网关实现。
- 测试：停 model-service 触发熔断与降级，响应含 `fallback_reason/fallback_strategy/trace_id`。
- Git 闸门：`branch created`、`commit exists`、`PR merged`、`tag created`。
- 回滚：回退到当前可用网关实现并保留降级契约。

## Step 16 - 前端工程化（Vue3 + TS + Pinia）

- 目标：从演示页升级为工程化前端项目。
- 输入：现有实时演示逻辑与接口合同。
- 输出：业主端与物业端基础页面、状态管理与通道状态展示。
- 测试：WebSocket 正常显示 realtime；故障后自动 degraded 并轮询更新。
- Git 闸门：`branch created`、`commit exists`、`PR merged`、`tag created`。
- 回滚：保留当前 `realtime_dashboard_demo.html` 作为演示保底。

## Step 17 - 可观测性与性能证据补齐

- 目标：形成可答辩的性能与可观测性定量证据。
- 输入：服务指标、日志与压测脚本。
- 输出：Prometheus/Grafana 三视图、JMeter/k6 对比报告（P95/P99/错误率/吞吐）。
- 测试：正常态/故障态/恢复态三段演示可复现；压测结果可重复运行。
- Git 闸门：`branch created`、`commit exists`、`PR merged`、`tag created`。
- 回滚：保留 Step 9 基线看板与最小指标集。

## Step 18 - 全量验收与论文证据收口（工程基线）

- 目标：完成“原闸门 + 定稿对齐闸门”第一阶段验收。
- 输入：Step 11~17 产物与 `acceptance.md`。
- 输出：技术验收报告、论文证据包、答辩脚本。
- 测试：Step 4~10 全回归通过 + Step11~17 闸门通过。
- Git 闸门：`branch created`、`commit exists`、`PR merged`、`tag created`。
- 回滚：按失败项定位回退到最近稳定步骤，禁止跨步修复。

## Step 19A - Spark Strict 与依赖基线收敛

- 目标：将 ETL 验收口径从“Spark 优先”升级为“Spark strict 必过”。
- 输入：Step 11 ETL 脚本、`requirements-dev.txt`、OpenAPI 校验脚本。
- 输出：统一 Python 依赖、严格 Spark 验收脚本、`engine=spark` 质量报告。
- 测试：`step11_etl.py --engine spark` 成功；`validate_openapi.py` 依赖齐全；质量报告显示 `engine=spark`。
- Git 闸门：`branch created`、`commit exists`、`PR merged`、`tag created`。
- 回滚：仅保留开发态 `auto/fallback`，验收态不降级。

## Step 19B - 调度算法纠偏（确定性真实 Hungarian）

- 目标：移除随机 cost 与伪 Hungarian，实现可复现的最优匹配。
- 输入：`model-service` 优化接口、Step 5 合同。
- 输出：确定性 cost matrix、真实 Hungarian 求解、对照校验脚本。
- 测试：同输入多次输出一致；小样本与 brute-force 最优一致；中大样本不退化为贪心。
- Git 闸门：`branch created`、`commit exists`、`PR merged`、`tag created`。
- 回滚：仅允许回退到上一稳定确定性实现，禁止退回随机 hash 路径。

## Step 20 - 共享计费主链补齐

- 目标：完成预约、预估、结算、账单的业务闭环。
- 输入：预约接口、计费规则冻结口径。
- 输出：`billing_records`、预估金额返回、订单完成结算接口。
- 测试：同一订单可追踪 `estimate -> final bill -> recognized revenue`；重复完成请求不重复记账。
- Git 闸门：`branch created`、`commit exists`、`PR merged`、`tag created`。
- 回滚：回退新增账单接口与表结构，不影响预约主链。

## Step 21 - 业主端 / 物业端页面化交付

- 目标：将现有单页实时看板升级为多页面业务前端。
- 输入：Vue3 工程、冻结 API、静态地理目录。
- 输出：`vue-router`、业主页、物业页、导航页、账单视图。
- 测试：页面路由可访问；业主可预约/查看账单/查看导航；物业可查看监控与收益。
- Git 闸门：`branch created`、`commit exists`、`PR merged`、`tag created`。
- 回滚：保留 Step16 实时看板能力与单页入口。

## Step 22 - 收益统计与业务监控收口

- 目标：完成物业收益与区域统计，不再只展示系统指标。
- 输入：`billing_records`、实时状态接口、区域维度。
- 输出：按日/区域收益汇总接口与业务监控视图。
- 测试：汇总结果可回溯到账单明细；业务视图与技术看板口径分离。
- Git 闸门：`branch created`、`commit exists`、`PR merged`、`tag created`。
- 回滚：保留账单明细能力，临时关闭汇总接口。

## Step 23 - 演示入口升级

- 目标：`defense_demo.sh start` 直接输出本项目业务页面入口。
- 输入：前端 build/preview、compose 栈、答辩 runbook。
- 输出：脚本自动启动前端预览并打印 owner/admin 业务 URL，RabbitMQ/Grafana 仅作诊断地址。
- 测试：一条命令后首屏落到业务页面而非 `15672`；README/runbook/脚本输出一致。
- Git 闸门：`branch created`、`commit exists`、`PR merged`、`tag created`。
- 回滚：保留现有后端栈启动，但必须继续给出业务前端补充启动说明。

## Step 24 - 新默认全量验收

- 目标：以最初题目需求为准完成新的最终态验收。
- 输入：Step18 基线 + Step19A~23 新增能力。
- 输出：`Step24` 全量验收报告、业务页面演示手册、更新后的 README 默认入口。
- 测试：旧 Step18 回归通过；新增 Spark strict / Hungarian / billing / frontend / demo entry 全通过。
- Git 闸门：`branch created`、`commit exists`、`PR merged`、`tag created`。
- 回滚：保留 Step18 作为历史证据，但默认入口不再回退。
