# Smart Parking 前端高级化重构设计

- 日期：2026-04-20
- 项目：`smart-parking-thesis`
- 当前基线：`Step40`
- 设计状态：已确认，可进入实现计划

## 1. 背景

`smart-parking-thesis` 当前已经形成以 `Step40` 为默认完成态的系统基线，核心业务链路、聚合接口、实时通道、前端页面与验收脚本均已具备较完整的交付形态。前端侧保留了四个主要业务页面：`OwnerDashboard`、`OwnerOrders`、`OwnerNavigation`、`AdminMonitor`，并通过 `OwnerLayout` 与 `AdminLayout` 完成业主端和物业端的布局分层。

从代码组织上看，当前前端已经完成了第一轮现代化改造，包括样式分层、页面级 composable、dashboard 聚合接口消费、统一状态表达和路由懒加载。这一基础是成立的，不需要推倒重来。当前真正需要解决的问题，不是功能缺失，而是“成品感”和“表达层结构”仍有继续收紧的空间。

结合仓库现状、论文要求与用户确认，本轮工作不再新增答辩专用页面，不改变现有路由和页面结构，而是在既有结构上完成一次高级化重构：页面视觉更成熟，状态表达更贴合业务语境，展示代码与编排代码边界更清晰，最终形成可以直接作为毕业论文最终版本依据的系统实现。

## 2. 问题陈述

当前前端的主要问题集中在以下几个方面。

第一，页面虽然已经具备统一组件和样式分层，但整体视觉层级仍偏平。业主端首页、订单页、导航页和物业端监控页都能用，但主次关系、信息节奏、重点提示和卡片层级还不够鲜明，容易给人“功能完整但展示略像阶段作品”的感觉。

第二，页面中的视图解释逻辑仍然有一定分散。部分金额、百分比、时间、状态文案、badge 内容和图表 option 直接分布在页面或 composable 内部，导致页面文件承担了部分展示解释职责。这样虽然不影响运行，但不利于继续维护，也不利于在论文中自然描述“前端页面编排层”和“展示层”的边界。

第三，统一状态表达已经建立，但不同页面的状态文案还不够贴业务。`loading / ready / empty / error / degraded / stale` 这套语义是正确的，不过在业主端和物业端上还可以进一步做语境化处理，让提示更像系统的一部分，而不是一张通用状态卡。

第四，图表、地图和摘要面板目前是功能可用的，但解释层仍然偏薄。物业端图表区更像一组图表集合，业主端地图区更像单独的地图组件展示，距离“面向真实使用场景的信息视图”还可以再推进一步。

## 3. 目标

本次重构的目标如下。

1. 保持现有页面结构和主要业务路径不变，在不新增答辩专用页面的前提下，提升整体视觉完成度。
2. 让业主端四类核心信息，即推荐、预约、订单、导航，形成更连续的旅程感。
3. 让物业端经营摘要、图表、状态、解释信息形成更清楚的层级，而不是平铺展示。
4. 保留并强化统一状态表达，让状态卡根据页面语境提供更自然的提示。
5. 继续下沉展示解释逻辑，把格式化、摘要文案和图表配置从页面主体中抽离，缩小页面文件职责。
6. 在不改变 Gateway、Parking Service、owner/admin dashboard 合同语义的前提下完成前端高级化重构。
7. 为后续最终论文写作提供稳定的“最终实现口径”，使论文可以直接围绕最终版本展开，而不必描述版本迭代历史。

## 4. 非目标

以下内容不属于本轮重构范围。

1. 不新增新的业务页面、总览页或答辩专用展示页。
2. 不修改现有路由结构，不改变 `OwnerLayout` / `AdminLayout` 的角色划分。
3. 不改动 Spark、LSTM-Lite、Hungarian、停车预约一致性主链等核心业务语义。
4. 不对后端接口做破坏性修改，不重写 owner/admin dashboard 聚合接口。
5. 不把本轮优化做成整体架构重构，不引入新的前端框架或状态管理方案。

## 5. 备选方案比较

本次设计阶段考虑了三种路线。

方案一是轻量视觉升级，只调整样式与局部组件观感。这条路线风险低、执行快，但代码结构改善有限，最终只能解决“好不好看”的一部分问题，无法充分支撑论文中对前端工程化的自然描述。

方案二是在保留页面结构的前提下，做体验优先的高级化重构。该方案同时处理视觉层、组件层和页面编排层，既不推翻现有实现，也能显著提升系统完成度。它兼顾展示效果与可维护性，且与用户“前者优先、两者都做”的要求完全一致。

方案三是深度架构重整，包括更大范围的前后端 view-model 与聚合接口调整。该方案结构收益更大，但风险和实施成本都更高，且容易偏离当前阶段目标。

最终选定方案二，作为本轮实现依据。

## 6. 总体设计

本轮设计的总原则是“业务结构不动，展示表达升级，页面职责收紧”。

前端保留现有四个页面和两套 layout，不新增新页面，不改变页面顺序与路由入口。视觉系统继续沿用 `tokens/base/layout/components/pages` 五层样式组织方式，但补齐更明确的语义 token，用于区分页面背景、主面板、次级卡片、状态提示、图表容器、表单区、强调指标和交互按钮。这样做的目标不是单纯换配色，而是建立稳定的展示层级。

在组件层，保留现有的 `SectionHeader`、`MetricCard`、`ViewStateNotice`、`EChartPanel`、`MapPreview`，并升级它们的表现能力。同时新增三个轻量通用组件，用于承接页面中反复出现的结构化展示模式：`ActionBar.vue` 负责主要动作与辅助动作排布，`KeyValueList.vue` 负责有语义顺序的详情列表展示，`StatusBadge.vue` 负责统一色调的业务状态标签。新增组件数量控制在最小必要范围，避免为了组件化而组件化。

在页面编排层，保留现有 composable 作为主入口，但继续缩小页面和 composable 中的展示解释职责。页面只负责结构组合，composable 负责业务编排，新增 `presenters` 目录承接数值格式化、页面摘要文案、图表 option 构造和 badge 文本映射。这样可以让页面代码更接近“声明式结构”，也让论文中的前端设计描述更自然。

## 7. 文件范围

本轮允许修改的核心文件如下。

### 7.1 样式与布局

1. `apps/frontend/src/styles/tokens.css`
2. `apps/frontend/src/styles/base.css`
3. `apps/frontend/src/styles/layout.css`
4. `apps/frontend/src/styles/components.css`
5. `apps/frontend/src/styles/pages.css`
6. `apps/frontend/src/layouts/OwnerLayout.vue`
7. `apps/frontend/src/layouts/AdminLayout.vue`

### 7.2 现有组件升级

1. `apps/frontend/src/components/SectionHeader.vue`
2. `apps/frontend/src/components/MetricCard.vue`
3. `apps/frontend/src/components/ViewStateNotice.vue`
4. `apps/frontend/src/components/EChartPanel.vue`
5. `apps/frontend/src/components/MapPreview.vue`

### 7.3 新增轻量组件

1. `apps/frontend/src/components/ActionBar.vue`
2. `apps/frontend/src/components/KeyValueList.vue`
3. `apps/frontend/src/components/StatusBadge.vue`

### 7.4 页面与编排层

1. `apps/frontend/src/pages/OwnerDashboard.vue`
2. `apps/frontend/src/pages/OwnerOrders.vue`
3. `apps/frontend/src/pages/OwnerNavigation.vue`
4. `apps/frontend/src/pages/AdminMonitor.vue`
5. `apps/frontend/src/composables/useOwnerDashboardView.ts`
6. `apps/frontend/src/composables/useAdminDashboardView.ts`
7. `apps/frontend/src/composables/useViewState.ts`
8. `apps/frontend/src/composables/useRealtimeChannel.ts`

### 7.5 新增展示解释层

1. `apps/frontend/src/presenters/format.ts`
2. `apps/frontend/src/presenters/owner.ts`
3. `apps/frontend/src/presenters/admin.ts`

除上述范围外，不主动扩展到后端服务与聚合接口实现。如确有必要，只允许做非破坏性类型对齐，但默认目标是不改后端。

## 8. 页面级设计

### 8.1 OwnerDashboard

保持现有“三段式”结构，即首页主卡、预约参数区、推荐车位区，但强化主次关系。首页主卡应成为用户进入系统后的主要焦点，负责承接当前区域、推荐摘要、最近订单和下一步动作。预约参数区仍保留，但其展示优先级低于主卡与推荐结果。推荐车位区保留卡片式列表，但每张推荐卡要更清楚地表达车位名、区域、预计费用、预计到达时间和操作意图，使其更像“可直接决策的候选项”。

### 8.2 OwnerOrders

保持订单与账单页面结构不变，但把“订单状态、预估金额、最终金额、结算信息、导航入口”组织成更清楚的阅读顺序。金额信息应成为主要指标，状态与账单规则作为解释信息跟随展示。结算操作按钮继续保留，但其位置和视觉层级要明确为当前页主要动作。

### 8.3 OwnerNavigation

继续采用“说明卡 + 地图卡”双区结构。说明卡需要更完整地展示订单号、目标车位、区域、ETA、路线摘要和距离信息；地图卡则保持页面内预览与外部地图跳转并存。地图区域应更接近成品页展示，而不是纯演示控件。

### 8.4 AdminMonitor

保持现有“经营主卡 + 摘要区 + 图表区”结构，但进一步加强层级。主卡负责当前模式、数据来源、刷新动作与状态说明；摘要区负责经营 highlights 与诊断入口；图表区则在每个图表内部补充更清楚的标题、副标题和解释说明，使其从“可视化组件集合”提升为“可阅读的经营视图”。

## 9. 状态与数据流设计

统一状态语义仍然采用 `loading / ready / empty / error / degraded / stale`，不引入第二套状态机。`useViewState.ts` 的核心语义保持不变，但需要补强页面语境化表达，使业主端更偏向用户旅程提示，物业端更偏向业务监控说明。

`useOwnerDashboardView.ts` 与 `useAdminDashboardView.ts` 继续作为页面级编排入口，不负责大面积视觉解释。新增的 `presenters` 文件承担以下职责：金额、百分比、时间与 trace 说明格式化；图表 option 构造；状态标题与说明拼接；摘要 badge 与 highlights 文案映射。这样可以避免页面和 composable 同时承担过多展示解释逻辑。

`useRealtimeChannel.ts` 的实时优先、Polling 回退、手动重连语义保持不变。本轮只增强页面感知层，不改变通道策略本身。正常实时状态要明确表达为“当前数据处于实时同步中”，降级状态要表达为“实时链路不可用但业务视图仍在更新”，`stale` 状态要表达为“建议刷新”，而不是表现成错误。

## 10. 视觉系统设计

视觉升级采用“保留当前暖色与青色混合基调，但提升层级和节奏”的策略。业主端强调连续旅程与移动优先体验，因此主卡、推荐卡和操作按钮会更集中、更有方向感；物业端强调经营视图和监控稳定性，因此图表面板、摘要卡和状态条需要更稳重、更具信息层级。

具体设计约束如下。

1. 保持明亮主题，不切换为深色主界面。
2. 保留现有项目色相方向，不引入与当前系统不一致的高饱和跳色。
3. 强化标题、数值、说明文字和辅助标签的字号节奏。
4. 增加主面板与次级卡片的明暗、描边和投影差异，但避免堆叠过重视觉效果。
5. 移动端优先策略继续保留，桌面端则提升横向布局平衡和视线引导。

## 11. 实施顺序

实现必须按以下顺序推进。

1. 先完成样式 token、基础样式和通用组件升级，建立统一视觉系统。
2. 再改造四个业务页面，使其在既有结构下完成高级化重构。
3. 随后收敛 composable 与 presenter 层，把格式化、图表配置和摘要文案迁移出去。
4. 最后进行类型检查、构建验证和 gate 回归，确认不破坏 `Step40` 默认完成态。

该顺序的目的，是先稳定展示语言，再缩小页面职责，最后做全量验收，避免边改边散。

## 12. 验收标准

本轮实现完成后，至少需要满足以下验收条件。

1. `npm run typecheck` 通过。
2. `npm run build` 通过，且不引入新的 ECharts chunk warning 退化。
3. 前端相关脚本通过：
   - `python3 scripts/test_step21_frontend_pages.py`
   - `python3 scripts/test_step27_app_shell.py`
   - `python3 scripts/test_step29_admin_charts.py`
   - `python3 scripts/test_step37_prompt_frontend_modernization.py`
   - `python3 scripts/test_step39_dashboard_hardening.py`
4. 若运行时环境可用，则 `python3 scripts/test_step40_release_acceptance.py` 继续通过。
5. owner/admin 页面路由不变、核心交互不变、聚合接口消费语义不变。
6. 页面状态表达必须保持统一，不允许某个页面重新写出一套脱离 `useViewState` 的状态体系。

## 13. 风险与控制

本轮主要风险有三个。

第一，视觉升级如果只落在样式层，容易形成“看起来更精致，但代码还是散”的结果。为控制这一风险，必须同时完成 `presenters` 层收敛。

第二，组件抽象如果过度，容易增加阅读成本。为控制这一风险，新增组件严格限制为 `ActionBar`、`KeyValueList`、`StatusBadge` 三个轻量组件，不扩大到通用容器滥用。

第三，页面结构不变会限制大幅重排空间。为控制这一风险，本轮通过强化主次关系、说明层和展示节奏来获得高级化效果，而不是试图靠新增页面解决问题。

## 14. 论文联动约束

本轮实现完成并冻结后，论文必须以最终系统版本为唯一写作对象，不写“优化前后”“更新后”“本次新增”等版本化表述，避免生成感和过程感过重。

论文正文应从第一章绪论写到第六章总结，正文总字数不少于 12000 字，总页数不少于 35 页。正文扩展方式应以需求分析、总体设计、详细实现、状态与降级设计、页面实现、测试分析等实质内容为主，不依赖大段代码粘贴撑篇幅。

根据学校要求，正文中不出现整页整页代码。若确需展示代码，只允许使用关键代码截图，并配以简要说明。论文中的图、表和页面截图应优先选取最终系统的稳定界面与关键流程，不展示临时调试状态。

本轮实现完成后，论文材料需要至少更新以下内容：

1. `docs/thesis-docs/thesis-draft.md`，作为最终正文基础稿。
2. `docs/thesis-docs/generate_final_docx.py` 的文稿输入与配图口径，确保最终导出的说明书对齐实现结果。
3. 与正文配套的图示、页面截图和代码截图清单，确保第 3 至第 5 章能够直接引用最终版本素材。

## 15. 通过条件

当且仅当以下条件同时满足时，本设计视为完成并可进入实现计划阶段。

1. 用户确认本设计文档。
2. 设计文档已写入仓库并完成自检。
3. 设计文档已单独提交，不与业务实现混杂。
4. 后续工作严格先进入实现计划，再进入代码实现，最后再写最终论文。
