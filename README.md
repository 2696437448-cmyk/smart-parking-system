# 🚗 Smart Parking System（智慧社区停车调度系统）

> 基于微服务架构的高并发智慧停车系统，融合 Spark ETL、轻量 LSTM 预测、确定性 Hungarian 调度、共享计费、多页面业务前端、Capacitor App 壳层、地图导航与物业经营图表，实现车位资源的动态优化配置。

[![Java](https://img.shields.io/badge/Java-17-orange.svg)](https://openjdk.org/projects/jdk/17/)
[![Python](https://img.shields.io/badge/Python-3.11-green.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.x-brightgreen.svg)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)

## 📌 当前状态

1. 当前稳定默认完成态：`Step30`。
2. 含义：主链需求与增强交付均已验收通过，覆盖 Spark strict、确定性 Hungarian、共享计费、收益统计、业主端/物业端业务页面、近真实 raw ingest、Capacitor App 壳层、地图预览、物业端图表与增强验收收口。
3. 历史稳定基线：`Step24`。
4. 含义：Step24 继续作为“主链已闭环”的保留基线；Step30 在其之上完成成品增强并升级为新的默认完成态。
5. 当前默认业务入口：
   - 业主端：`http://localhost:4173/owner/dashboard`
   - 物业端：`http://localhost:4173/admin/monitor`

## 📖 项目简介

本项目聚焦社区停车场“找位难、调度乱、共享计费难落地、超卖风险高”的实际痛点。系统采用 **Java + Python + Vue3** 混合微服务架构，通过：

1. Spark ETL 融合 IoT 车位传感器、车辆进出事件、业主出行规律数据；
2. 轻量 LSTM 预测供需缺口；
3. 确定性 Hungarian 算法进行全局匹配；
4. 一致性三重防护（幂等 + 分布式锁 + DB 唯一约束）保障高并发稳定性；
5. 共享计费、收益统计、地图导航、App 壳层与图表化物业端补齐完整业务闭环。

## 🎯 Step30 默认完成态

1. **并发一致性**：并发预约场景实现“零超卖、零重复有效写入”。
2. **高可用降级**：模型服务故障时自动降级，接口保持可解释可用。
3. **数据工程主链**：ETL 支持 Spark strict 验收，不再以 Python fallback 冒充通过。
4. **算法可复现**：调度优化输出对同输入稳定一致，不依赖随机 `hash()`。
5. **业务闭环**：预约、预估计费、订单结算、收益汇总、导航引导完整打通。
6. **近真实数据接入**：raw ingest 已覆盖 `sensor_event_raw`、`lpr_event_raw`、`resident_trip_raw`，并可产出区域热度、车辆流向、出行高峰摘要。
7. **跨端交付**：前端已具备 `Vue + Capacitor` Android 壳层与移动优先业主端页面。
8. **地图导航增强**：导航页支持 Leaflet + OpenStreetMap 页面内地图预览，并保留外部地图 fallback。
9. **物业图表化**：收益趋势、区域对比、占用率趋势、预测对照图全部进入物业业务页。
10. **增强验收收口**：Step24 基线与 Step26~29 增强闸门已统一通过，默认完成态已升级到 Step30。

## 🧭 Step25~30 完成情况

1. Step25：文档与完成态口径收敛，统一了 memory-bank / README / runbook / script 口径。
2. Step26：近真实 raw ingest 与 Spark 关联分析增强完成。
3. Step27：`Vue + Capacitor` App 壳层与移动优先业主端完成。
4. Step28：Leaflet + OpenStreetMap 页面内地图预览导航完成。
5. Step29：ECharts 物业端图表化展示完成。
6. Step30：增强验收与答辩材料升级完成，并成为新的默认完成态。

## 🏗️ 技术架构

| 服务名称 | 技术栈 | 职责描述 |
| :--- | :--- | :--- |
| **Gateway Service** | Java (Spring Cloud Gateway + Resilience4j) | 路由转发、TraceID 透传、熔断、降级、CORS 放行 |
| **Parking Service** | Java (Spring Boot) | 预约主链、共享计费、账单、收益统计、导航与 raw ingest |
| **Model Service** | Python 3.11 | 供需预测（LSTM-Lite）、调度优化（Hungarian）、模型版本激活/回滚 |
| **Realtime Service** | Python 3.11 | WebSocket 实时状态推送 |
| **Frontend** | Vue3 + TypeScript + Pinia + Vue Router + Leaflet + ECharts + Capacitor | 业主端 / 物业端业务页面、地图、图表与 App 壳层 |

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

### 2. 安装 Python 依赖

```bash
python3 -m pip install -r requirements-dev.txt
```

### 3. 安装前端依赖

```bash
cd apps/frontend
npm install
cd ../..
```

### 4. 启动演示环境

```bash
./scripts/defense_demo.sh start
```

### 5. 打开业务页面

1. 业主端：`http://localhost:4173/owner/dashboard`
2. 物业端：`http://localhost:4173/admin/monitor`

### 6. 运行当前默认全量验收（Step30）

```bash
./scripts/defense_demo.sh acceptance
# 或
python3 scripts/test_step30_enhanced_acceptance.py
```

### 7. 如需回看 Step24 基线验收

```bash
./scripts/defense_demo.sh acceptance-step24
# 或
python3 scripts/test_step24_full_acceptance.py
```

## 📚 项目展示与答辩材料

1. 项目展示手册：`docs/defense_demo_runbook.md`
2. 论文证据包：`reports/thesis_evidence_package.md`
3. Step30 增强验收：`reports/step30_technical_acceptance.md`
4. Step24 历史基线验收：`reports/step24_technical_acceptance.md`
5. 执行计划与历史路线：`memory-bank/implementation-plan.md`

## 🛣️ 路线图说明

1. `Step30` 是当前稳定默认完成态。
2. `Step24` 保留为主链闭环的历史稳定基线。
3. 后续如继续迭代，应在 Step30 之上进入新的增强步骤，而不是回退到 Step24 之前的口径。
