# Prompt Templates (Codex/Claude)

## 1. Execute one plan step

```text
Read files under memory-bank first, but focus on:
- architecture.md
- current step in implementation-plan.md
- directly related sections in prd.md / data-spec.md
Execute only Step N in memory-bank/implementation-plan.md.
Constraints:
- Do not execute Step N+1.
- Keep API schema unchanged unless explicitly required by this step.
- Provide changed files and local verification commands.
- For algorithm-core or cross-service integration tasks, reserve 1.5x effort and list blockers first.
- Update memory-bank/progress.md and memory-bank/architecture.md.
- IMPORTANT: After completion, generate:
  1) append-only content for progress.md (time, blockers, fix, test result screenshot notes),
  2) architecture.md change summary (new files/interfaces/data flow changes),
  3) if data/model is involved, one experiment note block (params, log summary, preliminary conclusion).
```

## 2. Regression and acceptance check

```text
Read memory-bank/acceptance.md.
Run tests needed for each acceptance item.
Output:
- pass/fail per item
- root cause for failures
- minimum patch plan
```

## 3. Thesis evidence packaging

```text
From current repo state, generate a thesis evidence package:
- architecture diagram inputs
- model comparison table source files
- reliability test screenshots/checkpoints
- reproducibility command list
```

## 4. Git execution checklist

```text
Before coding Step N, follow this checklist:
1) Create branch: feat/stepNN-<topic>
2) Run step-specific checks before commit
3) Commit code changes
4) Commit evidence/document changes (progress + step report)
5) Push branch and open PR
6) Merge PR to main
7) Create and push tag: stepNN-pass

Output required:
- branch name
- commit ids
- PR link/number
- tag name
- rollback tag (if any)
```
