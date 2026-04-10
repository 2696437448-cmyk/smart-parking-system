# Chain 03：Admin Dashboard 聚合与 Realtime 降级链

## 这条链解决什么业务问题

它解决的是：物业端经营驾驶舱怎样一次拿到聚合视图，又怎样在 WebSocket 异常时退回到 polling 继续工作。

## 学完后你必须会说的 3 句话

1. Admin 页面不是自己拼多个后端接口，而是优先使用 dashboard 聚合接口。
2. `Query / Assembler / ViewService` 是后端把经营数据整理成页面结构的分层。
3. realtime 通道是增强能力，不是页面唯一数据来源；它挂了以后页面还能降级继续工作。

## 预备知识

- 知道 dashboard 是给页面准备的复合视图
- 知道 WebSocket 和 polling 是两种不同更新方式
- 知道前端 store 用来保存跨组件状态

## 不要先看的文件

- owner 预约相关长链
- 模型训练实现细节
- 早期非 Step40 页面

## 场景故事

物业端打开 `/admin/monitor`，页面需要同时展示经营摘要、图表、实时状态和降级说明。如果每块都自己调一个接口，页面会非常碎；如果实时通道断了，页面又不能直接瘫掉。所以这里会看到“聚合层”和“降级”两个很典型的工程做法。

## 跟读路线

### Step 1：先看页面是不是自己拼数据

打开：`apps/frontend/src/pages/AdminMonitor.vue`

重点看：`useAdminDashboardView()`、图表 option、`store.modeLabel`

这一步要回答的问题：页面是不是自己到处发请求、自己算状态？

参考答案：不是。页面主要消费 `useAdminDashboardView()` 产出的 `dashboard`、`state` 和 realtime store 状态。说明页面主要负责展示和图表渲染。

### Step 2：看页面逻辑在哪里集中

打开：`apps/frontend/src/composables/useAdminDashboardView.ts`

重点看：`refreshBusinessViews()`、`syncSurfaceState()`

这一步要回答的问题：Admin 页面是怎样拿到经营视图并把它转成页面状态的？

参考答案：`refreshBusinessViews()` 通过 `fetchAdminDashboard()` 请求聚合接口；拿到数据后，再结合 realtime store 的状态，在 `syncSurfaceState()` 里生成 ready / degraded / empty 等视图状态。

### Step 3：看 realtime 通道如何建立和降级

打开：`apps/frontend/src/composables/useRealtimeChannel.ts`

重点看：`connectWebSocket()`、`startPolling()`、`scheduleReconnect()`

这一步要回答的问题：WebSocket 出问题时，为什么页面不会彻底停掉？

参考答案：因为 `useRealtimeChannel()` 会优先连 WebSocket；一旦初始化失败、消息解析失败、连接关闭或传输报错，就会 `markDegraded()` 并启动 polling，同时定时尝试重连。

### Step 4：看 store 是怎样表达状态切换的

打开：`apps/frontend/src/stores/realtime.ts`

重点看：`mode`、`source`、`connected`、`applySnapshot()`、`markDegraded()`

这一步要回答的问题：页面是怎么知道当前是实时模式还是降级模式的？

参考答案：store 用 `mode` 表示 `realtime` 还是 `degraded`，用 `source` 表示 `websocket` 还是 `polling`，用 `connected` 表示是否当前连接正常。页面通过这些状态渲染标签和提示。

### Step 5：看 Admin dashboard 的类型为什么这么重要

打开：`apps/frontend/src/types/dashboard.ts`

重点看：`AdminDashboardView`

这一步要回答的问题：为什么要专门定义 `summary / highlights / sections / degraded_metadata`？

参考答案：因为 Admin 页面并不是随便接几个数组，而是消费一个专门为页面设计的 view-model。这样前后端对 dashboard 结构有稳定约定，页面状态表达也更清楚。

### Step 6：看聚合接口真正怎么组装

打开：`services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewController.java`
再打开：`services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewModules.java`

重点看：`adminDashboard()`、`DashboardQueryService.adminDashboard()`、`AdminDashboardAssembler.assemble()`

这一步要回答的问题：为什么说 Admin dashboard 不是“查一张表”？

参考答案：因为 `adminDashboard()` 后面会去取 monitor summary、收益汇总、收益趋势、占用趋势、预测对照，然后由 assembler 统一拼成 `summary / highlights / sections / diagnostic_links / degraded_metadata` 结构。这显然不是单表查询，而是聚合视图。

### Step 7：看 realtime 服务本身做了什么

打开：`services/realtime_service.py`

重点看：`do_GET()`、`_ws_accept()`、`_ws_text_frame()`、`/ws/status`

这一步要回答的问题：realtime-service 在这里的职责是什么？

参考答案：它负责处理 WebSocket 握手和定时推送实时快照。也就是说它提供实时流，而不是承担 dashboard 聚合查询本身。

## 代码理解题

### 1. 为什么 Admin 页面更适合聚合接口，而不是每个卡片自己发请求？

参考答案：因为页面需要的是一个完整经营视图，里面包含摘要、图表和诊断信息。如果前端自己拼接多个接口，状态管理、错误处理和字段对齐都会变复杂。

### 2. `syncSurfaceState()` 为什么要同时看 dashboard 数据和 realtime store 状态？

参考答案：因为页面是否 ready / empty / degraded，不只由业务数据是否存在决定，也取决于实时通道当前是 WebSocket 还是 polling。

### 3. 为什么说 realtime 是增强链，而不是唯一数据源？

参考答案：因为即使 WebSocket 挂了，`refreshBusinessViews()` 仍然能通过聚合接口刷新业务数据，polling 也能继续提供状态更新。

## 定位训练题

### 1. 如果要找 Admin 页面上“实时通道已降级”这类提示是从哪里来的，你怎么找？

参考答案：先从 `AdminMonitor.vue` 找 `state`，再到 `useAdminDashboardView.ts` 的 `syncSurfaceState()`，再看它如何根据 store 的 `mode` 调 `markDegraded()`。

### 2. 如果要找“峰值占用率”是在哪里算出来的，你怎么找？

参考答案：先看前端 `dashboard.highlights.peak_occupancy`，再到 `AdminDashboardAssembler.assemble()`，最后看到 `peakOccupancy(query.occupancyTrend())`。

## 字段追踪题

题目：页面里的 `dispatch_strategy` 从哪里来的？

参考答案：前端从 `dashboard.summary.dispatch_strategy` 取值；它由 `AdminDashboardAssembler` 写入，而源头来自 `DashboardQueryService.adminDashboard()` 中 `monitorSummary` 的返回 payload。

## 最小验证

```bash
./scripts/defense_demo.sh start
curl "http://localhost:8080/api/v1/admin/dashboard?date=2026-03-31&trend_days=7&trend_limit=12"
curl "http://localhost:8080/api/v1/admin/realtime/status"
```

如果你本机支持 WebSocket 客户端，也可以验证：

- `ws://localhost:8090/ws/status`

## 常见误解

- 误解：dashboard 就是查一张表
  纠正：这里是多个来源的聚合视图。
- 误解：realtime 一断页面就彻底不可用
  纠正：WebSocket 断了会降级到 polling，聚合接口仍可刷新。
- 误解：前端自己拼所有字段更简单
  纠正：短期可能快，长期会让错误处理、状态表达和字段契约全部失控。

## 1 分钟复述稿

“Admin 页面不是自己分别去取收益、占用率、预测和诊断信息，而是通过 `useAdminDashboardView()` 调用聚合接口一次拿到完整的经营视图。后端由 `ParkingDashboardViewController` 接口进入，再通过 `DashboardQueryService` 查询多类数据，最后由 `AdminDashboardAssembler` 组装成页面可直接消费的 `summary / highlights / sections` 结构。与此同时，前端通过 `useRealtimeChannel()` 建立 WebSocket 连接，把实时状态写入 store；如果 WebSocket 异常，就会标记降级并切换到 polling，所以页面不会因为实时链路出问题就彻底失效。”

## 学完后应该留下什么记录

- 一张聚合链图：controller -> query -> assembler -> view-model -> page
- 一次 dashboard 接口和 realtime 状态接口的验证记录
- 一条字段追踪记录：`dispatch_strategy` 或 `peak_occupancy`
