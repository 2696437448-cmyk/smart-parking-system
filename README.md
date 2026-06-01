# 智慧社区停车调度系统

> 一个面向社区停车场景的智慧停车项目，提供统一登录、车位预约、共享计费、地图导航、运营看板、实时监控与智能调度能力。

[![Java](https://img.shields.io/badge/Java-17-orange.svg)](https://openjdk.org/projects/jdk/17/)
[![Python](https://img.shields.io/badge/Python-3.11-green.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3-brightgreen.svg)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue.svg)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)

## 项目简介

本项目聚焦社区停车场景中的预约冲突、车位供需不均、收费流程割裂和运营分析不足等问题，采用 `Java + Python + Vue` 的混合微服务架构，打通业主预约、订单结算、地图导航、物业经营分析和智能调度全链路。

项目适合用于以下场景：

- 智慧停车 / 智慧社区类课程设计、毕业设计或演示项目
- 微服务、前后端分离、实时数据展示类综合项目实践
- 停车调度、车位推荐、运营数据看板方向的系统原型

## 核心功能

- 统一登录与角色识别：支持业主端、物业端登录和基于 JWT 的身份识别。
- 业主端业务闭环：支持车位推荐、预约下单、订单查询、费用结算和地图导航。
- 物业端运营看板：支持收益趋势、区域占用率、预测对比、实时状态和诊断信息展示。
- 智能调度与预测：结合 Spark ETL、LSTM-Lite 预测和 Hungarian 优化算法完成供需分析与调度分配。
- 工程化交付：内置 OpenAPI 契约、Trace ID 透传、自动化验收脚本、预检脚本和发布打包流程。

## 技术栈

### 后端

- Java 17
- Spring Boot 3
- Spring Cloud Gateway
- Resilience4j
- JDBC
- MySQL
- Redis / Redisson
- JWT

### 前端

- Vue 3
- TypeScript
- Pinia
- Vue Router
- Arco Design Vue
- ECharts
- Leaflet
- Capacitor

### 算法与服务

- Python 3.11
- Spark ETL
- LSTM-Lite
- Hungarian 调度算法
- WebSocket 实时推送

### 工程与部署

- Docker / Docker Compose
- Makefile
- GitHub Actions
- OpenAPI

## 系统架构

| 模块 | 技术实现 | 主要职责 |
| :--- | :--- | :--- |
| Gateway Service | Spring Boot 3 + Spring Cloud Gateway + JWT | 统一鉴权、请求转发、CORS、熔断、链路追踪 |
| Parking Service | Spring Boot 3 + JDBC + MySQL + Redis | 预约主链、共享计费、订单结算、导航与物业经营接口 |
| Model Service | Python 3.11 | 供需预测、调度优化、模型版本切换与回滚 |
| Realtime Service | Python 3.11 + WebSocket | 实时状态推送、轮询降级与监控指标输出 |
| Frontend | Vue 3 + TypeScript + ECharts + Leaflet | 业主端与物业端页面、地图导航、经营图表与交互展示 |

## 仓库结构

```text
apps/frontend/                前端工程
services/gateway-service/     网关与鉴权服务
services/parking-service/     停车核心业务服务
services/*.py                 模型服务、实时服务与辅助服务
scripts/                      自动化验收、预检与发布脚本
openapi/                      API 契约定义
infra/                        监控与基础设施配置
config/                       环境配置模板
deliverables/                 交付产物与打包结果
docs/                         运行、安全与演示说明文档
```

## 快速开始

### 环境要求

- Java 17+
- Python 3.11+
- Node.js 20+
- Docker / Docker Compose v2+

### 1. 克隆仓库

```bash
git clone https://github.com/2696437448-cmyk/smart-parking-system.git
cd smart-parking-system
```

### 2. 初始化环境

```bash
cp .env.example .env
cp apps/frontend/.env.example apps/frontend/.env.local
python3 -m pip install -r requirements-dev.txt
cd apps/frontend && npm install && cd ../..
```

如果你希望使用更安全的默认模板，可以将 `.env.example` 替换为 `.env.secure.example`。

### 3. 启动演示环境

```bash
./scripts/defense_demo.sh preflight
make preflight-static
./scripts/defense_demo.sh start
```

### 4. 打开系统

- 登录入口：`http://localhost:4173/login`
- 业主演示账号：`owner_demo / demo123`
- 物业演示账号：`admin_demo / admin123`

若从局域网设备访问，请将 `localhost` 替换为当前机器 IP。前端默认会根据访问主机自动连接网关和实时服务。

## 常用命令

```bash
make preflight-static
make ci-smoke
make step38-check
make step39-check
make step40-check
make security-scan
make release-bundle
python3 scripts/test_step40_release_acceptance.py
```

## 接口与文档入口

- OpenAPI 规范：`openapi/smart-parking.yaml`
- 演示与运行说明：`docs/defense_demo_runbook.md`
- 安全与配置说明：`docs/security_hardening.md`

核心接口包括：

- `/api/v1/auth/login`
- `/api/v1/owner/reservations`
- `/api/v1/owner/dashboard`
- `/api/v1/owner/orders/{order_id}`
- `/api/v1/admin/dashboard`
- `/api/v1/admin/dispatch/run`

## 验证与质量保障

仓库已集成以下工程化能力：

- OpenAPI 契约校验
- 前端类型检查与构建验证
- Step38 / Step39 / Step40 自动化验收脚本
- 安全扫描与配置检查
- GitHub Actions CI 流程

## 贡献方式

欢迎通过 Issue 和 Pull Request 参与改进。

- 提交 Bug：请使用 GitHub Issue
- 提交功能建议：请使用 GitHub Issue
- 提交代码：请先阅读 [CONTRIBUTING.md](./CONTRIBUTING.md)

## 支持与反馈

- 使用帮助、提问和反馈：见 [SUPPORT.md](./SUPPORT.md)
- 安全问题反馈：见 [SECURITY.md](./SECURITY.md)

## 维护说明

当前仓库主要用于智慧停车系统原型开发、课程/项目演示和工程化实践。若你准备将其用于正式部署，请至少完成以下工作：

- 替换默认演示账号和 JWT Secret
- 收紧 CORS 与网关配置
- 在前端环境变量中显式配置正式服务地址
- 对数据库、缓存、日志和告警体系做独立部署与加固

## 许可证

当前仓库尚未显式添加开源许可证文件。若后续需要对外开源，建议补充 `LICENSE` 文件后再公开授权范围。
