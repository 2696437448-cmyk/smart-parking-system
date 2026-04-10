# Lab 02：预约 / 订单 / 计费 / 导航闭环

## 理解题

题目：为什么 `useOrderContext.ts` 是 owner 闭环里的关键文件？

参考答案：因为它负责在推荐页、订单页、导航页之间传递和恢复 `orderId`，没有它，页面跳转后上下文会断掉。

为什么答案对：订单、导航、结算都依赖同一个订单标识。

## 定位题

题目：从“完成停车并结算”按钮，一路定位到后端接口入口。

参考答案：`OwnerOrders.vue` -> `useOwnerOrderView.ts` 的 `finishOrder()` -> `services/owner.ts` 的 `completeOrder()` -> `ParkingBusinessExtensions.java` 的 `/api/v1/owner/orders/{orderId}/complete`。

为什么答案对：这是完整前后端调用路径。

## 字段追踪题

题目：订单页的 `billing_status` 最终从哪里来？

参考答案：来自后端 `ownerAdminFacade.orderDetail(orderId)` 返回的订单 payload，根上是 `BillingRecordRow.billingStatus()`。

为什么答案对：前端只是展示它，不负责计算它。

## 最小验证题

题目：最小验证这条闭环时，至少应该验证哪两个接口？

参考答案：先验证 `/api/v1/owner/reservations`，再验证 `/api/v1/owner/orders/{orderId}` 或 `/api/v1/owner/navigation/{orderId}`。

为什么答案对：一个证明预约真的生成了订单，一个证明后续链真的接上了。

## 复述题

题目：解释为什么导航页不是孤立页面。

参考答案：导航页依赖 `orderId` 上下文，并通过后端导航接口取路线信息，所以它是订单链的后续步骤，不是单独展示页。
