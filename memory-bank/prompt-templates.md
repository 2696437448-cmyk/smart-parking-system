# Prompt Templates (Codex/Claude)

## 0. Mandatory prompt entrypoint

For any task related to code structure, frontend redesign, backend interface shaping, performance optimization, architecture review, or implementation planning:

1. Read `memory-bank/project-prompt-library.md` first.
2. Select the matching chapter before starting work:
   - Product
   - Data Science
   - AI
   - Algorithm
   - Frontend / UI
   - Backend
3. Keep `Step36` as the stability baseline unless the current step explicitly defines a newer accepted baseline.
4. Prefer additive changes over replacements when existing Step36 behavior can be preserved.

## 1. Execute one plan step

```text
Read `memory-bank/project-prompt-library.md` first and activate the most relevant chapter for this task.
Then read files under memory-bank, but focus on:
- architecture.md
- current step in implementation-plan.md
- directly related sections in prd.md / data-spec.md
Execute only Step N in memory-bank/implementation-plan.md.
Constraints:
- Do not execute Step N+1.
- Keep API schema unchanged unless explicitly required by this step.
- Preserve Step36-approved behaviors unless this step explicitly introduces an additive upgrade.
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
Read `memory-bank/project-prompt-library.md` first and activate the chapter that matches the failing subsystem.
Then read memory-bank/acceptance.md.
Run tests needed for each acceptance item.
Output:
- pass/fail per item
- root cause for failures
- minimum patch plan
```

## 3. Thesis evidence packaging

```text
Read `memory-bank/project-prompt-library.md` first.
From current repo state, generate a thesis evidence package:
- architecture diagram inputs
- model comparison table source files
- reliability test screenshots/checkpoints
- reproducibility command list
```

## 4. Git execution checklist

```text
Read `memory-bank/project-prompt-library.md` first if the step includes implementation or refactor work.
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

## 5. Task routing guide

```text
Use this routing before writing code or plans:

- Product ambiguity or roadmap change -> Product chapter
- Raw data, ETL, analytics, quality, chart-source logic -> Data Science chapter
- Forecasting, model training, activation, rollback -> AI chapter
- Scheduling, ranking, optimization, deterministic behavior -> Algorithm chapter
- Layout, UI, state flow, page refactor, bundle size -> Frontend / UI chapter
- API shape, aggregation endpoints, service boundaries, reliability compatibility -> Backend chapter

If a task spans multiple areas:
1) choose the primary execution chapter
2) name secondary chapters explicitly
3) preserve Step36 baseline unless the current accepted step says otherwise
```
