# Lab 01：Owner Dashboard 请求链

## 理解题

题目：为什么 owner dashboard 页面不自己手写完整请求逻辑？

参考答案：因为页面主要负责展示，数据请求和视图状态被下沉到了 `useOwnerDashboardView.ts`，这样页面不会变成混杂展示与逻辑的大文件。

为什么答案对：这是当前前端结构的明确分层。

常见错因：把 Vue 页面看成“所有逻辑都应该写在这里”。

## 定位题

题目：找出 `/owner/dashboard` 的前端入口和后端入口。

参考答案：前端入口是 `apps/frontend/src/router.ts` 中的 `OwnerDashboard` 路由；后端入口是 `ParkingDashboardViewController.ownerDashboard()`。

为什么答案对：一个解决页面路由问题，一个解决 HTTP 接口入口问题。

常见错因：把 `OwnerDashboard.vue` 误认为路由入口，或把 assembler 误认为 HTTP 入口。

## 字段追踪题

题目：`summary.latest_order_id` 是从哪里来的？

参考答案：由 `OwnerDashboardAssembler.assemble()` 写入，值来自 `query.latestOrder()` 中的 `order_id`。

为什么答案对：前端不自己造这个字段，它在后端 view-model 里组装完成。

常见错因：以为页面直接从数据库字段拿值。

## 最小验证题

题目：最小验证 owner dashboard 请求链，只需要跑哪 2 个动作？

参考答案：`./scripts/defense_demo.sh start` 和 `curl gateway /api/v1/owner/dashboard`。

为什么答案对：一个确认环境起来，一个确认链路真的返回了 owner dashboard 结构。

## 复述题

题目：不用术语，解释“页面数据是怎么回来的”。

参考答案：先由前端路由进页面，再由 composable 调 gateway，gateway 把请求转给 `parking-service`，后端 controller 接住请求，再把数据交给 dashboard 组装层整理，最后返回给页面渲染。
