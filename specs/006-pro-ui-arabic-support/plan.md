# Implementation Plan: Professional UI Redesign & Arabic/English Bilingual Support

**Branch**: `006-pro-ui-arabic-support` | **Date**: 2026-04-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-pro-ui-arabic-support/spec.md`

## Summary

Replace the current custom CSS/inline-style interface with Ant Design 5.x for a professional trading platform look. Add full Arabic/English bilingual support with RTL layout, i18n translations (~240 strings), and Arabic AI agent report generation. The migration follows an incremental page-by-page strategy to minimize risk.

## Technical Context

**Language/Version**: TypeScript 5.9 (frontend), Python 3.10+ (backend)
**Primary Dependencies**: React 19, Ant Design 5.x (new), react-i18next (new), i18next (new), @ant-design/icons (new), dayjs (new — antd peer dep); FastAPI, SQLAlchemy (backend — existing)
**Storage**: localStorage (language preference), SQLite (language column on AnalysisSession)
**Testing**: Manual verification per constitution (tests optional for MVP)
**Target Platform**: Web — desktop/laptop/tablet (768px+)
**Project Type**: Web application (React SPA + Python API)
**Performance Goals**: Language switch < 2 seconds, no page reload; existing page load times maintained
**Constraints**: Must preserve existing dark theme identity; all 7 pages must be migrated; zero functional regressions
**Scale/Scope**: 7 pages, ~30 components, ~240 translatable strings, 1 backend schema change

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Research | Post-Design | Notes |
|-----------|-------------|-------------|-------|
| I. Simplicity First | PASS | PASS | Ant Design replaces complex inline styles with standard components — net simplification. i18next is the minimal viable i18n solution. No speculative abstractions. |
| II. Correctness Over Speed | PASS | PASS | RTL/BiDi text rendering verified via Ant Design's built-in support. Language stored immutably on analysis sessions. Financial data precision unaffected. |
| III. Separation of Concerns | PASS | PASS | i18n translations in separate JSON files, locale state in dedicated Zustand store, theme config isolated. Backend change limited to schema + request threading. |
| IV. Incremental Delivery | PASS | PASS | Page-by-page migration order. Each page migration is independently testable. P1 stories (design system + Arabic UI) complete before P2 (agent reports). |
| V. Data Integrity | PASS | PASS | `language` column added with default `"en"` — backward compatible. Existing sessions untouched. No data migration needed beyond additive column. |

**Gate result**: ALL PASS — no violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/006-pro-ui-arabic-support/
├── plan.md              # This file
├── research.md          # Phase 0 output — technology decisions
├── data-model.md        # Phase 1 output — entity changes
├── quickstart.md        # Phase 1 output — setup guide
├── contracts/
│   └── rest-api.md      # Phase 1 output — API changes
└── tasks.md             # Phase 2 output (created by /speckit-tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── schemas.py       # Add language field to AnalysisRequest
│   │   └── database.py      # Add language column to AnalysisSession
│   ├── routers/
│   │   └── analysis.py      # Thread language to analysis manager
│   └── services/            # Pass language to agent prompts

frontend/
├── src/
│   ├── i18n.ts              # NEW — i18next initialization
│   ├── theme.ts             # NEW — Ant Design dark theme config
│   ├── locales/             # NEW — translation files
│   │   ├── en/
│   │   │   ├── common.json
│   │   │   ├── analysis.json
│   │   │   ├── dashboard.json
│   │   │   ├── history.json
│   │   │   ├── portfolio.json
│   │   │   ├── watchlist.json
│   │   │   ├── performance.json
│   │   │   └── settings.json
│   │   └── ar/
│   │       └── [mirror of en/]
│   ├── stores/
│   │   └── localeStore.ts   # NEW — language preference store
│   ├── components/
│   │   └── layout/
│   │       ├── Sidebar.tsx   # Migrate to Layout.Sider + Menu
│   │       └── Topbar.tsx    # Add language switcher
│   ├── pages/
│   │   ├── Dashboard.tsx     # Migrate to Ant Design components
│   │   ├── NewAnalysis.tsx   # Migrate wizard + forms
│   │   ├── History.tsx       # Migrate tables + filters
│   │   ├── Portfolio.tsx     # Migrate tables + modals
│   │   ├── Watchlist.tsx     # Migrate table + actions
│   │   ├── Performance.tsx   # Migrate cards + tables
│   │   └── Settings.tsx      # Migrate form
│   ├── services/
│   │   └── api.ts            # Add language to analysis request
│   └── styles/
│       └── globals.css       # Convert to logical properties for RTL
```

**Structure Decision**: Existing `backend/` + `frontend/` web application structure preserved. New files added within existing directory hierarchy. No structural changes needed.

## Complexity Tracking

> No Constitution violations — this section is not applicable.
