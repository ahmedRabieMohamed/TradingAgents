# Implementation Plan: 7 Trading Engines + Smart Picks + Danger Alerts

**Branch**: `010-engines-smart-picks` | **Date**: 2026-04-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/010-engines-smart-picks/spec.md`

## Summary

Add 7 quantitative trading engines (Monte Carlo, Momentum, Volume Confirmation, Support/Resistance, Mean Reversion, Bollinger Bands, Correlation) as a backend service. Combine with news sentiment to produce scored stock rankings ("Smart Picks") and position monitoring ("Danger Alerts"). All engines use free yfinance historical price data and numpy math — no paid APIs.

## Technical Context

**Language/Version**: Python 3.10+ (backend engines), TypeScript 5.x (frontend display)
**Primary Dependencies**: numpy (new — for MC simulations + stats), existing yfinance, FastAPI, React 18, Ant Design 5.x, Recharts (for histograms/charts)
**Storage**: SQLite — new table for engine scores persisted with analysis sessions
**Testing**: Manual verification per constitution
**Target Platform**: Web — existing SPA
**Project Type**: Web application (React SPA + Python API)
**Performance Goals**: All 7 engines on 1 stock in <5 seconds; Monte Carlo 10K simulations in <2 seconds
**Constraints**: Zero paid APIs; all computation from free OHLCV data
**Scale/Scope**: 7 engine classes + 3 API endpoints + 2 new pages + 1 new Zustand store

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Research | Post-Design | Notes |
|-----------|-------------|-------------|-------|
| I. Simplicity First | PASS | PASS | Each engine is a pure function: prices in → score out. No abstractions needed. 7 simple functions, not 1 complex framework. |
| II. Correctness Over Speed | PASS | PASS | Financial calculations use numpy float64. Monte Carlo uses validated GBM model. Edge cases (insufficient data, NaN) handled per engine. |
| III. Separation of Concerns | PASS | PASS | Engines = backend service layer. API contracts documented. Frontend reads scores from REST API. Engine logic never touches routes or UI. |
| IV. Incremental Delivery | PASS | PASS | Each engine is independently testable. Smart Picks works with even 1 engine. Danger Alerts work independently. |
| V. Data Integrity | PASS | PASS | Engine scores stored as JSON column on AnalysisSession — additive, backward-compatible. No existing data modified. |

**Gate result**: ALL PASS

## Project Structure

### Documentation (this feature)

```text
specs/010-engines-smart-picks/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── rest-api.md      # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit-tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── services/
│   │   ├── engines/              # NEW — all 7 engine modules
│   │   │   ├── __init__.py       # Engine registry + combined scorer
│   │   │   ├── monte_carlo.py    # MC simulation engine
│   │   │   ├── momentum.py       # Momentum/ROC engine
│   │   │   ├── volume.py         # Volume confirmation engine
│   │   │   ├── support_resistance.py  # S/R level detection
│   │   │   ├── mean_reversion.py # Mean reversion engine
│   │   │   ├── bollinger.py      # Bollinger band engine
│   │   │   └── correlation.py    # Sector correlation engine
│   │   ├── smart_picks.py        # NEW — news discovery + scoring orchestrator
│   │   └── news_sentiment.py     # NEW — news sentiment scoring
│   ├── routers/
│   │   └── engines.py            # NEW — API endpoints for engines
│   └── models/
│       └── schemas.py            # Add engine score schemas

frontend/
├── src/
│   ├── pages/
│   │   └── SmartPicks.tsx         # NEW — Smart Picks + Danger Alerts page
│   ├── components/
│   │   └── engines/               # NEW — engine display components
│   │       ├── EngineBreakdown.tsx # Combined score + 7 engine bars
│   │       ├── MonteCarloPanel.tsx # MC histogram + stats
│   │       ├── VolumePanel.tsx    # Volume bars chart
│   │       ├── SupportResistPanel.tsx  # S/R visual
│   │       ├── DangerAlerts.tsx   # Position alerts
│   │       └── SmartPicksTable.tsx # Ranked picks table
│   ├── stores/
│   │   └── engineStore.ts         # NEW — engine scores state
│   ├── services/
│   │   └── api.ts                 # Add engine API calls
│   └── locales/
│       ├── en/engines.json        # NEW — engine translations
│       └── ar/engines.json        # NEW — Arabic engine translations
```

**Structure Decision**: Engine modules are simple Python functions in a `services/engines/` package. No class hierarchies, no abstract base classes — just functions that take price arrays and return scores.

## Complexity Tracking

> No Constitution violations — this section is not applicable.
