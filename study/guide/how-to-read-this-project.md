# 怎么读这个项目

这个项目不是单体应用，而是前端、网关、业务服务、模型服务、实时服务一起组成的系统。对初学者来说，读法比读多少更重要。

## 先记住一个原则

不要从“最长的文件”开始。要从“最能说明调用关系的入口文件”开始。

在这个项目里，最值得先看的入口通常是：

- `apps/frontend/src/router.ts`
- `apps/frontend/src/pages/*.vue`
- `apps/frontend/src/composables/*.ts`
- `services/gateway-service/.../GatewayRoutesConfig.java`
- `services/parking-service/.../ParkingDashboardViewController.java`
- `services/parking-service/.../ParkingController`
- `services/model_service.py`
- `services/realtime_service.py`
- `scripts/test_step40_release_acceptance.py`

## 推荐阅读顺序

每次尽量按这个顺序：

1. 先知道功能在业务上想解决什么问题
2. 再找这个功能从哪里进入
3. 再追它经过了谁
4. 最后才看内部细节实现

## 每次读代码只问 3 个问题

1. 输入是什么
2. 中间经过谁
3. 输出给谁

例如看 `useOwnerDashboardView.ts`：

- 输入：区域、预约窗口、用户 ID、可选的订单上下文
- 中间经过：`fetchOwnerDashboard()`、网关、owner dashboard controller
- 输出：页面要显示的推荐、最新订单、视图状态

## 新手最容易混淆的地方

### 1. 把页面和业务逻辑看成同一层

在这个项目里，页面负责展示，很多逻辑被下沉到了 composable 或 service。

### 2. 把 controller 当成“后端所有逻辑都在这里”

controller 在很多时候只是入口。真正的数据查询、组装、账单计算、模型切换，往往在后面的 service / assembler / facade 中。

### 3. 把当前主线和历史实现混在一起

当前默认主线是 Step40，不是早期的 Python 版 `services/parking_service.py`。

## 什么时候该用 `chains`，什么时候看 `weeks`

- 你想知道系统大概长什么样：先看 `weeks`
- 你想真的追一条代码链：看 `chains`
- 你想确认自己会没会：做 `labs`
