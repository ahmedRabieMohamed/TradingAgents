# Tasks: Professional UI Redesign & Arabic/English Bilingual Support

**Input**: Design documents from `/specs/006-pro-ui-arabic-support/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/rest-api.md, quickstart.md

**Tests**: Not requested — manual verification per constitution.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and create foundational config files

- [ ] T001 Install Ant Design frontend dependencies: `antd`, `@ant-design/icons`, `dayjs` in frontend/package.json
- [ ] T002 Install i18n frontend dependencies: `react-i18next`, `i18next` in frontend/package.json
- [ ] T003 Create Ant Design dark theme configuration mapping existing CSS variables to Ant Design tokens in frontend/src/theme.ts
- [ ] T004 [P] Create i18next initialization with English default and Arabic support in frontend/src/i18n.ts
- [ ] T005 [P] Create locale Zustand store with localStorage persistence in frontend/src/stores/localeStore.ts

**Checkpoint**: Dependencies installed, theme + i18n + locale store ready. No visual changes yet.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Wrap the app in Ant Design ConfigProvider and i18n provider — MUST complete before page migrations

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create English common translation file (nav labels, buttons, statuses, errors) in frontend/src/locales/en/common.json
- [ ] T007 [P] Create Arabic common translation file (mirror of en/common.json) in frontend/src/locales/ar/common.json
- [ ] T008 Wrap App component with Ant Design ConfigProvider (dark theme, RTL direction from locale store) and i18n provider in frontend/src/App.tsx
- [ ] T009 Convert `margin-left: var(--sidebar-width)` to `margin-inline-start` and other directional CSS to logical properties in frontend/src/styles/globals.css
- [ ] T010 Verify app renders without errors with ConfigProvider + i18n wrappers (manual check: `npm run dev`)

**Checkpoint**: Foundation ready — Ant Design theme active, i18n loaded, RTL-ready CSS. User story implementation can begin.

---

## Phase 3: User Story 1 — Professional Trading Interface (Priority: P1) MVP

**Goal**: Replace all custom inline styles with Ant Design components across the layout shell and all 7 pages for a professional trading look.

**Independent Test**: Navigate all 7 pages — every table, card, button, form, and modal uses Ant Design components with consistent dark theme. No unstyled or broken elements.

### Implementation for User Story 1

- [ ] T011 [US1] Migrate Sidebar to Ant Design Layout.Sider + Menu with icons and active states in frontend/src/components/layout/Sidebar.tsx
- [ ] T012 [P] [US1] Migrate Topbar to Ant Design layout with breadcrumbs/title area in frontend/src/components/layout/Topbar.tsx
- [ ] T013 [US1] Update App layout to use Ant Design Layout wrapper (Layout, Layout.Content) in frontend/src/App.tsx
- [ ] T014 [US1] Migrate Dashboard page: replace inline style cards with Ant Design Card, Statistic, Table, Tag in frontend/src/pages/Dashboard.tsx
- [ ] T015 [P] [US1] Create English dashboard translation file in frontend/src/locales/en/dashboard.json
- [ ] T016 [P] [US1] Create Arabic dashboard translation file in frontend/src/locales/ar/dashboard.json
- [ ] T017 [US1] Migrate NewAnalysis page: replace wizard with Ant Design Steps, Form, Input, Select, Button in frontend/src/pages/NewAnalysis.tsx
- [ ] T018 [P] [US1] Create English analysis translation file in frontend/src/locales/en/analysis.json
- [ ] T019 [P] [US1] Create Arabic analysis translation file in frontend/src/locales/ar/analysis.json
- [ ] T020 [US1] Migrate analysis sub-components: TickerInput, ConfigPanel, PipelineStage, MessageLog, StatsBar, AnalysisProgress, MarketSelector, ResultHero, ReportSection to Ant Design in frontend/src/components/analysis/
- [ ] T021 [US1] Migrate History page: replace custom table with Ant Design Table, filters with Select, CompareModal with Modal in frontend/src/pages/History.tsx
- [ ] T022 [P] [US1] Migrate history sub-components: FilterBar, HistoryTable, CompareModal to Ant Design in frontend/src/components/history/
- [ ] T023 [P] [US1] Create English history translation file in frontend/src/locales/en/history.json
- [ ] T024 [P] [US1] Create Arabic history translation file in frontend/src/locales/ar/history.json
- [ ] T025 [US1] Migrate Portfolio page: replace tables with Ant Design Table, modals with Modal, charts kept as-is in frontend/src/pages/Portfolio.tsx
- [ ] T026 [P] [US1] Migrate portfolio sub-components: TradeHistory, PortfolioAnalytics, AIComparison, TradeModal, PortfolioSummary, PositionsTable to Ant Design in frontend/src/components/portfolio/
- [ ] T027 [P] [US1] Create English portfolio translation file in frontend/src/locales/en/portfolio.json
- [ ] T028 [P] [US1] Create Arabic portfolio translation file in frontend/src/locales/ar/portfolio.json
- [ ] T029 [US1] Migrate Watchlist page: replace table and actions with Ant Design Table, Button, Popconfirm in frontend/src/pages/Watchlist.tsx
- [ ] T030 [P] [US1] Create English watchlist translation file in frontend/src/locales/en/watchlist.json
- [ ] T031 [P] [US1] Create Arabic watchlist translation file in frontend/src/locales/ar/watchlist.json
- [ ] T032 [US1] Migrate Performance page: replace cards with Ant Design Card, tables with Table in frontend/src/pages/Performance.tsx
- [ ] T033 [P] [US1] Migrate performance sub-components: MarketPerf, SimulationTable, PerfCard to Ant Design in frontend/src/components/performance/
- [ ] T034 [P] [US1] Create English performance translation file in frontend/src/locales/en/performance.json
- [ ] T035 [P] [US1] Create Arabic performance translation file in frontend/src/locales/ar/performance.json
- [ ] T036 [US1] Migrate Settings page: replace form elements with Ant Design Form, Switch, Select in frontend/src/pages/Settings.tsx
- [ ] T037 [P] [US1] Create English settings translation file in frontend/src/locales/en/settings.json
- [ ] T038 [P] [US1] Create Arabic settings translation file in frontend/src/locales/ar/settings.json
- [ ] T039 [US1] Migrate market-overview sub-components: MoverGrid, NewsSection, IndexBar, MarketSummaryBar, TickerNews, StockTable, MarketOverview to Ant Design in frontend/src/components/market-overview/
- [ ] T040 [US1] Remove unused inline style constants and stale CSS classes from frontend/src/styles/globals.css after migration
- [ ] T041 [US1] Verify: build passes (`npx tsc --noEmit && npm run build`) and all 7 pages render with Ant Design components

**Checkpoint**: All pages use Ant Design. Professional trading look achieved. US1 independently testable.

---

## Phase 4: User Story 2 — Arabic Language Web Interface (Priority: P1)

**Goal**: Full Arabic UI with RTL layout, language switcher, and persisted preference.

**Independent Test**: Toggle language to Arabic — all UI text is Arabic, layout flips to RTL (sidebar right, text right-aligned). Toggle back to English — everything restores. Refresh browser — preference persists.

### Implementation for User Story 2

- [ ] T042 [US2] Add language switcher component (English/Arabic toggle) to Topbar in frontend/src/components/layout/Topbar.tsx
- [ ] T043 [US2] Connect language switcher to locale store: update i18next language, document.dir, and Ant Design ConfigProvider direction in frontend/src/App.tsx
- [ ] T044 [US2] Wire all common translation keys (t() calls) into Sidebar nav labels in frontend/src/components/layout/Sidebar.tsx
- [ ] T045 [US2] Wire translation keys into Dashboard page text (card titles, metrics, empty states) in frontend/src/pages/Dashboard.tsx
- [ ] T046 [P] [US2] Wire translation keys into NewAnalysis page text (wizard steps, labels, buttons) in frontend/src/pages/NewAnalysis.tsx
- [ ] T047 [P] [US2] Wire translation keys into analysis sub-components text in frontend/src/components/analysis/
- [ ] T048 [P] [US2] Wire translation keys into History page and sub-components in frontend/src/pages/History.tsx and frontend/src/components/history/
- [ ] T049 [P] [US2] Wire translation keys into Portfolio page and sub-components in frontend/src/pages/Portfolio.tsx and frontend/src/components/portfolio/
- [ ] T050 [P] [US2] Wire translation keys into Watchlist page in frontend/src/pages/Watchlist.tsx
- [ ] T051 [P] [US2] Wire translation keys into Performance page and sub-components in frontend/src/pages/Performance.tsx and frontend/src/components/performance/
- [ ] T052 [P] [US2] Wire translation keys into Settings page in frontend/src/pages/Settings.tsx
- [ ] T053 [US2] Verify RTL layout: sidebar on right, text right-aligned, directional icons mirrored, no overflow or broken layout
- [ ] T054 [US2] Verify bidirectional text rendering: Arabic text with English ticker names (e.g., "تحليل سهم JUFO") displays correctly
- [ ] T055 [US2] Verify language persistence: select Arabic, refresh browser, confirm Arabic + RTL persists

**Checkpoint**: Full Arabic UI with RTL. Language toggle works. Preference persists. US2 independently testable.

---

## Phase 5: User Story 3 — Arabic AI Agent Reports (Priority: P2)

**Goal**: AI agents generate reports in Arabic when user's language is set to Arabic.

**Independent Test**: Set language to Arabic, run a stock analysis, verify all agent reports (Market Analyst, Fundamentals, Sentiment, Risk, Recommendation) are in Arabic. Tickers and numbers remain in Latin format.

### Implementation for User Story 3

- [ ] T056 [US3] Add `language: str = "en"` field to AnalysisRequest Pydantic schema in backend/app/models/schemas.py
- [ ] T057 [P] [US3] Add `language` column (String, default "en") to AnalysisSession SQLAlchemy model in backend/app/models/database.py
- [ ] T058 [US3] Thread `language` parameter from request through to analysis manager in backend/app/routers/analysis.py
- [ ] T059 [US3] Pass `language` value into AI agent system prompts so agents generate reports in the specified language in backend/app/services/ (analysis manager)
- [ ] T060 [US3] Store `language` on AnalysisSession record and include in GET response in backend/app/routers/analysis.py
- [ ] T061 [US3] Add `language` field to AnalysisSession TypeScript type in frontend/src/types/index.ts
- [ ] T062 [US3] Send locale store language value in POST /api/analysis request body in frontend/src/services/api.ts
- [ ] T063 [US3] Ensure markdown rendering handles RTL Arabic content correctly in ReportSection in frontend/src/components/analysis/ReportSection.tsx
- [ ] T064 [US3] Verify: run analysis in Arabic, confirm reports are in Arabic with correct RTL rendering
- [ ] T065 [US3] Verify: historical English analyses still display correctly when viewed in Arabic UI mode

**Checkpoint**: Arabic agent reports working. Backend stores language per session. US3 independently testable.

---

## Phase 6: User Story 4 — Responsive Professional Layout (Priority: P2)

**Goal**: Layout adapts from 2560px desktop down to 768px tablet without breaking.

**Independent Test**: Resize browser from 1920px to 768px — sidebar collapses, tables scroll, cards stack, no horizontal overflow on any page.

### Implementation for User Story 4

- [ ] T066 [US4] Configure Ant Design Layout.Sider collapsible behavior with breakpoint triggers in frontend/src/components/layout/Sidebar.tsx
- [ ] T067 [US4] Add responsive breakpoints to main content area: single-column layout for tablet widths in frontend/src/App.tsx
- [ ] T068 [P] [US4] Add horizontal scroll to Ant Design Tables on narrow screens across all pages using `scroll={{ x: true }}` prop
- [ ] T069 [P] [US4] Stack Dashboard cards vertically on narrow screens using Ant Design Row/Col responsive grid in frontend/src/pages/Dashboard.tsx
- [ ] T070 [US4] Verify: resize from 1920px to 768px across all 7 pages, confirm no overflow or broken elements in both English and Arabic

**Checkpoint**: Responsive layout working at all target widths in both LTR and RTL. US4 independently testable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup and regression verification

- [ ] T071 [P] Remove stale index.css Vite scaffold styles that conflict with Ant Design in frontend/src/index.css
- [ ] T072 [P] Clean up any remaining inline `CSSProperties` style objects not replaced during migration
- [ ] T073 Verify frontend build passes: `cd frontend && npx tsc --noEmit && npm run build`
- [ ] T074 Verify backend linting: `cd backend && ruff check .`
- [ ] T075 Full regression smoke test: navigate all 7 pages in English, toggle to Arabic, navigate all 7 pages, run an analysis in each language, check history/portfolio/watchlist
- [ ] T076 Run quickstart.md validation steps

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2. Can start immediately after.
- **US2 (Phase 4)**: Depends on Phase 3 (needs Ant Design components to wire translations into). Translation files are created in Phase 3; wiring happens in Phase 4.
- **US3 (Phase 5)**: Depends on Phase 2 only (backend changes are independent of frontend migration). Can run in parallel with US1/US2 for backend tasks (T056-T060).
- **US4 (Phase 6)**: Depends on Phase 3 (needs Ant Design Layout components in place).
- **Polish (Phase 7)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (Professional UI)**: Foundation only — fully independent
- **US2 (Arabic UI)**: Depends on US1 (translation keys need Ant Design components to live in)
- **US3 (Arabic Agent Reports)**: Backend tasks (T056-T060) independent of frontend. Frontend tasks (T061-T065) depend on US2 for Arabic rendering.
- **US4 (Responsive Layout)**: Depends on US1 (needs Ant Design layout components)

### Within Each User Story

- Translation file pairs (en + ar) can be created in parallel [P]
- Page migration → sub-component migration (same page dependencies)
- Build verification after each page migration recommended

### Parallel Opportunities

- T004 + T005: i18n config and locale store (different files)
- T006 + T007: English and Arabic common translations (different files)
- All translation file pairs within US1 (T015+T016, T018+T019, T023+T024, etc.)
- US3 backend tasks (T056-T060) can run in parallel with US1/US2 frontend work
- T066 + T068 + T069: responsive changes on different files

---

## Parallel Example: User Story 1 Page Migration

```bash
# Launch translation files in parallel (different files):
Task: "Create en/dashboard.json" (T015)
Task: "Create ar/dashboard.json" (T016)

# Launch independent page migrations in parallel after layout shell:
Task: "Migrate History page" (T021)
Task: "Migrate history sub-components" (T022)

# Launch portfolio translation + watchlist translation in parallel:
Task: "Create en/portfolio.json" (T027)
Task: "Create ar/portfolio.json" (T028)
Task: "Create en/watchlist.json" (T030)
Task: "Create ar/watchlist.json" (T031)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T010)
3. Complete Phase 3: User Story 1 — Professional UI (T011-T041)
4. **STOP and VALIDATE**: All pages look professional with Ant Design dark theme
5. Demo if ready — this alone transforms the app's appearance

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1: Professional UI → Demo (MVP!)
3. US2: Arabic UI → Demo (full bilingual interface)
4. US3: Arabic Agent Reports → Demo (complete Arabic experience)
5. US4: Responsive Layout → Demo (tablet support)
6. Polish → Ship

### Recommended Single-Developer Order

Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3) → Phase 6 (US4) → Phase 7

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Translation files should be created alongside their page migration for consistency
- Chart components (lightweight-charts, recharts) are NOT migrated to Ant Design — they stay as-is
- CandlestickChart component is kept unchanged — only wrapper/container styles migrate
- Commit after each completed page migration for easy rollback
