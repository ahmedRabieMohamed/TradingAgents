# Research: 006 — Professional UI Redesign & Arabic/English Bilingual Support

**Date**: 2026-04-10

## R1: UI Component Library Selection

**Decision**: Ant Design 5.x (`antd` + `@ant-design/icons`)

**Rationale**:
- User explicitly requested Ant Design ("use ant skills for UI UX")
- Ant Design 5 has built-in RTL support via `ConfigProvider direction="rtl"` — critical for Arabic
- Comprehensive component set (Table, Card, Layout, Menu, Form, Button, Modal, Drawer, Tag, Badge, Spin, etc.) covers every component in the current app
- Built-in dark theme via `theme.darkAlgorithm` — maps well to the existing dark color palette
- Tree-shakeable in v5 — only imports used components, keeping bundle size manageable
- Large ecosystem with proven use in financial/trading dashboards

**Alternatives considered**:
- **Material UI (MUI)**: Strong RTL support but heavier bundle, less common in financial apps. User didn't request it.
- **Tailwind + Headless UI**: Would require building every component from scratch; no built-in RTL or dark theme token system.
- **Keep custom CSS**: Doesn't solve the "basic look" problem and makes RTL/i18n much harder.

**New dependencies**: `antd`, `@ant-design/icons`, `dayjs` (antd peer dependency)

## R2: Internationalization (i18n) Approach

**Decision**: `react-i18next` + `i18next` with JSON translation files

**Rationale**:
- Industry standard for React i18n — largest community, best documentation
- Supports namespaced translation files (one per page/component group) for maintainability
- Integrates with Ant Design's built-in locale system (`antd/locale/ar_EG`, `antd/locale/en_US`)
- Supports interpolation for dynamic values (stock names, numbers) inside translated strings
- Lightweight — only loads the active language's translations

**Alternatives considered**:
- **react-intl (FormatJS)**: Comparable but less ergonomic hook API (`useIntl` vs `useTranslation`). Slightly steeper learning curve.
- **Hand-rolled i18n**: Would work for 2 languages but lacks pluralization, interpolation, and namespace support. Not worth the effort.
- **No i18n library — just object lookup**: Too brittle for 7 pages × ~50-100 strings each. No RTL direction management.

**New dependencies**: `react-i18next`, `i18next`

**Translation file structure**:
```
frontend/src/locales/
├── en/
│   ├── common.json      # Shared: nav, buttons, status labels
│   ├── analysis.json    # NewAnalysis page
│   ├── dashboard.json   # Dashboard page
│   ├── history.json     # History page
│   ├── portfolio.json   # Portfolio page
│   ├── watchlist.json   # Watchlist page
│   ├── performance.json # Performance page
│   └── settings.json    # Settings page
└── ar/
    └── [mirror of en/]
```

## R3: RTL Layout Strategy

**Decision**: Ant Design `ConfigProvider` + CSS logical properties + `document.dir` attribute

**Rationale**:
- Ant Design handles RTL for all its components internally when `direction="rtl"` is set on `ConfigProvider`
- Setting `document.documentElement.dir = 'rtl'` handles browser-level text and layout direction
- CSS logical properties (`margin-inline-start` instead of `margin-left`) handle any remaining custom CSS
- The existing `globals.css` uses fixed `margin-left: var(--sidebar-width)` for layout offset — this needs to become `margin-inline-start`
- Sidebar position flip is handled automatically by CSS `direction: rtl` on the root

**Key RTL considerations**:
- Icons with directional meaning (arrows, chevrons) need to be mirrored — Ant Design icons handle this automatically
- Chart components (lightweight-charts, recharts) render LTR regardless of language — this is correct for financial data
- Bidirectional text (Arabic + English tickers) is handled natively by the Unicode BiDi algorithm when `dir="auto"` is used on mixed-content containers

## R4: Backend Language Parameter

**Decision**: Add optional `language` field to `AnalysisRequest` schema, thread it into agent system prompts

**Rationale**:
- The AI agents are LLM-powered and can generate Arabic text when instructed
- Adding `language: str = "en"` to `AnalysisRequest` is a minimal, backward-compatible change
- The language value gets stored with the analysis session so historical reports maintain their original language
- The frontend reads from the locale store and includes `language` in the POST body

**Implementation path**:
1. Add `language: str = "en"` to `AnalysisRequest` in `backend/app/models/schemas.py`
2. Add `language` column to `AnalysisSession` model in `backend/app/models/database.py`
3. Pass `language` to the analysis manager which includes it in agent system prompts
4. Store `language` with the session for retrieval

## R5: Dark Theme Mapping to Ant Design

**Decision**: Use Ant Design's `theme.darkAlgorithm` with custom token overrides matching existing palette

**Rationale**:
- The current app has a well-defined dark palette in `globals.css` (bg: #0a0e17, surface: #111827, accent: #3b82f6)
- Ant Design 5's token system allows overriding `colorPrimary`, `colorBgContainer`, `colorBgLayout`, `colorText`, etc.
- This preserves the existing visual identity while gaining Ant Design's component quality
- The CSS variables in `globals.css` can be kept for any custom components not replaced by Ant Design

**Token mapping**:
| CSS Variable | Ant Design Token |
|---|---|
| `--accent` (#3b82f6) | `colorPrimary` |
| `--bg` (#0a0e17) | `colorBgLayout` |
| `--surface` (#111827) | `colorBgContainer` |
| `--surface2` (#1a2236) | `colorBgElevated` |
| `--border` (#1e2a3a) | `colorBorder` |
| `--text` (#e2e8f0) | `colorText` |
| `--text2` (#94a3b8) | `colorTextSecondary` |
| `--text3` (#64748b) | `colorTextTertiary` |
| `--green` (#10b981) | `colorSuccess` |
| `--red` (#ef4444) | `colorError` |
| `--yellow` (#f59e0b) | `colorWarning` |

## R6: Migration Strategy (Incremental)

**Decision**: Page-by-page migration, layout shell first, then individual pages

**Rationale**:
- Migrating all 7 pages + 30+ components at once is risky and hard to review
- Start with the layout shell (Sidebar, Topbar, App wrapper) + i18n infrastructure
- Then migrate pages one at a time, starting with the most visible (Dashboard, NewAnalysis)
- Each page migration is independently testable per Constitution Principle IV (Incremental Delivery)

**Migration order**:
1. Infrastructure: Ant Design ConfigProvider, theme, i18n setup, locale store
2. Layout shell: Sidebar → `Layout.Sider` + `Menu`, Topbar → language switcher
3. Dashboard page (highest visibility)
4. NewAnalysis page (most complex — wizard flow, forms, streaming)
5. History page (tables, filters, compare modal)
6. Portfolio page (tables, charts, trade modal)
7. Watchlist page (table, actions)
8. Performance page (cards, tables)
9. Settings page (simplest)
10. Backend language parameter + agent Arabic support
