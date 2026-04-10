# 第 7 周：验收、报告与答辩表达

## 本周目标

- 理解这个项目是如何证明自己“做完了”的
- 看懂验收脚本、OpenAPI、报告、交付物之间的关系
- 学会把源码阅读结果转成答辩表达

## 你会先看哪些文件

- `openapi/smart-parking.yaml`
- `scripts/defense_demo.sh`
- `scripts/test_step40_release_acceptance.py`
- `reports/step40_technical_acceptance.md`
- `reports/thesis_evidence_package.md`
- `docs/defense_demo_runbook.md`
- `deliverables/README.md`

## 这部分代码到底在做什么

很多课程项目只做到“代码能跑”。  
但这个项目还做了另外几层东西：

- `OpenAPI`
  说明接口合同是什么
- `acceptance scripts`
  说明系统如何自动验证
- `reports`
  说明每一步结果怎么记录
- `deliverables`
  说明最终怎么打包交付

这意味着它不仅是一个代码仓库，也是一个“可展示、可验收、可答辩”的项目。

### OpenAPI 在这里的意义

它不是摆设。  
特别是 owner/admin dashboard 接口，在 Step38 之后已经被正式纳入合同。  
这说明前后端不只是“口头约定”，而是有明确的接口结构。

### 验收脚本在这里的意义

验收脚本解决的是：  
项目不能只靠肉眼说“好像能跑”，还要有一套能重复执行的检查方式。

### 报告在这里的意义

报告不是重复 README，而是为了回答：

- 做了什么
- 怎么验证
- 结果如何
- 当前完成态到哪一步

## 一条必须跟读的调用链

这周跟一条“代码到验收”的链：

1. 开发完成 Step40 当前主线
2. `test_step40_release_acceptance.py` 负责执行默认验收
3. `defense_demo.sh` 提供演示和验收入口
4. `reports/step40_technical_acceptance.md` 记录结果
5. `deliverables/` 负责最终交付包

## 给新手的概念解释

### 什么是接口合同

接口合同就是“前后端都认的一份数据约定”。  
比如请求参数叫什么、返回结构里必须有哪些字段。  
这个项目里主要用 `openapi/smart-parking.yaml` 来表达。

### 什么是 acceptance

acceptance 可以理解成“最终验收”。  
它不是单个单元测试，而是验证系统整体功能和完成态的一组检查。

### 为什么答辩项目需要报告

因为答辩不是只展示页面，还要解释：

- 架构为什么这么设计
- 如何证明系统能工作
- 哪些改动是在哪一步完成的

## 本周可直接运行的命令

```bash
# 启动环境
./scripts/defense_demo.sh start

# 运行默认 Step40 验收
./scripts/defense_demo.sh acceptance

# 或直接运行默认验收脚本
python3 scripts/test_step40_release_acceptance.py

# 构建交付包
make release-bundle
```

## 本周小练习

1. 找出 `openapi/smart-parking.yaml` 中 owner dashboard 和 admin dashboard 的定义位置。
2. 用自己的话解释：README、report、deliverable 三者分别面向谁。
3. 打开 `docs/defense_demo_runbook.md`，写出答辩演示最重要的两个入口页面。

## 本周完成标准

- 你能解释为什么这个项目不只是“代码仓库”，也是“交付物仓库”
- 你知道默认验收入口是什么
- 你能把架构、功能、验收和答辩材料串起来讲

## 可选加深阅读

- `reports/step38_execution.md`
- `reports/step39_execution.md`
- `memory-bank/implementation-plan.md`

## 继续深入

系统验收口径与模型链收口请继续：

- `../chains/chain-04-etl-model-registry-acceptance.md`
- `../labs/lab-04-model-etl.md`

