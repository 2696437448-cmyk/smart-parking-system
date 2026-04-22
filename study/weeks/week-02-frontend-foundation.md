# 第 2 周：前端基础与页面分层

## 本周目标

- 看懂前端入口、路由和页面结构
- 分清页面组件、页面逻辑、请求层三者的职责
- 理解这个前端为什么不是“把所有逻辑都写在页面里”
- 认识最终版本里的 UI 壳层、统一组件和页面命名

## 你会先看哪些文件

- `apps/frontend/src/main.ts`
- `apps/frontend/src/theme/arco.ts`
- `apps/frontend/src/router.ts`
- `apps/frontend/src/layouts/OwnerLayout.vue`
- `apps/frontend/src/layouts/AdminLayout.vue`
- `apps/frontend/src/pages/OwnerDashboard.vue`
- `apps/frontend/src/pages/OwnerOrders.vue`
- `apps/frontend/src/pages/OwnerNavigation.vue`
- `apps/frontend/src/pages/AdminMonitor.vue`
- `apps/frontend/src/components/MetricCard.vue`
- `apps/frontend/src/components/SectionHeader.vue`
- `apps/frontend/src/components/ViewStateNotice.vue`
- `apps/frontend/src/composables/useOwnerDashboardView.ts`
- `apps/frontend/src/composables/useAdminDashboardView.ts`

## 这部分代码到底在做什么

前端现在已经做了比较清晰的分层，你可以先记住 4 层：

1. `应用壳层`
   负责应用启动、主题、组件库接入和全局动效，比如 `main.ts`、`theme/arco.ts`
2. `页面层`
   负责模板和结构展示，比如 `OwnerDashboard.vue`、`AdminMonitor.vue`
3. `页面逻辑层`
   负责状态、加载、错误处理、按钮动作，比如 `useOwnerDashboardView.ts`
4. `请求层`
   负责真正去请求后端接口，比如 `services/owner.ts` 和 `services/admin.ts`

这套分层的核心好处是：  
页面文件不需要自己同时处理“发请求、管状态、做跳转、拼数据、渲染 UI”。

同时，最终版本又在页面层之上补了一层比较明确的“展示组件复用”：

- `MetricCard.vue`
  负责摘要卡片和数字卡片
- `SectionHeader.vue`
  负责区块标题、标签和副标题
- `ViewStateNotice.vue`
  负责 loading / empty / error / degraded / stale 等统一状态表达

### 当前主线

- `main.ts` 创建 Vue 应用，并接入 Arco Design Vue 与动效插件
- `router.ts` 决定 URL 对应哪个页面
- `layouts/*.vue` 决定 owner / admin 两类页面壳层
- `pages/*.vue` 决定页面长什么样
- `composables/*.ts` 决定页面怎么工作

### 最终页面怎么理解

- `OwnerDashboard.vue`
  页面标题可以理解成“首页”，它是业主端的推荐入口页
- `OwnerOrders.vue`
  页面标题可以理解成“订单”，它承接预约后的状态确认和结算
- `OwnerNavigation.vue`
  页面标题可以理解成“导航”，它承接同一个 `orderId` 的到达阶段
- `AdminMonitor.vue`
  页面标题可以理解成“物业监管”，它是物业端的一屏总览页

### 历史保留或次要内容

- `dist/` 是构建产物，不是学习主入口
- `node_modules/` 不需要读

## 一条必须跟读的调用链

这周建议你只跟 `Owner Dashboard` 这条前端链路：

1. `main.ts` 启动 Vue 应用，并注册主题与统一组件体系
2. `router.ts` 把 `/owner/dashboard` 路由到 `OwnerDashboard.vue`
3. `OwnerLayout.vue` 提供业主端左侧切换、页头状态和移动端底部导航
4. `OwnerDashboard.vue` 引入 `useOwnerDashboardView()`
5. `useOwnerDashboardView.ts` 在 `onMounted` 时加载数据
6. 它调用 `fetchOwnerDashboard()`
7. 页面根据拿到的数据展示推荐车位、最近订单和统一状态提示

## 给新手的概念解释

### 什么是 composable

在 Vue 3 里，composable 可以理解成“可复用的页面逻辑函数”。  
它不是页面本身，而是把页面里那些容易变复杂的逻辑抽出来，比如：

- 什么时候加载数据
- 请求成功或失败怎么办
- 页面上按钮点击后执行什么动作
- 页面处于 loading、error 还是 empty

### 什么是页面状态表达

这个项目没有让每个页面自己随便写一套状态提示，而是统一用了：

- `useViewState.ts`
- `ViewStateNotice.vue`

这说明作者在做一个比较规范的前端，不想让每个页面各写各的提示逻辑。

### 什么是最终版本里的页面壳层

当前版本的重点不是把页面做得很炫，而是让结构更清楚、信息更集中。你可以先记住三件事：

- Arco 亮色主题和统一状态标签
- owner / admin 两套明确的页面壳层
- 摘要卡片、标题区、图表卡片、地图卡片的统一外观

所以你读代码时不要只看 `pages/*.vue`，还要记得一起看：

- `styles/layout.css`
- `styles/components.css`
- `styles/pages.css`

## 本周可直接运行的命令

```bash
# 启动前端开发环境
cd apps/frontend
npm run dev

# 或者构建一次，确认前端能正常打包
npm run typecheck
npm run build

# 如果你想看最终业务页面，而不是开发服务
cd ../..
./scripts/defense_demo.sh start
```

运行后，重点打开：

- `http://localhost:5173/owner/dashboard`
- `http://localhost:5173/admin/monitor`

如果你走的是整套演示环境，优先看：

- `http://localhost:4173/owner/dashboard`
- `http://localhost:4173/admin/monitor`

如果你是配合整套服务一起看，也可以用 README 里的 `4173` 预览口径。

## 本周小练习

1. 写出 `页面层 / composable / 请求层` 分别负责什么。
2. 从 `OwnerDashboard.vue` 往下追，找出它到底是在哪里发起请求的。
3. 比较 `OwnerDashboard.vue` 和 `AdminMonitor.vue`，看看两者页面逻辑是不是都尽量放到了 composable 里。
4. 找出 `MetricCard.vue`、`SectionHeader.vue`、`ViewStateNotice.vue` 分别在页面里承担什么展示职责。

## 本周完成标准

- 你能解释为什么页面文件比较“薄”
- 你能从页面追到 composable，再追到请求函数
- 你知道前端当前的主角不是单个 `.vue` 文件，而是“主题 / 页面壳层 + 页面 + composable + service”一起工作

## 可选加深阅读

- `apps/frontend/src/components/ViewStateNotice.vue`
- `apps/frontend/src/composables/useViewState.ts`
- `reports/step38_execution.md`

## 继续深入

前端入口和请求链的详细带读请继续：

- `../chains/chain-01-owner-dashboard-request.md`
- `../labs/lab-01-owner-dashboard.md`
