# 架构说明（Step40 默认完成态）

## 1. 当前稳定架构（Step40）

1. `gateway-service`：Spring Cloud Gateway + Resilience4j，负责统一路由、trace 透传、超时熔断、降级兜底与 CORS。
2. `parking-service`：Java 主业务服务，负责预约一致性、共享计费、账单、收益统计、导航目标生成、业务监控、dashboard 聚合与 raw ingest 接入。
3. `model-service`：Python 算法服务，负责预测、优化、模型激活与版本管理。
4. `realtime-service`：WebSocket 实时推送与实时状态伴生服务。
5. `frontend-app`：Vue3 + TypeScript + Pinia + Vue Router + Leaflet + ECharts + Capacitor，交付业主端与物业端业务页面。

## 2. 主数据流

1. `sensor_event_raw / lpr_event_raw / resident_trip_raw` -> Step11/26 ETL -> `forecast_feature_table`、`dispatch_input_table`。
2. ETL 继续产出区域占用热度摘要、车辆流入流出摘要、业主出行高峰摘要。
3. 业主预约请求 -> Gateway -> `parking-service` 一致性主链（Redis 幂等 / Redisson 锁 / MySQL 唯一约束）。
4. `parking-service` 基于计费规则生成预估金额，并写入 `billing_records`。
5. 订单完成 -> `parking-service` 确认最终账单与收益。
6. `billing_records` -> 日收益 / 区域收益汇总 -> 物业业务图表与 dashboard 聚合接口。
7. `forecast_feature_table` / 预测输出 -> 占用率趋势与预测对照图表。
8. 业主端默认走 Gateway HTTP API；实时状态优先 WebSocket，故障时回退 Polling。

## 3. 导航与地理链路

1. `geo_catalog` 是固定地理目录，按 `region_id/slot_id` 存储 `lat/lng/display_name/map_label`。
2. 导航接口继续兼容旧字段：`map_url + eta_minutes + destination`。
3. 增强阶段新增兼容字段：`region_label`、`slot_display_name`、`route_summary`。
4. 页面内地图固定采用 `Leaflet + OpenStreetMap`，外部地图跳转作为 fallback。

## 4. 业务视图与技术视图分层

1. 统一入口：`/login`，按角色进入业主端或物业端业务页面。
2. 业主端业务视图：`首页 / 订单 / 导航` 三段式结构，桌面端左侧导航，移动端底部切换，覆盖推荐、预约、结算与导航。
3. 物业端业务视图：物业监管总览页，集中展示经营摘要、运行状态、收益趋势、区域对比、占用率趋势与降级提示。
4. 技术视图：Prometheus / Grafana / RabbitMQ，只用于诊断，不作为默认展示入口。

## 5. Step37 提示词驱动现代化层

1. Step37 为 Step36 之后的现代化入口，补齐项目专用 prompt library，并完成角色化布局、服务层与聚合接口首轮升级。
2. `memory-bank/project-prompt-library.md` 统一 Product / Data Science / AI / Algorithm / Frontend / UI / Backend 六类任务约束与输出格式。
3. Step37 保持 Step36 核心业务、可靠性、地图与计费语义不变。

## 6. 前端页面编排层

1. Owner 页面采用 `useOwnerDashboardView`、`useOwnerOrderView`、`useOwnerNavigationView` 负责数据编排、动作触发与错误恢复。
2. Admin 页面采用 `useAdminDashboardView` 负责 dashboard 聚合接口消费、实时状态联动与图表数据转换。
3. `useOrderContext` 负责 owner 推荐、订单、导航页的订单上下文恢复与 URL 持久化。
4. `useViewState + ViewStateNotice` 统一页面状态表达：`loading / ready / empty / error / degraded / stale`。

## 7. dashboard 合同与聚合接口

1. `GET /api/v1/owner/dashboard`：聚合推荐、计费规则、最近订单与旅程摘要。
2. `GET /api/v1/admin/dashboard`：聚合经营摘要、highlights、趋势 sections、诊断链接与降级元数据。
3. 两个 dashboard 接口均返回顶层 `trace_id` 与 `service`。
4. 历史 owner/admin 细粒度接口仍保留给旧脚本与兼容调用使用。

## 8. 性能与加载策略

1. 路由继续按页懒加载，Owner 与 Admin 分开加载。
2. `AdminMonitor` 通过异步组件按需加载 `EChartPanel`。
3. ECharts 仅在 admin 路由需要时进入 chunk；`vendor-zrender` 与 `vendor-echarts` 已拆分，默认构建无 chunk warning。
4. `requestJson` 统一解析 trace header、非 JSON 响应与 HTTP 错误；`useRealtimeChannel` 收敛 reconnect / polling 生命周期。

### 登录与最终 UI 合流状态

1. `feat/login-auth` 已并入 `main`，统一登录、JWT、角色跳转与会话状态已成为主线事实。
2. `feat/ui-refinement` 的最终页面结构、亮色 UI、`study/` 学习资料与演示文档已通过整合分支吸收到 `main`，并已补做 Git 合流收口。
3. 当前主线不再需要单独依赖 worktree 解释登录或最终 UI 状态，README / runbook / memory-bank 应统一按主线现状表述。

## 9. 默认完成态与历史基线

1. 当前默认完成态：`Step40`。
2. 发布化稳定锚点：`Step36`。
3. 历史功能基线：`Step30`。
4. 历史主链基线：`Step24`。
5. 后续迭代必须建立在 Step40 之上，不再回退到 Step36 / Step30 / Step24 之前的口径。

## 10. Step38 合同与体验收敛层

1. 把 dashboard OpenAPI 合同、前端 page-level view-model 与统一页面状态表达收敛为同一层。
2. Owner/Admin 页面不再在路由页内直接拼接口，而是通过 composable 复用统一状态语义。
3. 这一层解决的是“接口能否被稳定解释”和“业务旅程是否连续”的问题。

## 11. Step39 聚合层与性能硬化

1. `ParkingDashboardViewController.java` 只保留 HTTP 入口与 trace 封装。
2. `ParkingDashboardViewModules.java` 拆分 `DashboardQueryService`、`OwnerDashboardAssembler`、`AdminDashboardAssembler`、`DashboardViewService`。
3. 前端完成请求错误统一、实时通道生命周期硬化与图表 chunk 优化。
4. 这一层解决的是“controller 膨胀”和“admin 图表加载成本”的问题。

### Post-Step40 已落地主线增强

1. 登录能力已补齐：统一登录页、鉴权路由、owner/admin 会话状态与退出登录流程已经进入主线。
2. 最终 UI 已补齐：亮色令牌、Owner 左侧导航、物业监管总览、一屏指标与中文化文案已进入主线。
3. 学习资料已补齐：`study/` 目录已经进入主线，可作为 README 之外的结构化学习入口。
4. 这些增强当前仍建立在 Step40 默认完成态之上，属于 additive merge，不改变 Step40 作为默认验收入口的事实。

## 12. 默认完成态升级规则

1. 当前默认完成态已升级为 `Step40`。
2. `Step36` 继续保留为默认回滚锚点说明。
3. 若未来继续升级默认完成态，必须在 Step40 基线之上新增新的总验收步骤，并保持 additive change。
