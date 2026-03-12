# Git 工作流（强制执行）

## 1. 目的与适用范围

1. 目的：保证项目每个步骤可追踪、可回滚、可复现。
2. 适用范围：`smart-parking-thesis` 全项目（含 Step 0~Step 10 既有成果与后续 Step 11~18）。
3. 核心原则：
   - 不跳过 Git 闸门，不跨步合并。
   - 先提交证据，再进入下一步。
   - 禁止强推覆盖主分支。

## 2. G0 一次性导入流程（首次）

1. 初始化与远端绑定。

```bash
cd /Users/yanchen/VscodeProject/smart-parking-thesis
git init
git branch -M main
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/2696437448-cmyk/smart-parking-system.git
```

2. 基线提交与推送。

```bash
git add .
git commit -m "chore(repo): import step0-step10 baseline"
git push -u origin main
```

3. 若 `main` 推送失败（远端已有历史）：

```bash
git fetch origin
git switch -c migration/full-import
git push -u origin migration/full-import
```

然后在 GitHub 创建 `migration/full-import -> main` PR 合并。

4. 打基线标签。

```bash
git tag -a step10-pass-baseline -m "Step0-Step10 baseline"
git push origin step10-pass-baseline
```

## 3. 每一步（Step N）标准循环

1. 创建步骤分支。

```bash
git switch -c feat/stepNN-<short-topic>
```

2. 开发与自测（通过当前步骤闸门）。
3. 第一次提交：代码改动。

```bash
git add <code-files>
git commit -m "feat(stepNN): <code change summary>"
```

4. 第二次提交：证据与文档改动（至少包含 `progress.md` + 对应 `reports/stepNN_execution.md`）。

```bash
git add memory-bank/progress.md reports/stepNN_execution.md memory-bank/architecture.md
git commit -m "docs(stepNN): add execution evidence and architecture/progress updates"
```

5. 推送分支并创建 PR。

```bash
git push -u origin feat/stepNN-<short-topic>
```

6. PR 合并后打标签。

```bash
git switch main
git pull --ff-only
git tag -a stepNN-pass -m "StepNN gate passed"
git push origin stepNN-pass
```

## 4. Git 闸门定义（每步必须全部满足）

1. `branch created`：本步骤独立分支已创建。
2. `commit exists`：至少 2 次提交（代码 + 证据）。
3. `PR merged`：分支已通过 PR 合并到 `main`。
4. `tag created`：对应 `stepNN-pass` 标签已存在。

未满足任一项，视为“本步未完成”，禁止进入下一步。

## 5. 回滚策略

1. 单步回滚只允许回到最近稳定标签（如 `step12-pass`）。
2. 禁止跨步回滚（例如直接从 Step 16 回到 Step 11）。
3. 回滚动作必须在 `progress.md` 记录：原因、回滚标签、影响范围。
4. 禁止使用 `git push --force` 覆盖 `main`。

## 6. 数据提交双层策略

1. 当前阶段（体量小，答辩优先）：
   - fallback 数据与关键 Markdown 证据可入库。
2. Step 11 后（外部数据可能膨胀）：
   - 大体量原始数据不入库；改为下载脚本 + 校验哈希 + 来源说明。
   - 可复现最小样本与生成脚本保留在仓库。

## 7. 安全与合规检查

1. 禁止提交 `.env`、token、密码、私钥。
2. 首推前执行敏感词扫描（至少手工 `rg -n "token|secret|password|apikey|AKIA"`）。
3. 开启分支保护，主分支仅通过 PR 合并。

## 8. 证据记录最小集

每步至少沉淀以下证据：

1. `memory-bank/progress.md`：过程记录。
2. `reports/stepNN_execution.md`：执行命令与结果。
3. Git 元数据：`branch`、`commit_id`、`PR`、`tag`、`rollback_tag(optional)`。
