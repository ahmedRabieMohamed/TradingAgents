# Quickstart: 006 — Professional UI Redesign & Arabic/English Bilingual Support

**Date**: 2026-04-10

## Prerequisites

- Node.js 18+ and npm (already installed)
- Python 3.10+ (already installed)
- Existing TradingAgents app running on `006-pro-ui-arabic-support` branch

## Install New Frontend Dependencies

```bash
cd frontend
npm install antd @ant-design/icons dayjs react-i18next i18next
```

## Key Files to Create

### 1. i18n Configuration

Create `frontend/src/i18n.ts` — initializes i18next with English (default) and Arabic.

### 2. Locale Store

Create `frontend/src/stores/localeStore.ts` — Zustand store managing:
- `locale`: `"en"` | `"ar"` (persisted to localStorage)
- `setLocale(locale)`: updates store, localStorage, document.dir, and i18next language

### 3. Translation Files

Create `frontend/src/locales/en/*.json` and `frontend/src/locales/ar/*.json` — one file per namespace (common, analysis, dashboard, history, portfolio, watchlist, performance, settings).

### 4. Ant Design Theme Configuration

Create `frontend/src/theme.ts` — maps existing CSS variables to Ant Design token overrides with `darkAlgorithm`.

## Key Files to Modify

### Frontend

| File | Change |
|------|--------|
| `App.tsx` | Wrap with Ant Design `ConfigProvider` (theme, direction, locale) |
| `components/layout/Sidebar.tsx` | Replace with `Layout.Sider` + `Menu` |
| `components/layout/Topbar.tsx` | Add language switcher, use Ant Design components |
| `pages/Dashboard.tsx` | Replace inline styles with Ant Design `Card`, `Table`, `Statistic` |
| `pages/NewAnalysis.tsx` | Replace forms with Ant Design `Steps`, `Form`, `Input`, `Select` |
| `pages/History.tsx` | Replace with Ant Design `Table`, `Select` filters |
| `pages/Portfolio.tsx` | Replace with Ant Design `Table`, `Modal`, `Statistic` |
| `pages/Watchlist.tsx` | Replace with Ant Design `Table`, `Button` |
| `pages/Performance.tsx` | Replace with Ant Design `Card`, `Table` |
| `pages/Settings.tsx` | Replace with Ant Design `Form`, `Switch`, `Select` |
| `services/api.ts` | Add `language` field to analysis request |
| `styles/globals.css` | Convert `margin-left` to `margin-inline-start`, keep CSS variables |
| All components with inline styles | Replace with Ant Design component equivalents |

### Backend

| File | Change |
|------|--------|
| `backend/app/models/schemas.py` | Add `language: str = "en"` to `AnalysisRequest` |
| `backend/app/models/database.py` | Add `language` column to `AnalysisSession` |
| `backend/app/routers/analysis.py` | Pass `language` through to analysis manager |

## Verification

```bash
# Frontend builds without errors
cd frontend && npx tsc --noEmit && npm run build

# Backend passes linting
cd backend && ruff check .

# Manual: Toggle language to Arabic, verify RTL layout
# Manual: Run analysis in Arabic, verify Arabic reports
```

## Migration Order

1. Infrastructure (ConfigProvider, theme, i18n, locale store)
2. Layout shell (Sidebar, Topbar)
3. Pages one at a time (Dashboard → NewAnalysis → History → Portfolio → Watchlist → Performance → Settings)
4. Backend language parameter
5. Full regression test
