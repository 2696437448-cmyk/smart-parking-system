# Lab 03：Admin Dashboard 与 Realtime 降级

## 理解题

题目：为什么 Admin 页面更适合用聚合接口？

参考答案：因为它需要摘要、图表、诊断入口和降级说明等复合信息。用聚合接口可以把这些一次性组装好，而不是让前端自己拼很多零散接口。

为什么答案对：这正是 `ParkingDashboardViewModules.java` 存在的意义。

## 定位题

题目：定位“实时通道已降级”这类提示是在哪里被决定的。

参考答案：`AdminMonitor.vue` 读取 `state`，状态内容由 `useAdminDashboardView.ts` 的 `syncSurfaceState()` 结合 dashboard 数据和 realtime store 状态决定。

为什么答案对：页面只展示，状态判断在 composable。

## 字段追踪题

题目：`highlights.peak_occupancy` 是哪里算出来的？

参考答案：后端 `AdminDashboardAssembler.assemble()` 调用 `peakOccupancy(query.occupancyTrend())` 计算出来。

为什么答案对：这个字段是聚合层产物，不是前端即时算出来的。

## 最小验证题

题目：如何最小验证“聚合层 + 降级链”都活着？

参考答案：请求 `/api/v1/admin/dashboard` 看聚合结构，请求 `/api/v1/admin/realtime/status` 看 polling 降级状态。

为什么答案对：一个验证业务视图，一个验证降级通道。

## 复述题

题目：解释为什么 WebSocket 出问题后页面仍可能正常用。

参考答案：因为页面的业务数据还是可以通过 dashboard 聚合接口刷新，而实时状态会切到 polling，所以是降级，不是直接失效。
