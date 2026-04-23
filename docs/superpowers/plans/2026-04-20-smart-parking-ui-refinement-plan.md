# Smart Parking UI Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the existing owner/admin frontend into a more polished, structured final product without changing routes or page structure, and keep the result ready for final thesis writing.

**Architecture:** Keep the current `OwnerLayout` / `AdminLayout` and four-page structure, but move repeated display logic into lightweight shared components and presenter helpers. Preserve existing dashboard and realtime contracts while improving visual hierarchy, state wording, and page readability.

**Tech Stack:** Vue 3, TypeScript, Vite, Pinia, Vue Router, ECharts, Leaflet, existing Python gate scripts

---

## File Map

### New files
- `apps/frontend/src/components/ActionBar.vue`
- `apps/frontend/src/components/KeyValueList.vue`
- `apps/frontend/src/components/StatusBadge.vue`
- `apps/frontend/src/presenters/format.ts`
- `apps/frontend/src/presenters/owner.ts`
- `apps/frontend/src/presenters/admin.ts`
- `scripts/test_frontend_ui_refinement.py`

### Modified files
- `apps/frontend/src/styles/tokens.css`
- `apps/frontend/src/styles/base.css`
- `apps/frontend/src/styles/layout.css`
- `apps/frontend/src/styles/components.css`
- `apps/frontend/src/styles/pages.css`
- `apps/frontend/src/components/SectionHeader.vue`
- `apps/frontend/src/components/MetricCard.vue`
- `apps/frontend/src/components/ViewStateNotice.vue`
- `apps/frontend/src/components/EChartPanel.vue`
- `apps/frontend/src/components/MapPreview.vue`
- `apps/frontend/src/layouts/OwnerLayout.vue`
- `apps/frontend/src/layouts/AdminLayout.vue`
- `apps/frontend/src/pages/OwnerDashboard.vue`
- `apps/frontend/src/pages/OwnerOrders.vue`
- `apps/frontend/src/pages/OwnerNavigation.vue`
- `apps/frontend/src/pages/AdminMonitor.vue`
- `apps/frontend/src/composables/useOwnerDashboardView.ts`
- `apps/frontend/src/composables/useAdminDashboardView.ts`
- `apps/frontend/src/composables/useViewState.ts`

---

### Task 1: Add the refinement regression gate first

**Files:**
- Create: `scripts/test_frontend_ui_refinement.py`
- Test: `scripts/test_frontend_ui_refinement.py`

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "apps" / "frontend"

REQUIRED_FILES = [
    "src/components/ActionBar.vue",
    "src/components/KeyValueList.vue",
    "src/components/StatusBadge.vue",
    "src/presenters/format.ts",
    "src/presenters/owner.ts",
    "src/presenters/admin.ts",
]

REQUIRED_TOKENS = {
    "src/pages/OwnerDashboard.vue": ["ActionBar", "StatusBadge", "ownerDashboardHero"],
    "src/pages/OwnerOrders.vue": ["KeyValueList", "StatusBadge"],
    "src/pages/OwnerNavigation.vue": ["KeyValueList", "routeSummaryLines"],
    "src/pages/AdminMonitor.vue": ["ActionBar", "adminChartCards", "StatusBadge"],
}

for rel in REQUIRED_FILES:
    path = FRONTEND / rel
    if not path.exists():
        raise AssertionError(f"missing required refinement file: {path}")

for rel, tokens in REQUIRED_TOKENS.items():
    text = (FRONTEND / rel).read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            raise AssertionError(f"{rel} missing token: {token}")

print("FRONTEND_UI_REFINEMENT_PASS")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 scripts/test_frontend_ui_refinement.py`
Expected: FAIL with missing refinement files such as `ActionBar.vue` or `format.ts`

- [ ] **Step 3: Commit the failing test scaffold**

```bash
git add scripts/test_frontend_ui_refinement.py
git commit -m "test: add frontend refinement regression gate"
```

### Task 2: Build presenter helpers and shared UI primitives

**Files:**
- Create: `apps/frontend/src/components/ActionBar.vue`
- Create: `apps/frontend/src/components/KeyValueList.vue`
- Create: `apps/frontend/src/components/StatusBadge.vue`
- Create: `apps/frontend/src/presenters/format.ts`
- Create: `apps/frontend/src/presenters/owner.ts`
- Create: `apps/frontend/src/presenters/admin.ts`
- Modify: `apps/frontend/src/components/SectionHeader.vue`
- Modify: `apps/frontend/src/components/MetricCard.vue`
- Modify: `apps/frontend/src/components/ViewStateNotice.vue`
- Modify: `apps/frontend/src/components/EChartPanel.vue`
- Modify: `apps/frontend/src/components/MapPreview.vue`
- Modify: `apps/frontend/src/composables/useViewState.ts`
- Test: `scripts/test_frontend_ui_refinement.py`

- [ ] **Step 1: Write the minimal shared components and presenter helpers**

```ts
// apps/frontend/src/presenters/format.ts
export function formatCurrency(value: number | null | undefined) {
  return `¥${Number(value ?? 0).toFixed(2)}`;
}

export function formatPercent(value: number | null | undefined) {
  return `${Number((value ?? 0) * 100).toFixed(1)}%`;
}

export function formatDatetimeLabel(value: string | null | undefined) {
  return value ? value.replace("T", " ").slice(0, 16) : "暂无";
}
```

```vue
<!-- apps/frontend/src/components/StatusBadge.vue -->
<script setup lang="ts">
defineProps<{ label: string; tone?: "default" | "accent" | "calm" | "warn" }>();
</script>

<template>
  <span class="status-badge" :data-tone="tone ?? 'default'">{{ label }}</span>
</template>
```

```vue
<!-- apps/frontend/src/components/ActionBar.vue -->
<script setup lang="ts">
defineProps<{ align?: "start" | "between" }>();
</script>

<template>
  <div class="action-bar" :data-align="align ?? 'start'"><slot /></div>
</template>
```

```vue
<!-- apps/frontend/src/components/KeyValueList.vue -->
<script setup lang="ts">
defineProps<{ items: Array<{ label: string; value: string }> }>();
</script>

<template>
  <div class="key-value-list">
    <div v-for="item in items" :key="`${item.label}-${item.value}`" class="key-value-row">
      <span class="key-label">{{ item.label }}</span>
      <strong class="key-value">{{ item.value }}</strong>
    </div>
  </div>
</template>
```

- [ ] **Step 2: Upgrade the existing primitives without changing their core role**

```vue
<!-- SectionHeader.vue -->
<script setup lang="ts">
import StatusBadge from "./StatusBadge.vue";
defineProps<{ eyebrow: string; title: string; subtitle?: string; badge?: string; badgeTone?: "default" | "accent" | "calm" | "warn" }>();
</script>
```

```vue
<!-- ViewStateNotice.vue -->
<script setup lang="ts">
import StatusBadge from "./StatusBadge.vue";
// keep tone mapping, but render a richer summary block
</script>
```

```ts
// useViewState.ts
interface ReadyOptions {
  title: string;
  message: string;
  detail?: string;
  staleTitle?: string;
  staleMessage?: string;
  staleDetail?: string;
  badge?: string;
}
```

- [ ] **Step 3: Run the new regression test and verify it still fails for page tokens**

Run: `python3 scripts/test_frontend_ui_refinement.py`
Expected: FAIL with missing page tokens such as `ownerDashboardHero` or `adminChartCards`

- [ ] **Step 4: Commit the shared layer**

```bash
git add apps/frontend/src/components apps/frontend/src/presenters apps/frontend/src/composables/useViewState.ts
 git commit -m "feat: add frontend presenters and shared UI primitives"
```

### Task 3: Refine owner layout and owner pages

**Files:**
- Modify: `apps/frontend/src/styles/tokens.css`
- Modify: `apps/frontend/src/styles/base.css`
- Modify: `apps/frontend/src/styles/layout.css`
- Modify: `apps/frontend/src/styles/components.css`
- Modify: `apps/frontend/src/styles/pages.css`
- Modify: `apps/frontend/src/layouts/OwnerLayout.vue`
- Modify: `apps/frontend/src/pages/OwnerDashboard.vue`
- Modify: `apps/frontend/src/pages/OwnerOrders.vue`
- Modify: `apps/frontend/src/pages/OwnerNavigation.vue`
- Modify: `apps/frontend/src/composables/useOwnerDashboardView.ts`
- Test: `python3 scripts/test_frontend_ui_refinement.py`
- Test: `python3 scripts/test_step21_frontend_pages.py`
- Test: `python3 scripts/test_step27_app_shell.py`

- [ ] **Step 1: Refactor owner presenters and page-level derived data**

```ts
// apps/frontend/src/presenters/owner.ts
import { formatCurrency, formatDatetimeLabel } from "./format";

export function ownerDashboardHero(summary: { region_label?: string; recommendation_count?: number; latest_billing_status?: string }) {
  return {
    eyebrow: "Owner Journey",
    badge: summary.region_label ?? "智慧停车",
    helper: `当前共整理 ${summary.recommendation_count ?? 0} 个候选车位，最近账单状态为 ${summary.latest_billing_status ?? "NONE"}。`,
  };
}

export function routeSummaryLines(input: { eta_minutes?: number; route_summary?: { summary?: string; distance_km?: number } | null }) {
  return [
    `预计到达：${input.eta_minutes ?? 0} 分钟`,
    `路线摘要：${input.route_summary?.summary ?? "社区内部推荐路线"}`,
    `距离：${input.route_summary?.distance_km ?? 0} km`,
  ];
}
```

- [ ] **Step 2: Update owner pages to use the new shared blocks**

```vue
<!-- OwnerDashboard.vue -->
<script setup lang="ts">
import ActionBar from "../components/ActionBar.vue";
import StatusBadge from "../components/StatusBadge.vue";
import { ownerDashboardHero } from "../presenters/owner";
</script>
```

```vue
<!-- OwnerOrders.vue -->
<script setup lang="ts">
import KeyValueList from "../components/KeyValueList.vue";
import StatusBadge from "../components/StatusBadge.vue";
</script>
```

```vue
<!-- OwnerNavigation.vue -->
<script setup lang="ts">
import KeyValueList from "../components/KeyValueList.vue";
import { routeSummaryLines } from "../presenters/owner";
</script>
```

- [ ] **Step 3: Update owner layout and owner-facing styling**

```css
/* tokens.css */
:root {
  --color-bg-main: #f7f2ea;
  --color-panel-strong: rgba(255, 255, 255, 0.95);
  --color-panel-muted: rgba(250, 252, 254, 0.88);
  --shadow-soft: 0 20px 44px rgba(20, 45, 67, 0.08);
  --shadow-strong: 0 26px 60px rgba(20, 45, 67, 0.14);
}
```

```css
/* pages.css */
.owner-dashboard .recommend-card,
.owner-orders .metric-card,
.owner-navigation .map-panel {
  position: relative;
  overflow: hidden;
}
```

- [ ] **Step 4: Run owner-facing verifications**

Run:
- `python3 scripts/test_frontend_ui_refinement.py`
- `python3 scripts/test_step21_frontend_pages.py`
- `python3 scripts/test_step27_app_shell.py`

Expected: PASS

- [ ] **Step 5: Commit the owner refinement**

```bash
git add apps/frontend/src/layouts/OwnerLayout.vue apps/frontend/src/pages/OwnerDashboard.vue apps/frontend/src/pages/OwnerOrders.vue apps/frontend/src/pages/OwnerNavigation.vue apps/frontend/src/presenters/owner.ts apps/frontend/src/styles
git commit -m "feat: refine owner journey UI"
```

### Task 4: Refine admin monitor, chart presentation, and full verification

**Files:**
- Modify: `apps/frontend/src/layouts/AdminLayout.vue`
- Modify: `apps/frontend/src/pages/AdminMonitor.vue`
- Modify: `apps/frontend/src/composables/useAdminDashboardView.ts`
- Modify: `apps/frontend/src/components/EChartPanel.vue`
- Modify: `apps/frontend/src/styles/layout.css`
- Modify: `apps/frontend/src/styles/components.css`
- Modify: `apps/frontend/src/styles/pages.css`
- Create: `apps/frontend/src/presenters/admin.ts`
- Test: `npm run typecheck`
- Test: `npm run build`
- Test: `python3 scripts/test_frontend_ui_refinement.py`
- Test: `python3 scripts/test_step29_admin_charts.py`
- Test: `python3 scripts/test_step37_prompt_frontend_modernization.py`
- Test: `python3 scripts/test_step39_dashboard_hardening.py`

- [ ] **Step 1: Add admin presenter helpers and chart view-models**

```ts
// apps/frontend/src/presenters/admin.ts
import { formatCurrency, formatPercent } from "./format";

export function adminChartCards(dashboard: any) {
  return [
    { title: "今日收益", value: formatCurrency(dashboard?.summary?.revenue_total), note: "billing_records 汇总" },
    { title: "峰值占用率", value: formatPercent(dashboard?.highlights?.peak_occupancy), note: "最近图表采样区间" },
  ];
}
```

- [ ] **Step 2: Update admin page and layout to use the refined structure**

```vue
<!-- AdminMonitor.vue -->
<script setup lang="ts">
import ActionBar from "../components/ActionBar.vue";
import StatusBadge from "../components/StatusBadge.vue";
import { adminChartCards } from "../presenters/admin";
</script>
```

```vue
<!-- AdminLayout.vue -->
<template>
  <div class="experience-shell admin-shell admin-shell-refined">
    ...
  </div>
</template>
```

- [ ] **Step 3: Run full frontend verification**

Run:
- `cd apps/frontend && npm run typecheck`
- `cd apps/frontend && npm run build`
- `python3 scripts/test_frontend_ui_refinement.py`
- `python3 scripts/test_step29_admin_charts.py`
- `python3 scripts/test_step37_prompt_frontend_modernization.py`
- `python3 scripts/test_step39_dashboard_hardening.py`

Expected: PASS

- [ ] **Step 4: Run final regression check if runtime is available**

Run: `python3 scripts/test_step40_release_acceptance.py`
Expected: PASS or explicit runtime blocker report

- [ ] **Step 5: Commit the admin refinement and verification-backed finish**

```bash
git add apps/frontend/src/layouts/AdminLayout.vue apps/frontend/src/pages/AdminMonitor.vue apps/frontend/src/composables/useAdminDashboardView.ts apps/frontend/src/presenters/admin.ts apps/frontend/src/styles scripts/test_frontend_ui_refinement.py
git commit -m "feat: refine admin dashboard UI"
```

---

## Self-Review

### Spec coverage
- Visual hierarchy and component upgrades: Task 2 and Task 3
- Owner journey continuity: Task 3
- Admin dashboard readability and chart explanation: Task 4
- Presenter-layer extraction: Task 2, Task 3, Task 4
- Unified state semantics preserved: Task 2 and Task 4
- Verification requirements: Task 1 through Task 4
- Thesis-readiness constraint: preserved by keeping structure and not adding debate/demo-only pages

### Placeholder scan
- No `TODO` / `TBD`
- All new files and verification commands are explicit
- Every task includes concrete file paths and commands

### Type consistency
- Presenter helpers are named consistently: `ownerDashboardHero`, `routeSummaryLines`, `adminChartCards`
- Shared primitives are named consistently: `ActionBar`, `KeyValueList`, `StatusBadge`
- Existing state model stays on `useViewState`
