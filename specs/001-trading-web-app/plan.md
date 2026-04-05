# Implementation Plan: Trading Web Application

**Branch**: `001-trading-web-app` | **Date**: 2026-04-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-trading-web-app/spec.md`

## Summary

Build a web application that mirrors the existing CLI flow for multi-agent stock analysis. The app provides a visual interface for market/stock selection, analysis configuration, real-time pipeline progress, detailed report viewing, analysis history, and performance simulation. The backend wraps the existing `TradingAgentsGraph` engine with a FastAPI REST + WebSocket API. The frontend is a React/TypeScript SPA that streams analysis updates in real-time.

## Technical Context

**Language/Version**: Python 3.10+ (backend), TypeScript 5.x (frontend)  
**Primary Dependencies**: FastAPI, uvicorn, SQLAlchemy (backend); React 18, Vite, React Router, Zustand (frontend)  
**Storage**: SQLite (analysis history/metadata), file-based Markdown (report content — existing format)  
**Testing**: pytest + httpx (backend), Vitest (frontend), Playwright (E2E)  
**Target Platform**: Desktop/laptop browsers (Chrome, Firefox, Safari); server runs locally  
**Project Type**: Web application (backend API + frontend SPA)  
**Performance Goals**: Analysis progress updates streamed to browser within 1 second of generation; history page loads in under 500ms  
**Constraints**: Single-user deployment; no auth required; must not modify existing `tradingagents/` or `cli/` packages  
**Scale/Scope**: 2 markets, ~5 screens, 18 functional requirements, ~15 API endpoints + 1 WebSocket

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution file contains only placeholder templates — no actual gates defined. **PASS** (no constraints to evaluate).

**Post-Phase 1 Re-Check**: Still PASS — no constitution gates defined.

## Project Structure

### Documentation (this feature)

```text
specs/001-trading-web-app/
├── plan.md              # This file
├── spec.md              # Feature specification
├── prototype.html       # Interactive UI mockup
├── research.md          # Phase 0: Technology decisions
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Setup guide
├── contracts/           # Phase 1: API contracts
│   ├── rest-api.md      # REST endpoint definitions
│   └── websocket-api.md # WebSocket streaming protocol
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py                # FastAPI app entry, CORS, router registration
│   ├── database.py            # SQLite engine + session factory
│   ├── routers/
│   │   ├── analysis.py        # POST/GET/DELETE analysis + WebSocket streaming
│   │   ├── markets.py         # GET markets list
│   │   ├── stocks.py          # GET ticker validation
│   │   ├── performance.py     # GET aggregate stats
│   │   ├── settings.py        # GET/PATCH user settings
│   │   └── llm_providers.py   # GET available providers/models
│   ├── models/
│   │   ├── database.py        # SQLAlchemy ORM models
│   │   └── schemas.py         # Pydantic request/response schemas
│   ├── services/
│   │   ├── analysis.py        # Wraps TradingAgentsGraph, manages sessions
│   │   ├── streaming.py       # Adapts LangGraph stream chunks → WebSocket events
│   │   ├── simulation.py      # Computes result simulations from market data
│   │   ├── stock_info.py      # Ticker validation via yfinance
│   │   └── settings.py        # Settings CRUD
│   └── config.py              # App config, env vars
├── requirements.txt
├── .env.example
├── alembic.ini                # DB migrations (optional, SQLite)
└── tests/
    ├── conftest.py
    ├── test_analysis.py
    ├── test_markets.py
    ├── test_stocks.py
    ├── test_simulation.py
    └── test_settings.py

frontend/
├── src/
│   ├── App.tsx                # Root component, router setup
│   ├── main.tsx               # Entry point
│   ├── pages/
│   │   ├── NewAnalysis.tsx    # 5-step wizard (market → stock → config → progress → results)
│   │   ├── History.tsx        # Analysis history with filters
│   │   ├── Performance.tsx    # Performance dashboard + simulation results
│   │   └── Settings.tsx       # API keys & default config
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   └── Topbar.tsx
│   │   ├── analysis/
│   │   │   ├── MarketSelector.tsx
│   │   │   ├── TickerInput.tsx
│   │   │   ├── ConfigPanel.tsx
│   │   │   ├── AnalysisProgress.tsx
│   │   │   ├── PipelineStage.tsx
│   │   │   ├── MessageLog.tsx
│   │   │   ├── StatsBar.tsx
│   │   │   ├── ResultHero.tsx
│   │   │   └── ReportSection.tsx
│   │   ├── history/
│   │   │   ├── HistoryTable.tsx
│   │   │   └── FilterBar.tsx
│   │   └── performance/
│   │       ├── PerfCard.tsx
│   │       ├── MarketPerf.tsx
│   │       └── SimulationTable.tsx
│   ├── hooks/
│   │   ├── useAnalysis.ts     # Analysis creation + state management
│   │   ├── useWebSocket.ts    # WebSocket connection + event handling
│   │   └── useApi.ts          # REST API wrapper
│   ├── services/
│   │   └── api.ts             # HTTP client (fetch-based)
│   ├── stores/
│   │   └── analysisStore.ts   # Zustand store for analysis state
│   ├── types/
│   │   └── index.ts           # TypeScript interfaces matching API schemas
│   └── styles/
│       └── globals.css        # CSS variables, base styles (dark theme)
├── package.json
├── tsconfig.json
├── vite.config.ts
├── index.html
└── tests/
    ├── components/
    └── e2e/
```

**Structure Decision**: Web application with separate `backend/` and `frontend/` directories. The existing `tradingagents/`, `cli/`, and `main.py` remain entirely untouched. The backend imports from `tradingagents` as a library. This keeps the web app as a pure layer on top of the existing system.

## Complexity Tracking

No constitution violations — table not needed.
