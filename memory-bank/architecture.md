# 架构说明（Step36 默认完成态）

## 1. 当前稳定架构（Step36）

1. `gateway-service`：Spring Cloud Gateway + Resilience4j，负责统一路由、trace 透传、超时熔断、降级兜底与 CORS。
2. `parking-service`：Java 主业务服务，负责预约一致性、共享计费、账单、收益统计、导航目标生成、业务监控与 raw ingest 接入。
3. `model-service`：Python 算法服务，负责预测、优化、模型激活与版本管理。
4. `realtime-service`：WebSocket 实时推送与实时状态伴生服务。
5. `frontend-app`：Vue3 + TypeScript + Pinia + Vue Router + Leaflet + ECharts + Capacitor，交付业主端与物业端业务页面。

## 2. Step25~30 已完成增强

1. Step25：完成文档与完成态口径收敛。
2. Step26：完成 raw ingest 层与 Spark 关联分析增强，不新增微服务。
3. Step27：完成 Vue 前端内的 Capacitor Android 壳层与移动优先业主端交付。
4. Step28：完成 Leaflet + OpenStreetMap 页面内地图预览导航。
5. Step29：完成物业页 ECharts 图表化展示。
6. Step30：完成增强版验收与答辩材料收口。

## 3. 主数据流

1. `sensor_event_raw / lpr_event_raw / resident_trip_raw` -> Step11/26 ETL -> `forecast_feature_table`、`dispatch_input_table`。
2. ETL 继续产出区域占用热度摘要、车辆流入流出摘要、业主出行高峰摘要。
3. 业主预约请求 -> Gateway -> `parking-service` 一致性主链（Redis 幂等 / Redisson 锁 / MySQL 唯一约束）。
4. `parking-service` 基于计费规则生成预估金额，并写入 `billing_records`。
5. 订单完成 -> `parking-service` 确认最终账单与收益。
6. `billing_records` -> 日收益 / 区域收益汇总 -> 物业业务图表。
7. `forecast_feature_table` / 预测输出 -> 占用率趋势与预测对照图表。
8. 业主端默认走 Gateway HTTP API；实时状态优先 WebSocket，故障时回退 Polling。

## 4. 导航与地理链路

1. `geo_catalog` 是固定地理目录，按 `region_id/slot_id` 存储 `lat/lng/display_name/map_label`。
2. 导航接口继续兼容旧字段：`map_url + eta_minutes + destination`。
3. 增强阶段新增兼容字段：`region_label`、`slot_display_name`、`route_summary`。
4. 页面内地图固定采用 `Leaflet + OpenStreetMap`，外部地图跳转作为 fallback。

## 5. 业务视图与技术视图分层

1. 业主端业务视图：推荐、预约、订单/账单、导航、App 壳层。
2. 物业端业务视图：资源摘要、收益趋势、区域对比、占用率趋势、预测对照。
3. 技术视图：Prometheus / Grafana / RabbitMQ，只用于诊断，不作为默认展示入口。

## 6. 默认完成态与历史基线

1. 当前默认完成态：`Step36`。
2. 历史功能基线：`Step30`。
3. 历史主链基线：`Step24`。
4. 后续迭代必须建立在 Step36 之上，不再回退到 Step30 / Step24 之前的口径。

## 7. 冻结决策

1. 仍维持“3 核心服务 + 1 实时伴生服务 + 1 前端”的结构。
2. 仍冻结 `UPSTREAM_CONNECT_TIMEOUT_MS=10000`、`UPSTREAM_TIMEOUT_MS=2500`。
3. 仍冻结计费语义：`Asia/Shanghai`、`15 分钟一个计费块`、`不足一个计费块向上取整`。
4. 仍冻结地图策略：免费栈 `Leaflet + OpenStreetMap`，不接入付费地图 SDK。

## 8. Post-Step30 发布化增强层

1. Step31：负责把 Post-Step30 路线、缺口与验收目标固化进文档系统。
2. Step32：负责根目录 `.env.example`、preflight 脚本、`Makefile` 与 `defense_demo.sh preflight` 入口。
3. Step33：负责 CI 层，已通过 `.github/workflows/ci.yml`、`make ci-smoke` 和 Step33 smoke gate 将关键闸门自动化。
4. Step34：负责 release bundle 与交付资产目录，已通过 `scripts/create_release_bundle.sh` 与 `deliverables/` 目录规范落地。
5. Step35：负责安全与配置硬化，已通过 `.env.secure.example`、security scan 与恢复文档收口。
6. Step36：负责新的发布化总验收，已将默认完成态从 Step30 升级到 Step36。

## 9. 默认完成态升级规则

1. 当前默认完成态已升级为 `Step36`。
2. `Step30` 继续保留为功能与增强交付基线。
3. 后续若继续升级默认完成态，必须在 Step36 基线之上新增新的总验收步骤。
