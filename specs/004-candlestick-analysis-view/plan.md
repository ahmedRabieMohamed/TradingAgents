# Implementation Plan: Candlestick Chart & Analysis State Persistence

**Branch**: `004-candlestick-analysis-view` | **Date**: 2026-04-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-candlestick-analysis-view/spec.md`

## Summary

Add a candlestick (OHLC) chart to the analysis wizard after ticker
validation, and fix the bug where navigating away from the analysis
page loses all wizard state. The chart uses lightweight-charts
(TradingView) with data from a new backend endpoint. State persistence
is achieved by migrating wizard state from local useState to a Zustand
store.

## Technical Context

**Language/Version**: Python 3.10+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, yfinance (backend); React 18, Zustand,
lightweight-charts (frontend — new dependency)
**Storage**: N/A — no database changes
**Testing**: Manual verification per quickstart.md
**Target Platform**: Web browser (desktop)
**Project Type**: Web application (backend API + SPA frontend)
**Performance Goals**: Chart renders within 3 seconds, time range switch
within 2 seconds
**Constraints**: yfinance rate limits (not an issue for single-user app)
**Scale/Scope**: Single user, single ticker at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Simplicity First | PASS | Minimal changes: 1 new endpoint, 1 new component, 1 store migration. lightweight-charts justified (recharts lacks candlestick). |
| II. Correctness Over Speed | PASS | OHLC data from yfinance (authoritative source). Currency labels match market. Error states handled. |
| III. Separation of Concerns | PASS | Backend fetches OHLC data via service layer. Frontend renders via documented API contract. Wizard state in Zustand store (not prop drilling). |
| IV. Incremental Delivery | PASS | Two independent P1 stories. Chart works without state fix; state fix works without chart. Each testable independently. |
| V. Data Integrity | PASS | No database changes. OHLC data is read-only from yfinance. Wizard state is ephemeral (in-memory). |

## Project Structure

### Documentation (this feature)

```text
specs/004-candlestick-analysis-view/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── rest-api.md      # Phase 1 output
└── tasks.md             # Phase 2 output (via /speckit-tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── routers/
│   │   └── stocks.py          # ADD: price-history endpoint
│   ├── services/
│   │   └── market_data.py     # ADD: get_price_history() function
│   └── models/
│       └── schemas.py         # ADD: OHLCBar, PriceHistoryResponse

frontend/
├── src/
│   ├── stores/
│   │   └── wizardStore.ts     # NEW: wizard state store
│   ├── components/
│   │   └── analysis/
│   │       └── CandlestickChart.tsx  # NEW: chart component
│   ├── pages/
│   │   └── NewAnalysis.tsx    # MODIFY: use wizardStore, add chart
│   ├── services/
│   │   └── api.ts             # ADD: getPriceHistory() function
│   └── types/
│       └── index.ts           # ADD: OHLCBar, PriceHistoryResponse types
```

**Structure Decision**: Web application (backend + frontend). All changes
are additions to existing files or new files within existing directories.
No structural changes needed.

## Complexity Tracking

No constitution violations to justify.
