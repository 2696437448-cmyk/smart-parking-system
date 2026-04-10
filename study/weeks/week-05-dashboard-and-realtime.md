# 第 5 周：Dashboard 聚合与实时通道

## 本周目标

- 理解 dashboard 为什么要单独做聚合层
- 看懂前端实时通道和降级逻辑
- 能分清“经营数据”和“实时状态”不是同一条链

## 你会先看哪些文件

- `services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewController.java`
- `services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewModules.java`
- `apps/frontend/src/composables/useAdminDashboardView.ts`
- `apps/frontend/src/composables/useRealtimeChannel.ts`
- `apps/frontend/src/stores/realtime.ts`
- `services/realtime_service.py`
- `apps/frontend/src/pages/AdminMonitor.vue`

## 这部分代码到底在做什么

到了 Step40，这个项目已经不只是“把几个接口接起来”，而是在做一种更适合页面消费的 `view-model` 聚合方式。

### Dashboard 聚合层在解决什么问题

如果没有聚合层，前端通常要自己调很多接口：

- 收益汇总一个接口
- 趋势图一个接口
- 占用率一个接口
- 预测对照一个接口
- 再自己拼成页面

这样前端会很累，也容易让页面逻辑越来越乱。  
所以这里在后端把 dashboard 数据先组装成页面想要的结构，再统一返回。

### 实时链路在解决什么问题

物业页面里有两类数据：

1. 经营视图数据
   来自 dashboard 聚合接口
2. 实时状态数据
   来自 WebSocket，如果 WebSocket 不可用，就退回 polling

所以你要记住：  
`dashboard` 和 `实时通道` 是互补关系，不是同一个东西。

## 一条必须跟读的调用链

这周建议你跟 `物业端 AdminMonitor` 这条链：

1. `AdminMonitor.vue` 引入 `useAdminDashboardView()`
2. `useAdminDashboardView.ts` 一方面调用 `fetchAdminDashboard()`
3. 另一方面调用 `useRealtimeChannel()`
4. `fetchAdminDashboard()` 请求 `/api/v1/admin/dashboard`
5. `ParkingDashboardViewController` 收到请求
6. `DashboardViewService -> DashboardQueryService -> AdminDashboardAssembler`
7. 后端返回 `summary / highlights / sections / degraded_metadata`
8. 前端同时尝试 WebSocket，如果失败就自动切到 polling

## 给新手的概念解释

### 什么是 view-model

你可以把它理解成：`专门为页面准备的数据形状`。  
它不是数据库原始结构，也不是最底层业务对象，而是“页面刚好需要什么，就按页面的方式给什么”。

### 什么是 Assembler

Assembler 就是“组装器”。  
它的工作不是查数据库，而是把查到的原始结果整理成页面更容易消费的结构。

### 什么是降级

降级不是失败，而是“服务部分不可用时切换到备用方案”。  
这里的例子是：

- 正常：WebSocket 实时推送
- 降级：HTTP 轮询

页面仍然可用，只是实时性下降。

## 本周可直接运行的命令

```bash
# 启动整套环境
./scripts/defense_demo.sh start

# 查看 admin dashboard 聚合接口
curl "http://localhost:8080/api/v1/admin/dashboard?date=2026-03-31&trend_days=7&trend_limit=12"

# 查看轮询降级接口
curl "http://localhost:8080/api/v1/admin/realtime/status"
```

如果你想进一步体验降级链路，可以读：

- `scripts/test_step8_realtime_channel.py`

## 本周小练习

1. 写出 `summary`、`highlights`、`sections` 三块数据各自大概负责什么。
2. 找出 `useRealtimeChannel.ts` 中 WebSocket 失败后切到 polling 的位置。
3. 用一句话解释：为什么 dashboard 聚合接口更适合页面，而不是让页面自己拼 4 个接口。

## 本周完成标准

- 你能说清 dashboard 聚合层解决了什么问题
- 你知道 `AdminMonitor` 页面同时依赖“聚合接口 + 实时通道”
- 你能解释 WebSocket 和 polling 的降级关系

## 可选加深阅读

- `openapi/smart-parking.yaml`
- `reports/step38_execution.md`
- `reports/step39_execution.md`

## 继续深入

Dashboard 聚合与 realtime 降级的详细教程在这里：

- `../chains/chain-03-admin-dashboard-realtime.md`
- `../labs/lab-03-admin-realtime.md`

