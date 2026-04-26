# Tasks: Markdown Rendering & Premium UI Polish

**Input**: Design documents from `/specs/005-ui-polish-markdown/`
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Tests**: Not requested — manual verification per quickstart.md.

**Organization**: Tasks grouped by user story. Both stories are P1 and independent.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)

## Path Conventions

- **Web app**: `frontend/src/`

---

## Phase 1: Setup

**Purpose**: Install dependencies and add design system foundations

- [ ] T001 Install react-markdown and remark-gfm: `cd frontend && npm install react-markdown remark-gfm`
- [ ] T002 Add markdown body styles to frontend/src/styles/globals.css — add `.markdown-body` class with dark theme styles for h1-h6, strong, em, ul, ol, table, th, td, code, pre, blockquote, hr, a, img. Tables need visible borders (`1px solid var(--border)`), header bg (`var(--surface2)`), cell padding (8px 12px). Code gets monospace font on `var(--surface2)` bg. Headings get proper sizing scale and `var(--text)` color.
- [ ] T003 [P] Add shadow CSS variables to frontend/src/styles/globals.css — add `--shadow-sm: 0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2)` and `--shadow-md: 0 4px 12px rgba(0,0,0,0.4), 0 2px 4px rgba(0,0,0,0.3)` to `:root`
- [ ] T004 [P] Add skeleton and hover utility styles to frontend/src/styles/globals.css — add `.skeleton` class (background: var(--surface2), border-radius, animation: pulse 1.5s infinite), table row hover (`.hover-row:hover { background: rgba(59,130,246,0.04) }`), button hover (`.btn-hover:hover { filter: brightness(1.1) }`)

---

## Phase 2: User Story 1 — Properly Rendered Analysis Reports (P1)

**Goal**: Replace raw markdown `<pre>` with react-markdown rendered HTML in all report sections.

**Independent Test**: Run analysis, expand any report → headings are styled, tables have borders, bold is bold, no raw `###` or `**` visible.

- [ ] T005 [US1] Rewrite ReportSection.tsx in frontend/src/components/analysis/ReportSection.tsx — replace `<pre style={preStyle}>{content}</pre>` with `<ReactMarkdown remarkPlugins={[remarkGfm]} className="markdown-body">{content}</ReactMarkdown>`. Import react-markdown and remark-gfm. Remove the `preStyle` constant. Keep the collapsible header unchanged.
- [ ] T006 [US1] Verify markdown rendering in CompareModal if it displays report content — check frontend/src/components/history/CompareModal.tsx for any raw text rendering of report content and apply the same react-markdown treatment if needed (depends on T005)

**Checkpoint**: Expand any agent report on results page — all markdown renders correctly. Tables have borders, headings are sized, bold is bold.

---

## Phase 3: User Story 2 — Premium UI Polish (P1)

**Goal**: Polish all pages with consistent shadows, hover states, typography, and skeleton loading.

**Independent Test**: Navigate all pages — cards have depth, table rows highlight on hover, spacing is consistent, loading uses skeletons.

### Design System (globals.css)

- [ ] T007 [US2] Refine typography scale in frontend/src/styles/globals.css — ensure body font-size is 14px, add `.page-title` (fontSize: 20px, fontWeight: 700), `.section-title` (fontSize: 15px, fontWeight: 600), `.label` (fontSize: 11px, fontWeight: 600, uppercase, letter-spacing) utility classes

### Dashboard

- [ ] T008 [US2] Polish Dashboard cards in frontend/src/pages/Dashboard.tsx — add `boxShadow: 'var(--shadow-sm)'` to stat cards, add hover highlight to recent analyses table rows (className or inline onMouseEnter/Leave), replace loading spinner with skeleton card placeholders (4 skeleton blocks for stats + skeleton rows for table)

### History

- [ ] T009 [P] [US2] Polish History page in frontend/src/pages/History.tsx and frontend/src/components/history/HistoryTable.tsx — add hover highlight on table rows, add card shadow to table container, ensure consistent spacing

### Watchlist

- [ ] T010 [P] [US2] Polish Watchlist page in frontend/src/pages/Watchlist.tsx — add hover highlight on ticker rows, add card shadow to table container, style the add-ticker bar with proper alignment and spacing

### Portfolio

- [ ] T011 [P] [US2] Polish Portfolio page in frontend/src/pages/Portfolio.tsx — add card shadows to summary and positions sections, add hover on position rows

### Performance

- [ ] T012 [P] [US2] Polish Performance page in frontend/src/pages/Performance.tsx — add card shadows to perf cards

### Analysis Wizard

- [ ] T013 [US2] Polish NewAnalysis wizard in frontend/src/pages/NewAnalysis.tsx — refine step indicator (add subtle glow/shadow to active step circle), add shadow to the CandlestickChart container and ConfigPanel area

### Layout

- [ ] T014 [P] [US2] Polish Sidebar in frontend/src/components/layout/Sidebar.tsx — ensure nav item hover transition is smooth (0.15s), add subtle left border accent on hover (not just active)
- [ ] T015 [P] [US2] Polish Topbar in frontend/src/components/layout/Topbar.tsx — add subtle bottom border or shadow to create visual separation from content

### Modals

- [ ] T016 [P] [US2] Polish TradeModal in frontend/src/components/portfolio/TradeModal.tsx — add `boxShadow: 'var(--shadow-md)'` to modal card
- [ ] T017 [P] [US2] Polish CompareModal in frontend/src/components/history/CompareModal.tsx — add `boxShadow: 'var(--shadow-md)'` to modal card

**Checkpoint**: Navigate every page — cards have depth, rows highlight on hover, modals feel elevated, spacing is uniform.

---

## Phase 4: Polish & Verification

- [ ] T018 Run through all quickstart.md verification steps in specs/005-ui-polish-markdown/quickstart.md — fix any issues found
- [ ] T019 Verify TypeScript compiles cleanly (`tsc --noEmit`) and Vite builds without errors

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **US1 (Phase 2)**: Depends on T001 (react-markdown install) and T002 (markdown styles)
- **US2 (Phase 3)**: Depends on T003 (shadows) and T004 (hover/skeleton utilities)
- **Verification (Phase 4)**: Depends on US1 and US2 complete

### User Story Dependencies

- **US1 (Markdown)**: Independent — does not depend on US2
- **US2 (UI Polish)**: Independent — does not depend on US1
- Both can be implemented in parallel after Phase 1 setup

### Parallel Opportunities

```bash
# Phase 1 — after T001:
T002 (markdown CSS) || T003 (shadows) || T004 (hover/skeleton)

# Phase 2 (US1):
T005 (ReportSection) → T006 (CompareModal check)

# Phase 3 (US2) — all page polish tasks are parallelizable:
T008 || T009 || T010 || T011 || T012 || T013 || T014 || T015 || T016 || T017
```

---

## Implementation Strategy

### MVP First

1. Phase 1: Install deps + CSS foundations
2. US1: Fix markdown rendering (biggest visual fix)
3. **STOP and VALIDATE**: Reports render correctly
4. US2: Polish pages one by one
5. Phase 4: Full verification

---

## Notes

- [P] tasks = different files, no dependencies
- All changes are frontend-only — no backend modifications
- Inline styles remain the pattern — CSS classes only for markdown body,
  skeleton, and hover utilities that benefit from CSS pseudo-selectors
- Commit after each story completion
