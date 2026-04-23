# 从这里开始

这份文档是给第一次系统读 `smart-parking-thesis` 的人准备的。目标不是让你背技术栈，而是让你先进入正确的学习顺序。

## 你现在最容易犯的 4 个错误

1. 一上来就从最长的 Java 文件开始啃
2. 同时看前端、网关、模型、实时服务，结果每条链都只懂一点点
3. 把当前主线和历史保留实现混在一起
4. 只看不写、不跑、不验证，最后以为自己懂了

## 正确起手顺序

推荐这样开始：

1. 先看 [guide/how-to-read-this-project.md](./how-to-read-this-project.md)
2. 再看 [guide/file-map.md](./file-map.md)
3. 然后直接进入 [chains/README.md](../chains/README.md)
4. 从 `chain-01` 开始，不要跳过第一条链
5. 学完一条链，立刻做对应的 `lab`

## 为什么不建议直接从 `weeks/` 开始

`weeks/` 的作用是帮你知道“学什么”，不是帮你真正跟代码。它很适合建立地图，但不适合一个人硬啃源码。

如果你已经发现：

- 我知道要看哪些文件，但还是不懂
- 我能大概说出模块名，但不会追调用链
- 我看完后不知道自己到底会了没有

那就说明你应该进入 `chains/ + labs/` 体系，而不是继续在 `weeks/` 里加阅读量。

## 第一个 90 分钟怎么学

如果你今天只打算花 90 分钟，推荐这样分配：

1. 15 分钟：看 [guide/file-map.md](./file-map.md)
2. 35 分钟：读 [chains/chain-01-owner-dashboard-request.md](../chains/chain-01-owner-dashboard-request.md)
3. 20 分钟：打开真实文件，按步骤定位一次
4. 20 分钟：做 [labs/lab-01-owner-dashboard.md](../labs/lab-01-owner-dashboard.md) 前 3 题

## 卡住时怎么退回

如果你开始迷路，不要全项目乱翻，按这个顺序退回：

1. 回到当前 `chain` 的“场景故事”和“跟读路线”
2. 回到 [guide/how-to-read-this-project.md](./how-to-read-this-project.md)
3. 回到 [guide/file-map.md](./file-map.md)
4. 最后才回到 `weeks/` 找概念补充
