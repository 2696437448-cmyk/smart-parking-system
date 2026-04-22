# 新手怎么读这个项目的代码

这份文档不是讲某个具体模块，而是告诉你：  
面对一个像 `smart-parking-thesis` 这样多技术栈、多服务的项目时，新手到底应该怎么读代码，才不容易迷路。

## 先记住一个总原则

不要从“最长的文件”开始读。  
要从“最能说明调用关系的入口文件”开始读。

在这个项目里，最值得优先看的入口通常是：

- 前端入口：`apps/frontend/src/main.ts`
- 路由入口：`apps/frontend/src/router.ts`
- 网关入口：`services/gateway-service/src/main/java/com/smartparking/gateway/GatewayServiceApplication.java`
- 业务主服务入口：`services/parking-service/src/main/java/com/smartparking/parking/ParkingServiceApplication.java`
- 模型服务入口：`services/model_service.py`
- 实时服务入口：`services/realtime_service.py`
- 整体运行入口：`infra/docker-compose.yml`

## 推荐阅读顺序

每次都尽量按这个顺序：

1. 先看文档
2. 再看入口文件
3. 再看调用链
4. 最后才看细节实现

### 第 1 步：先看文档

先回答这 3 个问题：

1. 这个模块是干什么的？
2. 它在系统里的位置是什么？
3. 它和谁协作？

对应可先看：

- `README.md`
- `study/appendix/file-map.md`
- 当前周讲义

### 第 2 步：再看入口文件

入口文件的意义是：告诉你“从哪里开始走”。  
比如：

- 前端页面怎么被路由出来
- 后端接口从哪里进入
- 服务从哪里启动

### 第 3 步：再看调用链

调用链就是“这个需求是怎样一步步传下去的”。  
例如：

- 页面 -> composable -> service -> gateway -> parking-service
- dashboard controller -> query service -> assembler
- ETL -> 训练 -> registry -> model-service

### 第 4 步：最后看细节实现

只有在你已经知道这段代码在整个系统里干什么之后，再去读细节，效率才高。

## 每次读一个模块，只问 3 个问题

无论你看的是函数、类、组件还是脚本，都先回答：

1. 它输入什么？
2. 它输出什么？
3. 它依赖谁？

比如看 `useOwnerDashboardView.ts`，你就可以这样想：

- 输入：当前用户、区域、时间窗口、订单上下文
- 输出：页面需要的状态、推荐结果、动作函数
- 依赖：`fetchOwnerDashboard()`、`reserveOwnerSlot()`、`useOrderContext()`

## 新手最容易犯的 5 个错误

### 1. 一上来就读最长的文件

结果通常是：  
看了很多行，但不知道它在系统里处于什么位置。

### 2. 同时追很多支线

例如一边看前端、一边看模型训练、一边看实时服务。  
这样很容易全都“好像看过”，但没一条真正看懂。

### 3. 不区分当前主线和历史遗留

这个项目里最典型的例子就是：

- 当前主线：`services/parking-service`
- 历史保留：`services/parking_service.py`

如果混着看，会非常容易误解当前系统真实结构。

### 4. 看实现前不先看接口和返回结构

例如 dashboard 页面，先看：

- 页面怎么调接口
- 接口返回结构长什么样

再去看后端怎么组装，会清楚很多。

### 5. 只看不写

如果你不写笔记、不画调用链、不复述，大脑会很快把细节混在一起。  
所以建议配合：

- `study/templates/weekly-note-template.md`

## 一个实用的阅读法：一条链读到底

每次只选一条链，比如：

- Owner Dashboard
- 预约主链
- Admin Dashboard
- 实时降级链
- ETL 到模型注册表

然后按顺序读到底，不中途切到别的主题。

## 推荐的最小阅读成果

每读完一条链，至少留下这 4 样东西：

1. 一句总结：这条链在做什么
2. 3-8 个关键文件
3. 一张简化调用顺序
4. 一个你还没完全懂的问题

## 如果你卡住了，怎么排查

先按这个顺序回退：

1. 回到对应周讲义
2. 回到入口文件
3. 回到调用链的上一个节点
4. 看接口输入输出，而不是先死啃内部实现

## 最后一句建议

把自己当成“调查员”，不是“背代码的人”。  
你的目标不是把每一行都记住，而是逐渐建立：  
`我知道这个功能从哪进、往哪走、出问题该先查哪。`
