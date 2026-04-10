# Chain 02：预约 / 订单 / 计费 / 导航业务闭环

## 这条链解决什么业务问题

它解决的是：用户从推荐页点一个车位以后，预约、订单、账单和导航是怎样串成一条完整业务链的。

## 学完后你必须会说的 3 句话

1. 预约不是停在推荐页，而是会生成订单上下文并跳到订单页。
2. `orderId` 会通过路由参数和本地存储共同恢复，所以订单页和导航页能接上同一条业务链。
3. 账单和导航不是前端自己算出来的，它们都来自后端的订单与导航接口。

## 预备知识

- 知道什么是页面跳转
- 知道什么是 `query` 参数
- 知道前端通过 service 调后端接口

## 不要先看的文件

- 模型训练脚本
- Admin dashboard 图表代码
- 与 owner 业务无关的实时服务细节

## 场景故事

用户先在推荐页选中了一个车位，然后系统要创建预约、生成订单、展示账单、最后还能去看导航。如果你看懂这条链，你就第一次真正看到了“业务闭环”，而不是只看一个页面。

## 跟读路线

### Step 1：看推荐页如何发起预约

打开：`apps/frontend/src/pages/OwnerDashboard.vue`

重点看：推荐卡片按钮上的 `@click="reserveAndOpenOrders(...)"`

这一步要回答的问题：预约动作是从哪里发起的？

参考答案：从推荐页里每个候选车位卡片的按钮发起，调用的是 composable 暴露出来的 `reserveAndOpenOrders()`。

### Step 2：看预约动作具体做了什么

打开：`apps/frontend/src/composables/useOwnerDashboardView.ts`

重点看：`reserveAndOpenOrders(slotId)`

这一步要回答的问题：预约成功后，为什么页面能直接跳去订单页？

参考答案：这个方法先调用 `reserveOwnerSlot()` 提交预约，拿到 `order_id` 后通过 `orderContext.rememberOrderId()` 记住订单，再调用 `navigateWithOrder('/owner/orders', nextOrderId)` 跳去订单页。

### Step 3：看订单上下文是怎么恢复的

打开：`apps/frontend/src/composables/useOrderContext.ts`

重点看：`orderId`、`rememberOrderId()`、`ensureRouteOrderId()`、`navigateWithOrder()`

这一步要回答的问题：如果刷新页面，为什么订单页还能知道当前订单是谁？

参考答案：`orderId` 会优先读路由里的 `query.orderId`，如果没有，再读 `localStorage` 里的 `ORDER_STORAGE_KEY`。所以刷新页面或页面间跳转时，订单上下文可以被恢复。

### Step 4：看订单页怎样取账单详情

打开：`apps/frontend/src/composables/useOwnerOrderView.ts`

重点看：`loadOrder()`、`finishOrder()`、`fetchOrderDetail()`、`completeOrder()`

这一步要回答的问题：订单页是自己计算账单，还是向后端请求？

参考答案：订单页通过 `fetchOrderDetail(orderId)` 请求后端订单接口拿详情；结算时通过 `completeOrder(orderId, endedAt)` 请求后端完成订单。账单不是前端自己算的。

### Step 5：看导航页为什么属于同一条业务链

打开：`apps/frontend/src/composables/useOwnerNavigationView.ts`

重点看：`loadNavigation()`、`fetchNavigation(orderId)`

这一步要回答的问题：导航页为什么不是一个孤立页面？

参考答案：导航页同样依赖 `orderId` 上下文，调用的是 `/api/v1/owner/navigation/{orderId}`。所以它是订单链的后续步骤，而不是单独的静态页面。

### Step 6：看 reservation 请求真正打到哪里

打开：`apps/frontend/src/services/owner.ts`

重点看：`reserveOwnerSlot()`、`fetchOrderDetail()`、`completeOrder()`、`fetchNavigation()`

这一步要回答的问题：前端这 4 个动作分别对应哪类后端接口？

参考答案：分别对应预约、订单详情、订单完成、导航详情这 4 类 owner 业务接口，而且全部经由 gateway 进入后端。

### Step 7：看预约接口后端入口

打开：`services/parking-service/src/main/java/com/smartparking/parking/ParkingServiceApplication.java`

重点看：`ParkingController.createReservation()` 和 `ReservationService.reserve()`

这一步要回答的问题：预约接口只是插一条记录吗？

参考答案：不是。`reserve()` 先校验字段，再处理幂等键，再尝试拿锁，再检查是否已有活动预约，成功后插入预约，并调用 `billingService.createEstimatedOrder()` 生成预估账单订单。

### Step 8：看订单 / 结算 / 导航接口后端入口

打开：`services/parking-service/src/main/java/com/smartparking/parking/ParkingBusinessExtensions.java`

重点看：`orderDetail()`、`completeOrder()`、`navigation()`

这一步要回答的问题：订单详情、账单确认和导航信息分别由谁提供？

参考答案：`orderDetail()` 通过 `ownerAdminFacade.orderDetail(orderId)` 返回订单详情；`completeOrder()` 通过 `billingService.completeOrder(...)` 进入结算逻辑；`navigation()` 通过 `ownerAdminFacade.navigation(orderId)` 返回地图链接、目的地和路线摘要。

## 代码理解题

### 1. 为什么 `useOrderContext.ts` 对这条链很关键？

参考答案：因为它负责在推荐页、订单页、导航页之间传递并恢复 `orderId`，没有这层，业务链会在页面跳转时断开。

### 2. 为什么预约成功返回的 `order_id` 和 `reservation_id` 会被立即记住？

参考答案：因为后续订单详情、导航、结算都要依赖这个 ID，如果不立刻记录，就无法无缝进入下一步。

### 3. 为什么说这条链里已经带有一致性和幂等考虑？

参考答案：预约接口里有 `Idempotency-Key`、锁、重复预约检查和 DB 唯一约束保护，不是单纯的前端按钮点击就结束了。

## 定位训练题

### 1. 如果你要找“完成停车并结算”按钮对应的后端入口，应该怎么找？

参考答案：先从 `OwnerOrders.vue` 找 `finishOrder`，再到 `useOwnerOrderView.ts` 找 `completeOrder()`，再到 `services/owner.ts`，最后定位到 `ParkingBusinessExtensions.java` 的 `/api/v1/owner/orders/{orderId}/complete`。

### 2. 如果你要找导航页里 `map_url` 是从哪里来的，应该怎么找？

参考答案：先看 `useOwnerNavigationView.ts` -> `fetchNavigation()` -> owner service -> `navigation(orderId)` 后端接口 -> `ownerAdminFacade.navigation()`，最后看到 `mapUrl(point)` 生成地图链接。

## 字段追踪题

题目：订单页里的 `billing_status` 最终来自哪里？

参考答案：前端从 `orderDetail.billing_status` 读取；这个字段来自后端 `ownerAdminFacade.orderDetail(orderId)` 返回的 payload，而 payload 又来自 `BillingRecordRow.billingStatus()`。

## 最小验证

```bash
./scripts/defense_demo.sh start
curl -X POST "http://localhost:8080/api/v1/owner/reservations"       -H "Content-Type: application/json"       -H "Idempotency-Key: demo-owner-order"       -d '{"user_id":"owner-app-001","preferred_window":"2026-03-31T09:00:00/2026-03-31T10:00:00","location":"R1","slot_id":"R1-S001"}'
```

然后再请求：

```bash
curl "http://localhost:8080/api/v1/owner/orders/<order_id>"
curl "http://localhost:8080/api/v1/owner/navigation/<order_id>"
```

## 常见误解

- 误解：订单页只是把推荐页的数据搬过去
  纠正：订单页会重新请求订单详情接口。
- 误解：导航页和订单没有关系
  纠正：导航页也依赖同一个 `orderId` 上下文。
- 误解：预约成功只代表插入了一条 reservation
  纠正：后端还会建立预估账单订单，并且受幂等和锁保护。

## 1 分钟复述稿

“推荐页上的预约按钮会调用 `reserveAndOpenOrders()`，它先通过 owner service 请求 `/api/v1/owner/reservations`，预约成功后把返回的 `order_id` 写进订单上下文，再跳转到订单页。订单页通过 `fetchOrderDetail()` 请求后端订单详情接口，结算时再调用 `/complete` 接口进入账单确认逻辑。导航页继续复用同一个 `orderId`，调用 `/api/v1/owner/navigation/{orderId}` 获取 ETA、路线摘要和地图链接。所以推荐、订单、账单、导航并不是分散页面，而是一条连贯的 owner 业务闭环。”

## 学完后应该留下什么记录

- 一条 `orderId` 在 3 个页面间流转的链路图
- 一次 reservation -> order -> navigation 的接口验证
- 一条字段追踪记录：`billing_status` 从哪来
