# Project Prompt Library (Step40)

> This library adapts high-signal prompt patterns to `smart-parking-thesis`.
> Use it as the first memory entrypoint for planning, refactoring, UI redesign, interface shaping, and repo modernization tasks.

## 1. Product

### When to use

- Define or refine owner/admin product scope.
- Compare candidate features without drifting away from the thesis baseline.
- Convert ambiguous ideas into a concrete, demoable workflow.

### Read first

- `memory-bank/prd.md`
- `memory-bank/architecture.md`
- `memory-bank/implementation-plan.md`
- `README.md`

### Project constraints

- The system serves two product surfaces: owner experience and admin experience.
- The current stable baseline is `Step40`; proposals must not invalidate Step40 acceptance.
- Keep the existing business backbone: reservation, billing, navigation, monitoring, revenue, reliability.
- Do not propose platform pivots as a default solution when the same goal can be reached through additive changes.

### Expected output

- Problem statement
- Target users and usage context
- In-scope / out-of-scope list
- Minimum viable workflow
- Success signals for demo and engineering validation
- Concrete repo impact: docs, APIs, pages, services, tests

### Common anti-patterns

- Reframing the project into a different product domain
- Treating admin and owner needs as the same information architecture problem
- Adding new features without linking them to demo value or thesis evidence
- Replacing stable flows instead of extending them additively

### Repo-specific checklist

- Preserve owner flow: recommendation -> reservation -> billing -> navigation
- Preserve admin flow: monitoring -> revenue -> occupancy -> forecast interpretation
- Preserve reliability story: idempotency, fallback, DLQ, realtime degradation
- Map every new idea back to an existing `memory-bank` step or a new Post-Step40 step

## 2. Data Science

### When to use

- Audit raw data quality and feature engineering assumptions.
- Design or refine Spark cleaning and summary analytics.
- Explain how data outputs should support model inputs and business charts.

### Read first

- `memory-bank/data-spec.md`
- `memory-bank/architecture.md`
- `reports/step11_execution.md`
- `reports/step26_execution.md`

### Project constraints

- Raw inputs are `sensor_event_raw`, `lpr_event_raw`, and `resident_trip_raw`.
- Spark strict remains the reference acceptance posture.
- Data work must stay compatible with `forecast_feature_table` and `dispatch_input_table`.
- Do not leak plaintext license plates or weaken existing privacy handling.

### Expected output

- Data quality risks
- Cleaning rules
- Feature construction logic
- Analytics outputs for owner/admin product use
- Validation metrics and evidence paths

### Common anti-patterns

- Treating fallback Python logic as equivalent to Spark strict acceptance
- Proposing features that cannot be traced to raw tables
- Mixing experimentation advice with unsupported production claims
- Ignoring how analytics feed charts, forecasting, or scheduling

### Repo-specific checklist

- Trace raw tables to processed outputs
- Keep feature naming compatible with existing reports and scripts
- Identify chart-facing fields for admin dashboards
- Identify model-facing fields for LSTM and scheduling inputs

## 3. AI

### When to use

- Review or refine forecasting model workflows.
- Compare model changes without breaking the productionized service shape.
- Plan evaluation, rollout, fallback, and registry behavior.

### Read first

- `memory-bank/tech-stack.md`
- `memory-bank/architecture.md`
- `reports/step12_execution.md`
- `reports/step13_execution.md`

### Project constraints

- The AI path is intentionally lightweight and thesis-friendly, not full MLOps.
- Model service behavior, activation, rollback, and prediction contract must stay stable unless changes are additive.
- Existing evaluation framing uses reproducible training and comparison artifacts.

### Expected output

- Objective and target variable
- Model/data assumptions
- Offline evaluation plan
- Online service impact
- Rollback and compatibility notes
- Required code, config, and evidence changes

### Common anti-patterns

- Replacing the model stack without an acceptance-driven reason
- Ignoring model-service contract compatibility
- Suggesting research ideas that have no repo execution path
- Describing quality improvements without metrics or rollback strategy

### Repo-specific checklist

- Keep `/predict`, `/optimize`, and model activation semantics coherent
- Preserve model registry and rollback support
- Separate experiment guidance from service integration work
- Tie output back to `reports/step12_*` and `reports/step13_*`

## 4. Algorithm

### When to use

- Audit or improve scheduling behavior, determinism, and complexity.
- Analyze ETA, ranking, dispatch, or decision logic.
- Evaluate whether a heuristic or optimization change is worth the risk.

### Read first

- `memory-bank/architecture.md`
- `reports/step19b_execution.md`
- `scripts/test_step19b_hungarian.py`

### Project constraints

- Hungarian-based scheduling is part of the thesis core and must remain reproducible.
- Determinism is mandatory for acceptance and evidence quality.
- Algorithm work must preserve business semantics and interface compatibility.

### Expected output

- Current algorithm goal and constraints
- Complexity and bottleneck analysis
- Determinism risks
- Edge cases and failure modes
- Minimal safe change set
- Verification plan

### Common anti-patterns

- Optimizing for elegance while weakening determinism
- Changing ranking logic without discussing user/business impact
- Treating benchmark wins as valid without matching acceptance scenarios
- Ignoring fallback behavior or traceability

### Repo-specific checklist

- Preserve deterministic outputs for identical inputs
- Preserve compatibility with reservation and dispatch flows
- Keep performance discussion grounded in actual request paths
- Link any proposed change to test coverage and evidence scripts

## 5. Frontend / UI

### When to use

- Redesign owner/admin user interfaces.
- Refactor frontend structure, route organization, or data-fetch boundaries.
- Improve design-system consistency, readability, performance, and interaction quality.

### Read first

- `memory-bank/architecture.md`
- `memory-bank/acceptance.md`
- `apps/frontend/src/App.vue`
- `apps/frontend/src/router.ts`
- `apps/frontend/src/pages/*`

### Project constraints

- Frontend stack is fixed: `Vue3 + TypeScript + Pinia + Vue Router + Leaflet + ECharts + Capacitor`.
- Step21, Step27, Step28, Step29, and Step33 capabilities must not regress.
- Owner experience and admin experience should feel intentionally different while sharing a coherent design language.
- Do not redesign the UI into a generic SaaS shell; it must still read as a smart parking product.

### Expected output

- Information architecture diagnosis
- Layout and component strategy
- Visual direction
- Data-flow and state-flow refactor plan
- Performance considerations
- Validation commands and manual review checklist

### Common anti-patterns

- Keeping owner/admin inside a single demo-style shell
- Leaving data fetching embedded in route components when the complexity grows
- Making charts/maps visually dense without business interpretation
- Using cosmetic redesign without improving hierarchy, clarity, or responsiveness
- Solving bundle warnings by simply raising warning thresholds

### Repo-specific checklist

- Prefer role-aware layouts over a one-shell-fits-all structure
- Normalize API access, trace headers, and error handling
- Keep navigation, billing, and chart pages demoable on desktop and mobile
- Lazy-load heavy route views when possible
- Preserve Leaflet and ECharts functional coverage while improving presentation

## 6. Backend

### When to use

- Refactor backend interface shape or service boundaries.
- Add additive endpoints that simplify the frontend.
- Audit reservation, billing, monitoring, or aggregation logic.

### Read first

- `memory-bank/architecture.md`
- `memory-bank/acceptance.md`
- `services/parking-service/src/main/java/com/smartparking/parking/*`
- `openapi/smart-parking.yaml`

### Project constraints

- Core topology stays: `gateway-service + parking-service + model-service + realtime-service + frontend-app`.
- Existing business semantics and public flows must remain compatible.
- Step24 / Step30 / Step36 / Step40 evidence must stay meaningful after the change.
- Additive view-model endpoints are preferred over breaking existing APIs.

### Expected output

- Interface or service boundary issue
- Proposed endpoint/service change
- Compatibility policy
- Data shape for frontend consumption
- Risks, rollout, and verification plan

### Common anti-patterns

- Forcing the frontend to stitch many low-level endpoints when the backend can expose a stable dashboard view
- Mixing technical diagnostics with business-facing API payloads
- Changing core booking or billing semantics to simplify UI work
- Refactoring for purity while ignoring acceptance and demo behavior

### Repo-specific checklist

- Keep old endpoints unless there is an explicit migration step
- Add `summary`, `sections`, chart-ready arrays, and fallback metadata for UI-facing aggregates
- Preserve traceability and compatibility with gateway routing
- Verify additive endpoints against existing scripts and owner/admin page expectations
