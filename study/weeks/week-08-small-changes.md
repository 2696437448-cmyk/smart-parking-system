# 第 8 周：新手可做的小改动

## 本周目标

- 把“会看”升级成“敢动一点”
- 学会定位入口、判断改动位置和验证方式
- 完成 1-3 个非常小、风险可控的改动练习

建议这一周配合下面这份清单一起使用：

- `study/templates/small-change-checklist.md`

## 你会先看哪些文件

- `apps/frontend/src/pages/OwnerDashboard.vue`
- `apps/frontend/src/composables/useOwnerDashboardView.ts`
- `apps/frontend/src/composables/useViewState.ts`
- `services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewModules.java`
- `apps/frontend/src/pages/AdminMonitor.vue`
- `apps/frontend/src/services/http.ts`

## 这部分代码到底在做什么

这一周不是让你做大需求，而是教你怎么做 `新手友好的小改动`。

最核心的能力不是写多少代码，而是先判断：

- 这是前端展示问题吗
- 这是接口数据结构问题吗
- 这是后端业务规则问题吗
- 这是实时状态问题吗

### 新手优先改哪类问题

优先顺序建议如下：

1. 页面文案、说明文字、按钮文案
2. 页面上已有字段的展示方式
3. dashboard 已有字段的排序或组合
4. 简单的默认值或提示信息

暂时不要先碰：

- 网关熔断配置
- 并发一致性逻辑
- 模型服务核心算法
- ETL 主流程结构

## 一条必须跟读的调用链

这周建议你跟一条“页面字段显示”改动链：

1. 在页面上看到一个文案或字段显示
2. 找到对应的 `.vue` 页面文件
3. 如果页面里只是展示，再去找对应 composable
4. 如果 composable 只是透传数据，再去找对应 service 请求
5. 如果数据本身不对，再去找后端 view-model 组装位置
6. 改动后重新跑页面或最小验证

## 给新手的概念解释

### 什么是最小可验证改动

意思是：  
一次只改一小块，并且改完后能马上验证结果。  
比如改一行展示文案，比同时改 5 个服务更适合入门。

### 为什么先改 view-model 和展示层

因为这类改动影响范围更小、反馈更快，也更容易建立“我真的能改动这个项目”的信心。

### 什么叫判断改前端还是后端

你可以先问自己：

- 页面拿到的数据是对的，只是显示不理想？优先改前端
- 页面拿到的数据结构就不合适？优先改后端 view-model
- 请求根本失败或字段缺失？先追接口链路

## 本周可直接运行的命令

```bash
# 启动整套环境
./scripts/defense_demo.sh start

# 前端类型检查与构建
cd apps/frontend
npm run typecheck
npm run build
cd ../..

# 默认 Step40 验收
python3 scripts/test_step40_release_acceptance.py
```

## 本周小练习

1. 任选一个页面，找出它的“展示层入口”和“逻辑层入口”。
2. 在不真的修改代码的前提下，写出如果你要改一个文案，应该先看哪 3 个文件。
3. 选择 owner dashboard 或 admin monitor，写出“如果字段不对，我该怎么定位”的排查顺序。
4. 为自己列出 3 个未来可以尝试的小改动题目。

## 本周完成标准

- 你知道小改动应该优先挑哪类问题
- 你能从页面一路反查到后端聚合层
- 你知道改完后至少要做哪些最小验证

## 可选加深阅读

- `reports/step37_execution.md`
- `reports/step38_execution.md`
- `reports/step39_execution.md`

## 继续深入

准备动手前，建议先回看最相关的主链并完成对应练习：

- owner 相关：`../chains/chain-02-owner-order-billing-navigation.md` + `../labs/lab-02-owner-business.md`
- admin 相关：`../chains/chain-03-admin-dashboard-realtime.md` + `../labs/lab-03-admin-realtime.md`

