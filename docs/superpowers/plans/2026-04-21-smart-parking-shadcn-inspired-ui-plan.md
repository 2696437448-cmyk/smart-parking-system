# Smart Parking Shadcn-Inspired UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rework the current smart parking frontend into a shadcn-inspired product UI while keeping the existing Vue + Arco stack, routes, and business flow intact.

**Architecture:** Keep the current owner/admin route structure and business composables, then tighten the visual system around product-style shells, headers, KPI cards, chart/map containers, and page hierarchy. Use a source-level regression script as the TDD guardrail for the new UI structure, then refactor shared primitives before updating owner/admin pages and style tokens together.

**Tech Stack:** Vue 3, TypeScript, Arco Design Vue, Vue Router, Pinia, ECharts, Leaflet, `@vueuse/motion`, Python verification scripts, Vite

---

### Task 1: Add a failing regression gate for the new product UI structure

**Files:**
- Create: `scripts/test_step42_shadcn_ui_polish.py`
- Modify: `scripts/test_frontend_ui_refinement.py`
- Verify: `apps/frontend/src/layouts/AdminLayout.vue`
- Verify: `apps/frontend/src/layouts/OwnerLayout.vue`
- Verify: `apps/frontend/src/components/SectionHeader.vue`
- Verify: `apps/frontend/src/components/MetricCard.vue`

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "apps" / "frontend"

REQUIRED = {
    "src/layouts/AdminLayout.vue": ["admin-sidebar-shell", "admin-page-header", "admin-sidebar-footer"],
    "src/layouts/OwnerLayout.vue": ["owner-journey-header", "owner-nav-pill", "owner-mobile-dock"],
    "src/components/SectionHeader.vue": ["section-header-actions", "section-header-kicker"],
    "src/components/MetricCard.vue": ["metric-card-trend", "metric-card-meta"],
    "src/pages/AdminMonitor.vue": ["operations-primary-grid", "operations-secondary-grid", "primary-chart-card"],
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 scripts/test_step42_shadcn_ui_polish.py`

Expected: FAIL because the new class tokens do not exist yet.

- [ ] **Step 3: Extend the existing UI refinement regression**

```python
REQUIRED_TOKENS = {
    "src/pages/OwnerDashboard.vue": ["owner-summary-band", "reservation-panel", "recommendation-list"],
    "src/pages/OwnerOrders.vue": ["order-status-band", "billing-summary-card", "task-footer-actions"],
    "src/pages/OwnerNavigation.vue": ["navigation-summary-stack", "navigation-map-stage"],
    "src/pages/AdminMonitor.vue": ["operations-primary-grid", "operations-secondary-grid", "primary-chart-card"],
}
```

- [ ] **Step 4: Run both source-level UI scripts**

Run:

```bash
python3 scripts/test_step42_shadcn_ui_polish.py
python3 scripts/test_frontend_ui_refinement.py
```

Expected: both fail before implementation, proving the new structure is actually enforced.

- [ ] **Step 5: Commit**

```bash
git add scripts/test_step42_shadcn_ui_polish.py scripts/test_frontend_ui_refinement.py
git commit -m "test: add shadcn-inspired ui structure gate"
```

### Task 2: Refactor shared shells and UI primitives

**Files:**
- Modify: `apps/frontend/src/layouts/AdminLayout.vue`
- Modify: `apps/frontend/src/layouts/OwnerLayout.vue`
- Modify: `apps/frontend/src/components/SectionHeader.vue`
- Modify: `apps/frontend/src/components/MetricCard.vue`
- Modify: `apps/frontend/src/components/ViewStateNotice.vue`
- Modify: `apps/frontend/src/components/EChartPanel.vue`
- Modify: `apps/frontend/src/components/MapPreview.vue`
- Modify: `apps/frontend/src/styles/tokens.css`
- Modify: `apps/frontend/src/styles/layout.css`
- Modify: `apps/frontend/src/styles/components.css`
- Verify: `scripts/test_step42_shadcn_ui_polish.py`

- [ ] **Step 1: Implement the new admin and owner shell structure**

```vue
<aside class="admin-sidebar-shell">
  <div class="admin-sidebar-brand">...</div>
  <nav class="admin-sidebar-nav">...</nav>
  <div class="admin-sidebar-footer">...</div>
</aside>

<header class="owner-journey-header">
  <div class="owner-journey-copy">...</div>
  <div class="owner-journey-actions">...</div>
</header>
```

- [ ] **Step 2: Implement the shared product header and KPI card structure**

```vue
<div class="section-header-kicker">
  <p class="eyebrow">{{ eyebrow }}</p>
  <a-tag v-if="badge">{{ badge }}</a-tag>
</div>
<div class="section-header-actions">
  <slot name="actions" />
</div>
```

```vue
<article class="metric-card-shell">
  <div class="metric-card-meta">...</div>
  <strong class="metric-value">{{ value }}</strong>
  <p class="metric-card-trend">{{ note }}</p>
</article>
```

- [ ] **Step 3: Rebuild notice, chart, and map containers around the new hierarchy**

```vue
<div class="state-notice-inline" v-if="compact">...</div>
<article class="chart-panel-shell primary-chart-card">...</article>
<article class="map-preview-shell navigation-map-stage">...</article>
```

- [ ] **Step 4: Update tokens and shared CSS**

```css
.admin-sidebar-shell { ... }
.admin-page-header { ... }
.owner-mobile-dock { ... }
.section-header-actions { ... }
.metric-card-meta { ... }
.metric-card-trend { ... }
```

- [ ] **Step 5: Run the red test and typecheck**

Run:

```bash
python3 scripts/test_step42_shadcn_ui_polish.py
npm run typecheck
```

Expected: the new structure gate passes, and typecheck stays green.

- [ ] **Step 6: Commit**

```bash
git add apps/frontend/src/layouts/AdminLayout.vue apps/frontend/src/layouts/OwnerLayout.vue apps/frontend/src/components/SectionHeader.vue apps/frontend/src/components/MetricCard.vue apps/frontend/src/components/ViewStateNotice.vue apps/frontend/src/components/EChartPanel.vue apps/frontend/src/components/MapPreview.vue apps/frontend/src/styles/tokens.css apps/frontend/src/styles/layout.css apps/frontend/src/styles/components.css
git commit -m "feat: add shadcn-inspired product shells and shared ui"
```

### Task 3: Recompose owner/admin pages and verify the final frontend build

**Files:**
- Modify: `apps/frontend/src/pages/AdminMonitor.vue`
- Modify: `apps/frontend/src/pages/OwnerDashboard.vue`
- Modify: `apps/frontend/src/pages/OwnerOrders.vue`
- Modify: `apps/frontend/src/pages/OwnerNavigation.vue`
- Modify: `apps/frontend/src/styles/pages.css`
- Verify: `scripts/test_frontend_ui_refinement.py`
- Verify: `scripts/test_step41_arco_tech_ui.py`
- Verify: `scripts/test_step42_shadcn_ui_polish.py`

- [ ] **Step 1: Restructure AdminMonitor into primary and secondary grids**

```vue
<section class="operations-primary-grid">
  <article class="panel primary-kpi-panel">...</article>
  <article class="panel primary-chart-card">...</article>
</section>

<section class="operations-secondary-grid">
  <article class="panel insights-panel">...</article>
  <article class="panel forecast-panel">...</article>
</section>
```

- [ ] **Step 2: Restructure owner pages into summary-first task flows**

```vue
<div class="owner-summary-band">...</div>
<article class="panel reservation-panel">...</article>
<div class="recommendation-list">...</div>
```

```vue
<div class="order-status-band">...</div>
<article class="billing-summary-card">...</article>
<div class="task-footer-actions">...</div>
```

```vue
<div class="navigation-summary-stack">...</div>
<article class="navigation-map-stage">...</article>
```

- [ ] **Step 3: Update page-level CSS to match the new hierarchy**

```css
.operations-primary-grid { ... }
.operations-secondary-grid { ... }
.owner-summary-band { ... }
.billing-summary-card { ... }
.navigation-summary-stack { ... }
```

- [ ] **Step 4: Run all targeted UI verification**

Run:

```bash
python3 scripts/test_frontend_ui_refinement.py
python3 scripts/test_step41_arco_tech_ui.py
python3 scripts/test_step42_shadcn_ui_polish.py
npm run typecheck
npm run build
```

Expected: all scripts pass, typecheck passes, build exits 0.

- [ ] **Step 5: Commit**

```bash
git add apps/frontend/src/pages/AdminMonitor.vue apps/frontend/src/pages/OwnerDashboard.vue apps/frontend/src/pages/OwnerOrders.vue apps/frontend/src/pages/OwnerNavigation.vue apps/frontend/src/styles/pages.css
git commit -m "feat: polish smart parking pages with shadcn-inspired hierarchy"
```
