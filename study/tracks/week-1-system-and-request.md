# 第 1 周：系统地图与请求流

这一周的任务很明确：先知道这个项目现在是怎么跑起来的，再跟一条最基础的页面请求链。  
你的目标不是立刻看懂所有源码，而是先建立“位置感”。

## 这周只学什么

只回答 3 个问题：

1. 当前 `Step40` 主线到底由哪些服务组成
2. `owner dashboard` 这个页面的请求经过了谁
3. 为什么我们要先看入口文件，而不是先看最长的业务文件

## 这周配套讲义

按这个顺序读：

1. [第 1 周：系统全景与主线定位](../weeks/week-01-system-map.md)
2. [第 2 周：前端基础与页面分层](../weeks/week-02-frontend-foundation.md)
3. [第 3 周：请求流与网关](../weeks/week-03-request-flow-and-gateway.md)
4. [新手怎么读这个项目的代码](../appendix/how-to-read-code.md)

## 先看哪些文件

只看下面这些，不要贪多：

- `README.md`
- `infra/docker-compose.yml`
- `apps/frontend/src/main.ts`
- `apps/frontend/src/router.ts`
- `apps/frontend/src/pages/OwnerDashboard.vue`
- `apps/frontend/src/composables/useOwnerDashboardView.ts`
- `apps/frontend/src/services/owner.ts`
- `services/gateway-service/src/main/java/com/smartparking/gateway/GatewayRoutesConfig.java`
- `services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewController.java`

## 这周不要先看

这些文件不是现在这周的重点，先别跳进去：

- `services/parking_service.py`
- `services/stub_server.py`
- 模型训练细节脚本
- `parking-service` 里很长的业务扩展细节

## 带读节奏

### 第 1 次：建立系统地图

先对着 `README.md` 和 `infra/docker-compose.yml` 看：

- 有哪些服务会启动
- 前端页面入口是什么
- 默认业务页面是什么
- gateway、parking-service、model-service、realtime-service 各自做什么

这一步结束时，你至少要能口头说出：

`这个项目不是一个单体网页，而是前端 + 网关 + 多个后端服务协作起来的。`

### 第 2 次：跟 owner dashboard 请求链

按这个顺序读：

1. `router.ts` 看页面路由怎么进 `OwnerDashboard`
2. `OwnerDashboard.vue` 看页面主要依赖谁
3. `useOwnerDashboardView.ts` 看页面逻辑往哪里走
4. `owner.ts` 看 HTTP 请求发向哪里
5. `GatewayRoutesConfig.java` 看网关如何转发
6. `ParkingDashboardViewController.java` 看后端接口从哪里进

这一轮只要搞懂“请求经过了谁”，先不要要求自己看懂每个字段。

### 第 3 次：做最小验证

至少做其中 2 件：

```bash
./scripts/defense_demo.sh preflight
./scripts/defense_demo.sh start
curl http://localhost:8080/actuator/health
curl "http://localhost:8080/api/v1/owner/dashboard?location=R1&preferred_window=2026-03-31T09:00:00/2026-03-31T10:00:00&user_id=owner-app-001"
```

验证时只关心：

- 服务有没有起来
- 网关是不是通的
- owner dashboard 接口是不是能返回东西

### 第 4 次：复述与笔记

用 [每周笔记模板](../templates/weekly-note-template.md) 写一页。  
最少要写：

- 我先看了哪些文件
- owner dashboard 这条调用链
- 我还没完全懂的问题
- 我这周真实跑了哪些命令

## 这周必须会说的主链

1. 浏览器打开 `/owner/dashboard`
2. 前端路由进入 `OwnerDashboard`
3. 页面逻辑通过 composable 和 service 发 HTTP 请求
4. 请求先到 gateway
5. gateway 把请求转到 `parking-service`
6. `parking-service` 返回 dashboard 数据
7. 前端把结果渲染到页面

## 这周复述题

1. 为什么这个项目要先看 `docker-compose`？
2. `useOwnerDashboardView.ts` 在页面链路里起什么作用？
3. 为什么不能把 `services/parking_service.py` 当成当前主线？

## 这周定位题

1. 找到 `owner dashboard` 页面路由入口和接口调用入口。
2. 找到 gateway 里负责转发 owner/admin 业务请求的配置位置。

## 这周完成标准

- 你能说出当前主线里的主要服务
- 你能用自己的话复述 owner dashboard 请求链
- 你知道当前主线文件和历史保留文件的区别
- 你至少运行过一次本周命令或接口验证

## 卡住时怎么退回

如果你看到一半开始迷路，按这个顺序退回：

1. 回看本页“这周必须会说的主链”
2. 回看 [第 1 周讲义](../weeks/week-01-system-map.md)
3. 回看 [新手怎么读代码](../appendix/how-to-read-code.md)
4. 再重新从 `router.ts` 和 `GatewayRoutesConfig.java` 开始

## 详细深读与练习

如果你觉得本页仍然更像路线图，请继续：

- `../chains/chain-01-owner-dashboard-request.md`
- `../labs/lab-01-owner-dashboard.md`

