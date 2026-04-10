# 第 1 周：系统全景与主线定位

## 本周目标

- 知道这个项目里到底有哪些服务
- 分清当前 `Step40` 主线和历史保留文件
- 先建立“系统地图”，不要一上来扎进某个函数细节

如果你是第一次系统性读项目代码，建议先配合这两份辅助资料一起用：

- `study/appendix/how-to-read-code.md`
- `study/templates/weekly-note-template.md`

## 你会先看哪些文件

- `README.md`
- `infra/docker-compose.yml`
- `apps/frontend/src/router.ts`
- `services/gateway-service/src/main/java/com/smartparking/gateway/GatewayRoutesConfig.java`
- `services/parking-service/src/main/java/com/smartparking/parking/ParkingServiceApplication.java`
- `services/model_service.py`
- `services/realtime_service.py`

这 7 个文件的作用不是让你一次看懂所有实现，而是帮你回答一个更重要的问题：`这个项目现在是怎么跑起来的`。

## 这部分代码到底在做什么

这个项目不是单体应用，而是一套分工明确的微服务系统。你可以先把它拆成 5 个角色来记：

1. `Frontend`
   负责页面展示，给业主和物业看。
2. `Gateway Service`
   负责统一入口，把请求转发给后面的服务。
3. `Parking Service`
   负责核心业务，比如预约、计费、导航、dashboard 聚合。
4. `Model Service`
   负责预测和调度优化。
5. `Realtime Service`
   负责 WebSocket 实时推送，给物业端页面做实时状态展示。

`infra/docker-compose.yml` 是当前真实运行拓扑的最短真相来源。它告诉你：

- 哪些服务会启动
- 每个服务用什么语言运行
- 服务之间如何连接
- 端口分别是什么

本项目当前主线以 `Step40` 为准。它的默认业务入口有两个：

- 业主端：`http://localhost:4173/owner/dashboard`
- 物业端：`http://localhost:4173/admin/monitor`

### 当前主线

- `apps/frontend/src`
- `services/gateway-service`
- `services/parking-service`
- `services/model_service.py`
- `services/realtime_service.py`
- `scripts/test_step40_release_acceptance.py`

### 历史保留，不作为当前主线入口

- `services/parking_service.py`
- `services/stub_server.py`

它们仍然值得以后了解，但现在不应该先学它们，否则你很容易把旧实现和当前实现混在一起。

## 一条必须跟读的调用链

这一周先只跟一条最粗的系统调用链：

1. 用户在浏览器打开 `/owner/dashboard`
2. 前端路由把页面切到 `OwnerDashboard`
3. 前端通过 HTTP 请求访问网关
4. 网关根据路由把请求转发到 `parking-service`
5. `parking-service` 组装 owner dashboard 数据并返回
6. 前端把返回数据渲染成页面

这一周不要求你看懂数据结构的每个字段，只要能说清“请求经过了谁”就够了。

## 给新手的概念解释

### 什么是微服务

微服务不是“炫技拆很多服务”，而是把不同职责分开。这个项目里：

- 页面展示和后端业务分开
- 核心业务和算法服务分开
- 实时推送和普通业务接口分开

这样做的好处是职责清晰，但代价是你需要学会看“服务之间如何协作”。

### 什么是 Step40

你可以把 `Step40` 理解成“当前默认完成版”。  
它不是技术名词，而是这个项目迭代过程中的一个稳定里程碑。现在我们学代码，都默认以这个版本为主。

### 为什么先看 docker-compose

因为它最能帮你建立全局图。对新手来说，先知道“谁会启动、谁依赖谁”，比先读 800 行业务代码更重要。

## 本周可直接运行的命令

```bash
# 1. 安装依赖
python3 -m pip install -r requirements-dev.txt
cd apps/frontend && npm install && cd ../..

# 2. 运行预检查
./scripts/defense_demo.sh preflight
make preflight-static

# 3. 启动演示环境
./scripts/defense_demo.sh start
```

如果你暂时不想全跑起来，也至少先把 `README.md` 和 `infra/docker-compose.yml` 对着看一遍。

## 本周小练习

1. 用自己的话写出 5 个服务分别负责什么。
2. 在纸上或笔记里画出 `frontend -> gateway -> parking-service -> model/realtime` 的主线图。
3. 找出哪个文件最能说明“当前真实运行拓扑”，并写下原因。

## 本周完成标准

- 你能说出当前系统的 5 个主要服务
- 你知道默认主线不是旧的 `services/parking_service.py`
- 你能解释为什么学习要先看 `docker-compose` 和 `README`

## 可选加深阅读

- `memory-bank/architecture.md`
- `memory-bank/tech-stack.md`
- `reports/step40_technical_acceptance.md`

## 继续深入

本文是概览版。如果你准备真正跟代码，请继续：

- `../chains/chain-01-owner-dashboard-request.md`
- `../labs/lab-01-owner-dashboard.md`

