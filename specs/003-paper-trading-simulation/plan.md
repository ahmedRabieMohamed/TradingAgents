# Implementation Plan: Paper Trading & Portfolio Simulation

**Branch**: `003-paper-trading-simulation` | **Date**: 2026-04-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-paper-trading-simulation/spec.md`

## Summary

Add paper trading capabilities to the existing web app. Users can execute virtual trades from AI analysis results, track open positions with live P&L, close positions to realize gains/losses, view portfolio performance analytics, and compare outcomes of following vs ignoring AI recommendations. Enhancement to existing 001-trading-web-app backend and frontend.

## Technical Context

**Language/Version**: Python 3.10+ (backend), TypeScript 5.x (frontend) — existing stack  
**Primary Dependencies**: FastAPI, SQLAlchemy, yfinance (backend); React 18, Zustand, Recharts (frontend — Recharts new for equity curve)  
**Storage**: SQLite — new tables for Portfolio, Position, Trade alongside existing AnalysisSession  
**Testing**: pytest (backend), Vitest (frontend) — from 001  
**Target Platform**: Desktop/laptop browsers  
**Project Type**: Web application enhancement  
**Performance Goals**: Portfolio dashboard loads < 2 seconds; P&L calculations accurate to 2 decimal places  
**Constraints**: Paper trading only; no broker API; yfinance 15-min delay; single user; full closes only  
**Scale/Scope**: 4 new DB tables, ~6 new API endpoints, 1 new page + components on existing pages

## Constitution Check

No gates defined. **PASS**.

## Project Structure

### Documentation

```text
specs/003-paper-trading-simulation/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Technology decisions
├── data-model.md        # New DB entities
├── quickstart.md        # Testing guide
└── contracts/
    └── rest-api.md      # New endpoints
```

### Source Code (additions to existing structure)

```text
backend/
├── app/
│   ├── routers/
│   │   └── portfolio.py         # NEW: Portfolio + position CRUD, trade execution
│   ├── services/
│   │   └── portfolio.py         # NEW: Trade execution, P&L calc, portfolio stats
│   └── models/
│       └── database.py          # MODIFIED: Add Portfolio, Position, Trade models
│       └── schemas.py           # MODIFIED: Add portfolio Pydantic schemas

frontend/
├── src/
│   ├── pages/
│   │   ├── Portfolio.tsx         # NEW: Portfolio dashboard page
│   │   └── NewAnalysis.tsx       # MODIFIED: Add "Execute Trade" button to results
│   ├── components/
│   │   └── portfolio/            # NEW directory
│   │       ├── PortfolioSummary.tsx   # Balance, value, P&L bar
│   │       ├── PositionsTable.tsx     # Open positions with live P&L
│   │       ├── TradeHistory.tsx       # Closed trades list
│   │       ├── TradeModal.tsx         # Execute/close trade dialog
│   │       ├── EquityCurve.tsx        # Portfolio value over time chart
│   │       ├── PortfolioAnalytics.tsx # Win rate, avg return, by-market
│   │       └── AIComparison.tsx       # Followed vs Ignored comparison
│   ├── stores/
│   │   └── portfolioStore.ts     # NEW: Portfolio state
│   ├── hooks/
│   │   └── usePortfolio.ts       # NEW: Portfolio data fetching
│   └── types/
│       └── index.ts              # MODIFIED: Add portfolio types
```

**Structure Decision**: Enhancement to existing app. 1 new backend router + 1 service. 1 new frontend page + 7 components. New Recharts dependency for equity curve chart.

## Complexity Tracking

No violations.
