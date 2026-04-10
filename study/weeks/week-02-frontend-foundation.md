# 第 2 周：前端基础与页面分层

## 本周目标

- 看懂前端入口、路由和页面结构
- 分清页面组件、页面逻辑、请求层三者的职责
- 理解这个前端为什么不是“把所有逻辑都写在页面里”

## 你会先看哪些文件

- `apps/frontend/src/main.ts`
- `apps/frontend/src/router.ts`
- `apps/frontend/src/pages/OwnerDashboard.vue`
- `apps/frontend/src/pages/OwnerOrders.vue`
- `apps/frontend/src/pages/OwnerNavigation.vue`
- `apps/frontend/src/pages/AdminMonitor.vue`
- `apps/frontend/src/composables/useOwnerDashboardView.ts`
- `apps/frontend/src/composables/useAdminDashboardView.ts`

## 这部分代码到底在做什么

前端现在已经做了比较清晰的分层，你可以先记住 3 层：

1. `页面层`
   负责模板和展示，比如 `OwnerDashboard.vue`、`AdminMonitor.vue`
2. `页面逻辑层`
   负责状态、加载、错误处理、按钮动作，比如 `useOwnerDashboardView.ts`
3. `请求层`
   负责真正去请求后端接口，比如 `services/owner.ts` 和 `services/admin.ts`

这套分层的核心好处是：  
页面文件不需要自己同时处理“发请求、管状态、做跳转、拼数据、渲染 UI”。

### 当前主线

- `main.ts` 创建 Vue 应用
- `router.ts` 决定 URL 对应哪个页面
- `pages/*.vue` 决定页面长什么样
- `composables/*.ts` 决定页面怎么工作

### 历史保留或次要内容

- `dist/` 是构建产物，不是学习主入口
- `node_modules/` 不需要读

## 一条必须跟读的调用链

这周建议你只跟 `Owner Dashboard` 这条前端链路：

1. `main.ts` 启动 Vue 应用
2. `router.ts` 把 `/owner/dashboard` 路由到 `OwnerDashboard.vue`
3. `OwnerDashboard.vue` 引入 `useOwnerDashboardView()`
4. `useOwnerDashboardView.ts` 在 `onMounted` 时加载数据
5. 它调用 `fetchOwnerDashboard()`
6. 页面根据拿到的数据展示推荐车位、最近订单和状态提示

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

## 本周可直接运行的命令

```bash
# 启动前端开发环境
cd apps/frontend
npm run dev

# 或者构建一次，确认前端能正常打包
npm run typecheck
npm run build
```

运行后，重点打开：

- `http://localhost:5173/owner/dashboard`
- `http://localhost:5173/admin/monitor`

如果你是配合整套服务一起看，也可以用 README 里的 `4173` 预览口径。

## 本周小练习

1. 写出 `页面层 / composable / 请求层` 分别负责什么。
2. 从 `OwnerDashboard.vue` 往下追，找出它到底是在哪里发起请求的。
3. 比较 `OwnerDashboard.vue` 和 `AdminMonitor.vue`，看看两者页面逻辑是不是都尽量放到了 composable 里。

## 本周完成标准

- 你能解释为什么页面文件比较“薄”
- 你能从页面追到 composable，再追到请求函数
- 你知道前端当前的主角不是单个 `.vue` 文件，而是“页面 + composable + service”一起工作

## 可选加深阅读

- `apps/frontend/src/components/ViewStateNotice.vue`
- `apps/frontend/src/composables/useViewState.ts`
- `reports/step38_execution.md`

## 继续深入

前端入口和请求链的详细带读请继续：

- `../chains/chain-01-owner-dashboard-request.md`
- `../labs/lab-01-owner-dashboard.md`

