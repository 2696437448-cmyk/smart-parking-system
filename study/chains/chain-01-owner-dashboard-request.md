# Chain 01：Owner Dashboard 请求链

## 这条链解决什么业务问题

它解决的是：当业主打开 `/owner/dashboard` 时，页面上的推荐、最近订单和计费规则是如何一路从前端走到后端，再回到页面上的。

## 学完后你必须会说的 3 句话

1. `/owner/dashboard` 先由前端路由命中页面，再由 composable 发 HTTP 请求。
2. owner dashboard 请求不会直接到 `parking-service`，而是先经过 gateway。
3. `ParkingDashboardViewController` 是后端入口，但真正的视图数据会继续交给后面的 dashboard 组装层处理。

## 预备知识

- 知道前端页面、composable、service 是三层
- 知道网关是统一入口
- 知道 controller 是 HTTP 入口层

## 不要先看的文件

- `services/parking_service.py`
- 早期 stub 文件
- 模型训练脚本
- 与 owner dashboard 无关的长业务文件

## 场景故事

想象一个业主打开页面，想在某个区域、某个预约时间窗内找到可预约车位。页面上不仅要显示推荐车位，还要显示最近订单和计费规则。你现在要追的不是“页面长什么样”，而是“这些信息是怎么一路流动的”。

## 跟读路线

### Step 1：先看路由入口

打开：`apps/frontend/src/router.ts`

重点看：`/owner`、`dashboard`、`OwnerDashboard`

这一步要回答的问题：为什么访问 `/owner/dashboard` 会进 `OwnerDashboard.vue`？

参考答案：`router.ts` 里定义了 `/owner` 子路由，`dashboard` 子路径绑定的组件就是 `OwnerDashboard`。所以 URL 先由前端路由命中页面组件。

### Step 2：看页面把逻辑交给了谁

打开：`apps/frontend/src/pages/OwnerDashboard.vue`

重点看：`useOwnerDashboardView()`

这一步要回答的问题：页面里为什么没有把请求细节全写死？

参考答案：页面主要负责展示和按钮事件绑定，真正的数据加载、预约动作、视图状态管理都被下沉到了 `useOwnerDashboardView.ts`，这样页面不会变成难读的大文件。

### Step 3：看 composable 是怎样发起请求的

打开：`apps/frontend/src/composables/useOwnerDashboardView.ts`

重点看：`loadRecommendations()`、`fetchOwnerDashboard()`、`reserveAndOpenOrders()`

这一步要回答的问题：页面请求数据时，composable 真正调用了谁？

参考答案：`loadRecommendations()` 内部调用 `fetchOwnerDashboard()`，它来自 `services/owner.ts`。也就是说 composable 不直接手写 fetch URL，而是通过 service 层发请求。

### Step 4：看 service 层真正打向哪里

打开：`apps/frontend/src/services/owner.ts`

重点看：`fetchOwnerDashboard()`

这一步要回答的问题：前端请求是直接打某个后端服务，还是先打 gateway？

参考答案：`fetchOwnerDashboard()` 通过 `gatewayUrl("/api/v1/owner/dashboard", ...)` 组装地址，说明它先打的是网关地址，而不是直接打 `parking-service`。

### Step 5：看 gateway 怎样转发 owner 请求

打开：`services/gateway-service/src/main/java/com/smartparking/gateway/GatewayRoutesConfig.java`

重点看：`.path("/api/v1/owner/**", "/api/v1/admin/**", ...)`

这一步要回答的问题：gateway 怎么知道 owner 请求该转到哪个服务？

参考答案：`GatewayRoutesConfig` 里把 `/api/v1/owner/**` 和 `/api/v1/admin/**` 都路由到 `parkingBaseUrl`，也就是 `parking-service`。所以 owner dashboard 请求会先经过 gateway，再被转发给 `parking-service`。

### Step 6：看后端 HTTP 入口

打开：`services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewController.java`

重点看：`ownerDashboard(...)`

这一步要回答的问题：后端接到 owner dashboard 请求后的第一站是什么？

参考答案：请求命中 `ownerDashboard()` 方法。这个方法会整理 trace id，然后调用 `dashboardViewService.ownerDashboard(...)`，说明 controller 负责接入口和回响应，不在这里手写推荐和账单明细。

### Step 7：看 controller 后面发生了什么

打开：`services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewModules.java`

重点看：`DashboardViewService.ownerDashboard()`、`DashboardQueryService.ownerDashboard()`、`OwnerDashboardAssembler.assemble()`

这一步要回答的问题：owner dashboard 数据为什么不是 controller 自己拼？

参考答案：controller 把工作交给 `DashboardViewService`。后面再由 query service 取推荐和最近订单，由 assembler 组装出页面需要的 `summary / journey / billing_rule / latest_order / recommendations` 结构。这样页面拿到的是 view-model，不是数据库原始结构。

## 代码理解题

### 1. 为什么页面逻辑被放到 `useOwnerDashboardView.ts` 而不是直接写在 `OwnerDashboard.vue`？

参考答案：因为页面负责展示，composable 负责请求、状态和动作函数。这样页面更清楚，也更适合复用和测试。

### 2. `fetchOwnerDashboard()` 为什么不直接写死 `parking-service` 地址？

参考答案：因为系统设计上前端统一通过 gateway 进入后端。这样路由、治理和 trace 透传都在统一入口处理。

### 3. `ParkingDashboardViewController` 为什么不是这条链的终点？

参考答案：因为它只是 HTTP 入口。实际的数据查询和页面结构组装还要交给 `DashboardViewService / QueryService / Assembler`。

## 定位训练题

### 1. 如果让你找 owner dashboard 的前端入口，你应该先去哪里？

参考答案：先去 `apps/frontend/src/router.ts` 找 `/owner/dashboard`，再顺着页面组件进入 `OwnerDashboard.vue`。

### 2. 如果让你找 owner dashboard 的后端入口，你应该去哪里？

参考答案：`ParkingDashboardViewController.ownerDashboard()`，因为它是 `/api/v1/owner/dashboard` 的 HTTP 入口。

## 字段追踪题

题目：页面上的“最近订单”是从哪里来的？

参考答案：前端从 `dashboard.latest_order` 和 `dashboard.summary.latest_order_id` 读取；这些字段由 `OwnerDashboardAssembler.assemble()` 组装，而 `latest_order` 又来自 `DashboardQueryService.ownerDashboard()` 中对 `resolveLatestOrder()` 的调用。

## 最小验证

```bash
./scripts/defense_demo.sh start
curl "http://localhost:8080/api/v1/owner/dashboard?location=R1&preferred_window=2026-03-31T09:00:00/2026-03-31T10:00:00&user_id=owner-app-001"
```

验证时重点看：

- 返回里是否有 `summary`
- 是否有 `billing_rule`
- 是否有 `trace_id` 和 `service`

## 常见误解

- 误解：页面一打开就是直接调 `parking-service`
  纠正：前端先打 gateway，再由 gateway 转发。
- 误解：controller 里就有全部业务逻辑
  纠正：controller 主要是入口，后面还有 query / assembler 分工。
- 误解：页面字段就是数据库字段
  纠正：页面拿到的是聚合过的 view-model。

## 1 分钟复述稿

“当用户打开 `/owner/dashboard` 时，前端先由 `router.ts` 命中 `OwnerDashboard.vue`。页面并不自己处理请求，而是把数据加载逻辑交给 `useOwnerDashboardView.ts`。这个 composable 再通过 `services/owner.ts` 调用 gateway 的 `/api/v1/owner/dashboard`。请求进入 gateway 后，被 `GatewayRoutesConfig.java` 转发到 `parking-service`。后端由 `ParkingDashboardViewController.ownerDashboard()` 接住请求，再交给 `DashboardViewService`、`DashboardQueryService` 和 `OwnerDashboardAssembler` 组装出页面需要的推荐、最近订单和计费规则，最后返回给前端渲染。”

## 学完后应该留下什么记录

- 一张从 `/owner/dashboard` 到 controller 的简图
- 一条字段追踪记录：`latest_order_id` 从哪来
- 一次 `curl` 验证结果
