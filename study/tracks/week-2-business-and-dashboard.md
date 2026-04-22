# 第 2 周：Java 业务主链与 Dashboard

这一周开始正式进入后端主业务，但仍然只追一条主线。  
你的任务不是把整个 `parking-service` 全啃下来，而是看懂：`接口进来之后，页面数据是怎么被组织出来的。`

## 这周只学什么

只回答 3 个问题：

1. `parking-service` 里的接口通常从哪里进入
2. dashboard 数据为什么不是某一个类里“直接一把查完”
3. 前端页面拿到的数据为什么要先经过 view-model 或聚合层

## 这周配套讲义

按这个顺序读：

1. [第 4 周：Java 业务主链](../weeks/week-04-parking-service-core.md)
2. [第 5 周：Dashboard 聚合与实时通道](../weeks/week-05-dashboard-and-realtime.md)
3. [项目文件地图](../appendix/file-map.md)

## 先看哪些文件

- `services/parking-service/src/main/java/com/smartparking/parking/ParkingServiceApplication.java`
- `services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewController.java`
- `services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewModules.java`
- `services/parking-service/src/main/java/com/smartparking/parking/ParkingBusinessExtensions.java`
- `apps/frontend/src/composables/useOwnerDashboardView.ts`
- `apps/frontend/src/composables/useAdminDashboardView.ts`
- `apps/frontend/src/types/dashboard.ts`
- `apps/frontend/src/pages/AdminMonitor.vue`
- `apps/frontend/src/stores/realtime.ts`

## 这周不要先看

- Repository 或 DTO 细节里的每个字段
- 很长的并发保护和一致性分支
- 模型服务实现
- ETL 细节

## 带读节奏

### 第 1 次：后端入口感

先建立这两个认识：

- HTTP 请求不是直接进数据库，而是先进入 Controller
- dashboard 返回的不是数据库原表，而是为页面整理过的结果

先看：

1. `ParkingDashboardViewController.java`
2. `ParkingDashboardViewModules.java`

这一轮只关注类的职责，不钻细节。

### 第 2 次：跟一条 dashboard 组装链

建议先跟 `owner dashboard`，再补 `admin dashboard`。

关注点：

1. 接口从哪里接收参数
2. 谁负责查询
3. 谁负责 assembler 或 view-service 组装
4. 返回的数据结构最后如何被前端使用

同时配合前端看：

1. `useOwnerDashboardView.ts`
2. `useAdminDashboardView.ts`
3. `dashboard.ts`

这一轮要形成一个认识：  
`页面看到的数据，常常是后端聚合层专门为页面准备过的 view-model。`

### 第 3 次：看 realtime 是怎么挂在 dashboard 旁边的

这一块不要一上来研究 WebSocket 协议，而是先回答：

- 为什么 dashboard 页面还需要 realtime 状态
- realtime 断了为什么页面还能降级工作
- 前端 store 在这里承担什么角色

推荐看：

- `apps/frontend/src/stores/realtime.ts`
- `week-05-dashboard-and-realtime.md`

### 第 4 次：做最小验证

至少做其中 2 件：

```bash
./scripts/defense_demo.sh start
curl "http://localhost:8080/api/v1/owner/dashboard?location=R1&preferred_window=2026-03-31T09:00:00/2026-03-31T10:00:00&user_id=owner-app-001"
curl "http://localhost:8080/api/v1/admin/dashboard?date=2026-03-31&trend_days=7&trend_limit=12"
curl "http://localhost:8080/api/v1/admin/realtime/status"
```

## 这周必须会说的主链

1. 前端页面请求 dashboard 接口
2. 请求经 gateway 进入 `parking-service`
3. Controller 接收请求
4. Query / Assembler / ViewService 组织页面需要的数据
5. 返回统一的 dashboard 结构
6. 前端 composable 把结果转成页面状态
7. realtime 作为增强或降级伴生能力补充页面状态

## 这周复述题

1. `Controller / Service / Repository` 在这个项目里各自是什么角色？
2. 为什么 dashboard 需要聚合层，而不是前端自己拼所有字段？
3. realtime 通道断开时，为什么页面不一定就完全不可用？

## 这周定位题

1. 找到 owner 或 admin dashboard 的后端接口入口。
2. 找到前端页面里哪一层把接口数据转成页面状态。
3. 找到 realtime 状态在前端是由哪个 store 或 composable 管理的。

## 这周完成标准

- 你能说出 dashboard 数据是如何从后端聚合后提供给前端的
- 你能区分 Controller、聚合层、页面 composable 的职责
- 你知道 realtime 是增强链路，不是唯一数据来源
- 你至少验证过一个 dashboard 接口和一个 realtime 相关接口

## 卡住时怎么退回

1. 回看本页“这周必须会说的主链”
2. 回看 [第 4 周讲义](../weeks/week-04-parking-service-core.md)
3. 再回看 `ParkingDashboardViewController.java`
4. 最后再重新读 `ParkingDashboardViewModules.java`

## 详细深读与练习

这一周请分别进入：

- owner 闭环：`../chains/chain-02-owner-order-billing-navigation.md`
- admin 聚合：`../chains/chain-03-admin-dashboard-realtime.md`
- 对应练习：`../labs/lab-02-owner-business.md`、`../labs/lab-03-admin-realtime.md`

