# Smart Parking System

> 面向社区停车场景的智慧停车调度系统，提供统一登录、车位预约、共享计费、地图导航、运营看板、实时监控与智能调度能力。

[![Java](https://img.shields.io/badge/Java-17-orange.svg)](https://openjdk.org/projects/jdk/17/)
[![Python](https://img.shields.io/badge/Python-3.11-green.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3-brightgreen.svg)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue.svg)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)

## Overview

项目聚焦社区停车中的预约冲突、车位供需不均、收费与运营分析割裂等问题，采用 Java + Python + Vue 的混合微服务架构，打通业主预约、订单结算、导航指引、物业经营分析和智能调度全链路。

## Core Features

- 统一登录与角色路由：支持业主端、物业端登录和基于 JWT 的身份识别。
- 业主业务闭环：支持车位推荐、预约下单、订单查询、费用结算和地图导航。
- 物业运营看板：支持收益趋势、区域占用率、预测对比、实时状态和诊断信息展示。
- 智能调度与预测：结合 Spark ETL、LSTM-Lite 预测和 Hungarian 优化算法完成供需分析与调度分配。
- 工程化交付：内置 OpenAPI 契约、Trace ID 透传、自动化验收、预检脚本和发布打包流程。

## Architecture

| Service | Tech Stack | Responsibility |
| :--- | :--- | :--- |
| Gateway Service | Spring Boot 3, Spring Cloud Gateway, Resilience4j, JWT | 统一鉴权、路由转发、CORS、熔断与链路追踪 |
| Parking Service | Spring Boot 3, JDBC, MySQL, Redis, Redisson | 预约主链、共享计费、订单结算、导航和物业经营聚合接口 |
| Model Service | Python 3.11 | 供需预测、Hungarian 调度、模型版本激活与回滚 |
| Realtime Service | Python 3.11, WebSocket | 实时状态推送、轮询降级与监控指标输出 |
| Frontend | Vue 3, TypeScript, Pinia, Vue Router, Arco Design, ECharts, Leaflet, Capacitor | 业主端与物业端页面、地图导航、图表展示和移动端壳层 |

## Project Structure

```text
apps/frontend/              Vue3 前端工程
services/gateway-service/   网关与鉴权服务
services/parking-service/   停车核心业务服务
services/*.py               模型服务、实时推送与辅助服务
scripts/                    自动化验收、预检与发布脚本
openapi/                    API 契约定义
infra/                      监控与基础设施配置
config/                     环境配置模板
```

## Quick Start

### Requirements

- Docker / Docker Compose v2+
- Python 3.11+
- Node.js 20+
- Java 17+

### 1. Clone

```bash
git clone https://github.com/2696437448-cmyk/smart-parking-system.git
cd smart-parking-system
```

### 2. Prepare Environment

```bash
cp .env.example .env
cp apps/frontend/.env.example apps/frontend/.env.local
python3 -m pip install -r requirements-dev.txt
cd apps/frontend && npm install && cd ../..
```

如需更安全的默认配置，可将 `.env.example` 替换为 `.env.secure.example`。

### 3. Start Demo Environment

```bash
./scripts/defense_demo.sh preflight
make preflight-static
./scripts/defense_demo.sh start
```

### 4. Open the App

- 登录入口：`http://localhost:4173/login`
- 业主演示账号：`owner_demo / demo123`
- 物业演示账号：`admin_demo / admin123`
- 若从局域网设备访问，请将 `localhost` 替换为当前机器 IP；前端默认会跟随页面所在主机自动连接 `8080/8090` 服务。

## Common Commands

```bash
make preflight-static
make ci-smoke
make step38-check
make step39-check
make step40-check
make release-bundle
make security-scan
python3 scripts/test_step40_release_acceptance.py
```

## API Contract

- OpenAPI：`openapi/smart-parking.yaml`
- 核心接口：
  - `/api/v1/auth/login`
  - `/api/v1/owner/reservations`
  - `/api/v1/owner/dashboard`
  - `/api/v1/owner/orders/{order_id}`
  - `/api/v1/admin/dashboard`
  - `/api/v1/admin/dispatch/run`

## Deployment Notes

- Demo 环境中的账号、JWT secret 与宽松 CORS 配置仅适用于本地演示，不建议直接用于正式环境。
- 正式部署时建议在 `apps/frontend/.env.local` 中显式配置网关与实时服务地址。
- 运行与安全说明可参考 `docs/defense_demo_runbook.md` 和 `docs/security_hardening.md`。
