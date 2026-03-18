# 🚗 Smart Parking System（智慧社区停车调度系统）

> 基于微服务架构的高并发智慧停车系统，融合 Spark ETL、轻量 LSTM 预测、确定性 Hungarian 调度、共享计费与多页面业务前端，实现车位资源的动态优化配置。

[![Java](https://img.shields.io/badge/Java-17-orange.svg)](https://openjdk.org/projects/jdk/17/)
[![Python](https://img.shields.io/badge/Python-3.11-green.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.x-brightgreen.svg)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)

## 📌 当前状态

本项目默认完成态已经从 **Step18 工程基线** 升级为 **Step24 业务闭环验收**：

1. Step18：保留为历史工程基线证据。
2. Step24：作为默认全量验收入口，覆盖 Spark strict、真实 Hungarian、共享计费、收益统计、前端页面化交付与演示入口一致性。
3. 默认业务入口：
   - 业主端：`http://localhost:4173/owner/dashboard`
   - 物业端：`http://localhost:4173/admin/monitor`

## 📖 项目简介

本项目聚焦社区停车场“找位难、调度乱、共享计费难落地、超卖风险高”的实际痛点。
系统采用 **Java + Python + Vue3** 混合微服务架构，通过：

1. Spark ETL 融合 IoT 车位传感器、车辆进出事件、业主出行规律数据；
2. 轻量 LSTM 预测供需缺口；
3. 确定性 Hungarian 算法进行全局匹配；
4. 一致性三重防护（幂等 + 分布式锁 + DB 唯一约束）保障高并发稳定性；
5. 共享计费、收益统计和地图导航补齐完整业务闭环。

## 🎯 已实现核心目标

1. **并发一致性**：并发预约场景实现“零超卖、零重复有效写入”。
2. **高可用降级**：模型服务故障时自动降级，接口保持可解释可用。
3. **数据工程主链**：ETL 支持 Spark strict 验收，不再以 Python fallback 冒充通过。
4. **算法可复现**：调度优化输出对同输入稳定一致，不依赖随机 `hash()`。
5. **业务闭环**：预约、预估计费、订单结算、收益汇总、导航引导完整打通。
6. **页面化交付**：业主端与物业端页面均可访问，不再只依赖技术看板演示。
7. **可观测性**：Prometheus + Grafana 三视图与结构化日志。

## 🏗️ 技术架构

### 1. 服务拓扑

| 服务名称 | 技术栈 | 职责描述 |
| :--- | :--- | :--- |
| **Gateway Service** | Java (Spring Cloud Gateway + Resilience4j) | 路由转发、TraceID 透传、熔断、降级、CORS 放行 |
| **Parking Service** | Java (Spring Boot) | 预约主链、共享计费、账单与收益统计、导航目标生成 |
| **Model Service** | Python 3.11 | 供需预测（LSTM-Lite）、调度优化（Hungarian）、模型版本激活/回滚 |
| **Realtime Service** | Python 3.11 | WebSocket 实时状态推送 |
| **Frontend** | Vue3 + TypeScript + Pinia + Vue Router | 业主端 / 物业端业务页面、实时状态、账单与导航展示 |

### 2. 中间件与基础设施

- **MySQL 8**：预约、账单、收益明细
- **Redis 7**：幂等键、缓存与分布式锁协同
- **RabbitMQ**：异步调度、重试与 DLQ
- **Prometheus + Grafana**：指标采集与三视图监控
- **Docker Compose**：单机可复现编排

## ⚡ 技术亮点

### 🔒 并发一致性（防超卖三重保护）

1. **Idempotency-Key**：请求幂等，重复请求返回同一结果。  
2. **Redisson Lock**：细粒度锁控制同车位同时间窗竞争。  
3. **MySQL Unique Constraint**：数据库层最终兜底，阻断重复有效写入。

### 🧠 数据与算法主链

1. **Spark Strict ETL**：验收必须显示 `engine=spark`。  
2. **LSTM-Lite**：轻量训练与供需预测。  
3. **Deterministic Hungarian**：确定性最优匹配，结果可复现。  
4. **模型管理**：版本注册、激活、回滚，支持在线切换。

### 💸 共享计费与收益统计

1. **规则引擎 V1**：按 `region + 时间桶 + 时长` 计算金额。  
2. **计费冻结语义**：`Asia/Shanghai`、15 分钟计费块、向上取整。  
3. **收益汇总**：支持按日 / 区域回溯到账单明细。

### 🗺️ 页面化业务交付

1. **业主端**：推荐车位、预约结果、账单详情、导航引导。  
2. **物业端**：资源监控、调度摘要、日收益 / 区域收益统计。  
3. **技术视图分离**：Grafana / RabbitMQ 仅作诊断，不再冒充业务页面。

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

### 6. 运行默认全量验收（Step24）

```bash
./scripts/defense_demo.sh acceptance
# 或
python3 scripts/test_step24_full_acceptance.py
```

### 7. 运行历史工程基线验收（Step18 Legacy）

```bash
python3 scripts/test_step18_full_acceptance.py
```

## 🖥️ 前端本地开发

```bash
cd apps/frontend
npm install
npm run dev
```

默认地址：`http://localhost:5173`

## 📚 项目展示与答辩材料

1. 项目展示手册：`docs/defense_demo_runbook.md`
2. 论文证据包：`reports/thesis_evidence_package.md`
3. Step18 基线验收：`reports/step18_technical_acceptance.md`
4. Step24 全量验收：`reports/step24_technical_acceptance.md`（Step24 默认口径）

## 🛣️ 路线图说明

1. Step18 是工程基线，不再作为默认完成态。  
2. Step19A~24 用于把项目从“工程化 demo”补齐到“原始题目需求完整闭环”。  
3. 后续优化主要聚焦压测矩阵、页面打磨和论文展示质量，而不是改动冻结业务语义。
