# 🚗 Smart Parking System（智慧社区停车调度系统）

> 基于微服务架构的高并发智慧停车系统，融合 Spark ETL、轻量 LSTM 预测、确定性 Hungarian 调度、共享计费、多页面业务前端、Capacitor App 壳层、地图导航与物业经营图表，实现车位资源的动态优化配置。

[![Java](https://img.shields.io/badge/Java-17-orange.svg)](https://openjdk.org/projects/jdk/17/)
[![Python](https://img.shields.io/badge/Python-3.11-green.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.x-brightgreen.svg)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)

## 📌 当前状态

1. 当前稳定默认完成态：`Step40`。
2. 含义：在 `Step36` 发布化稳定基线与 `Step37` 现代化起点之上，完成 Step38 合同与体验收敛、Step39 dashboard 聚合层与性能硬化、Step40 综合验收与默认完成态升级。
3. 历史稳定基线：
   - `Step36`：发布化稳定锚点与默认回滚参考
   - `Step30`：功能与增强交付基线
   - `Step24`：原始题目主链闭环基线
4. 当前默认业务入口：
   - 统一登录：`http://localhost:4173/login`
   - 登录后按角色自动跳转到业主端或物业端

## 📖 项目简介

本项目聚焦社区停车场“找位难、调度乱、共享计费难落地、超卖风险高”的实际痛点。系统采用 **Java + Python + Vue3** 混合微服务架构，通过：

1. Spark ETL 融合 IoT 车位传感器、车辆进出事件、业主出行规律数据。
2. 轻量 LSTM 预测供需缺口。
3. 确定性 Hungarian 算法进行全局匹配。
4. 一致性三重防护（幂等 + 分布式锁 + DB 唯一约束）保障高并发稳定性。
5. 共享计费、收益统计、地图导航、App 壳层、dashboard 聚合接口与图表化物业端补齐完整业务闭环。

## 📘 学习资料

如需面向代码小白按阶段学习当前 `Step40` 主线，可直接阅读 [`study/README.md`](study/README.md)。  
这里提供了一套中文 `8 周学习包`，覆盖系统全景、前端、网关、Java 业务主链、模型与 ETL、验收与小改动路径。

## 🎯 Step40 默认完成态

1. `Step21 / Step27 / Step28 / Step29 / Step30 / Step36 / Step37` 已通过行为保持兼容，不因新优化线而退化。
2. `/api/v1/owner/dashboard` 与 `/api/v1/admin/dashboard` 已正式纳入 `openapi/smart-parking.yaml`，合同覆盖查询参数、`summary/highlights/sections`、`billing_rule`、`latest_order`、`diagnostic_links`、`degraded_metadata`、`trace_id`、`service`。
3. 前端页面逻辑已从路由页继续下沉到页面级数据编排层：`useOwnerDashboardView`、`useOwnerOrderView`、`useOwnerNavigationView`、`useAdminDashboardView`。
4. Owner/Admin 页面统一使用 `ViewStateNotice + useViewState` 表达 `loading / error / empty / degraded / stale`，不再各写一套页面状态分支。
5. Owner 推荐、订单、导航页面共享 `useOrderContext` 的订单恢复策略、动作禁用策略与错误回退策略。
6. `parking-service` 已把 dashboard 组装逻辑从 controller 抽离到 `ParkingDashboardViewModules.java`，形成 query / assembler / view service 分层。
7. 前端 `requestJson` 与实时通道已完成硬化，统一非 JSON 错误处理、trace 透传、轮询与 reconnect 生命周期。
8. Admin 图表仅在经营页按需加载；`npm run build` 不再出现 ECharts chunk size warning。
9. Makefile 与 GitHub Actions 已纳入 `make step38-check`、`make step39-check`、`make step40-check`。
10. 默认验收入口已升级为 `Step40`，同时保留 `Step36 / Step30 / Step24` 历史验收入口。

## 🧭 Step25~40 完成情况

1. Step25：文档与完成态口径收敛，统一 memory-bank / README / runbook / script 口径。
2. Step26：近真实 raw ingest 与 Spark 关联分析增强完成。
3. Step27：`Vue + Capacitor` App 壳层与移动优先业主端完成。
4. Step28：Leaflet + OpenStreetMap 页面内地图预览导航完成。
5. Step29：ECharts 物业端图表化展示完成。
6. Step30：增强验收与答辩材料升级完成，并成为新的默认完成态。
7. Step31：Post-Step30 路线收敛完成。
8. Step32：环境模板、preflight 与统一命令入口完成。
9. Step33：CI 与最小自动回归完成。
10. Step34：release bundle 与交付目录完成。
11. Step35：安全与配置硬化完成。
12. Step36：发布化总验收完成，并升级为稳定默认完成态。
13. Step37：提示词体系、角色化布局、聚合接口与第一轮现代化改造完成。
14. Step38：dashboard OpenAPI 契约、页面级 view-model 与统一页面状态表达完成。
15. Step39：dashboard 聚合层模块化、HTTP/实时通道硬化、ECharts 包体优化完成。
16. Step40：综合验收、默认完成态升级、Step40 报告与 release bundle 收口完成。

## 🏗️ 技术架构

| 服务名称 | 技术栈 | 职责描述 |
| :--- | :--- | :--- |
| **Gateway Service** | Java (Spring Cloud Gateway + Resilience4j) | 路由转发、TraceID 透传、熔断、降级、CORS 放行 |
| **Parking Service** | Java (Spring Boot) | 预约主链、共享计费、账单、收益统计、导航、dashboard 聚合与 raw ingest |
| **Model Service** | Python 3.11 | 供需预测（LSTM-Lite）、调度优化（Hungarian）、模型版本激活/回滚 |
| **Realtime Service** | Python 3.11 | WebSocket 实时状态推送与降级伴生能力 |
| **Frontend** | Vue3 + TypeScript + Pinia + Vue Router + Leaflet + ECharts + Capacitor | 业主端 / 物业端业务页面、地图、图表、view-model、App 壳层 |

## 🚀 快速开始

### 环境要求

1. Docker + Docker Compose v2+
2. Python 3.11+
3. Node.js 20+

### 1. 克隆项目

```bash
git clone https://github.com/2696437448-cmyk/smart-parking-system.git
cd smart-parking-system
```

### 2. 准备环境模板

```bash
cp .env.example .env
cp apps/frontend/.env.example apps/frontend/.env.local
```

如需更安全的起点，可改用：

```bash
cp .env.secure.example .env
cp apps/frontend/.env.example apps/frontend/.env.local
```

### 3. 安装依赖

```bash
python3 -m pip install -r requirements-dev.txt
cd apps/frontend
npm install
cd ../..
```

### 4. 启动演示环境

```bash
./scripts/defense_demo.sh preflight
make preflight-static
./scripts/defense_demo.sh start
```

### 5. 打开业务页面

1. 统一登录：`http://localhost:4173/login`
2. 业主演示账号：`owner_demo / demo123`
3. 物业演示账号：`admin_demo / admin123`
4. 登录后会自动跳转到业主端或物业端首页

### 6. 运行当前默认验收（Step40）

```bash
./scripts/defense_demo.sh acceptance
# 或
make acceptance
# 或
make release-acceptance
# 或
python3 scripts/test_step40_release_acceptance.py
```

### 7. 运行 Step38 / Step39 增量 gate

```bash
make step38-check
make step39-check
make step40-check
```

### 8. 如需回看 Step36 / Step30 / Step24 历史验收

```bash
./scripts/defense_demo.sh acceptance-step36
make acceptance-step36
python3 scripts/test_step36_release_acceptance.py

./scripts/defense_demo.sh acceptance-step30
make acceptance-step30
python3 scripts/test_step30_enhanced_acceptance.py

./scripts/defense_demo.sh acceptance-step24
make acceptance-step24
python3 scripts/test_step24_full_acceptance.py
```

### 9. 运行本地最小回归（对齐 Step33 CI）

```bash
make ci-smoke
cd apps/frontend && npm run typecheck && npm run build
```

### 10. 生成交付包

```bash
make release-bundle
```

生成物默认输出到 `deliverables/bundles/`，默认 label 为 `step40`。

### 11. 运行安全扫描与配置硬化检查

```bash
make security-scan
```

## 📚 项目展示与答辩材料

1. 项目展示手册：`docs/defense_demo_runbook.md`
2. 论文证据包：`reports/thesis_evidence_package.md`
3. Step40 综合验收：`reports/step40_technical_acceptance.md`
4. Step39 执行报告：`reports/step39_execution.md`
5. Step38 执行报告：`reports/step38_execution.md`
6. Step36 发布化总验收：`reports/step36_technical_acceptance.md`
7. Step30 增强验收：`reports/step30_technical_acceptance.md`
8. 执行计划与历史路线：`memory-bank/implementation-plan.md`
9. 交付物目录说明：`deliverables/README.md`
10. 安全与配置硬化说明：`docs/security_hardening.md`

## 🛣️ 路线图说明

1. `Step40` 是当前稳定默认完成态。
2. `Step36` 继续保留为发布化稳定锚点与默认回滚参考。
3. `Step30` 保留为功能与增强交付基线。
4. `Step24` 保留为原始题目主链闭环基线。
5. 后续迭代应继续建立在 `Step40` 之上，优先 additive change，而不是回退到 `Step36 / Step30 / Step24` 之前的口径。
