# TradingAgents Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-08

## Active Technologies
- Python 3.10+ (backend), TypeScript 5.x (frontend) + FastAPI, yfinance (backend); React 18, Zustand (frontend) — all already installed from 001 (002-market-overview-news)
- In-memory caching for stock prices (refreshed on demand); existing news infrastructure reused (002-market-overview-news)
- Python 3.10+ (backend), TypeScript 5.x (frontend) — existing stack + FastAPI, SQLAlchemy, yfinance (backend); React 18, Zustand, Recharts (frontend — Recharts new for equity curve) (003-paper-trading-simulation)
- SQLite — new tables for Portfolio, Position, Trade alongside existing AnalysisSession (003-paper-trading-simulation)
- Python 3.10+ (backend), TypeScript 5.x (frontend) + FastAPI, yfinance (backend); React 18, Zustand, (004-candlestick-analysis-view)
- N/A — no database changes (004-candlestick-analysis-view)
- TypeScript 5.x (frontend only) + React 18, react-markdown (new), remark-gfm (new) (005-ui-polish-markdown)
- N/A — no backend changes (005-ui-polish-markdown)

- Python 3.10+ (backend), TypeScript 5.x (frontend) + FastAPI, uvicorn, SQLAlchemy (backend); React 18, Vite, React Router, Zustand (frontend) (001-trading-web-app)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.10+ (backend), TypeScript 5.x (frontend): Follow standard conventions

## Recent Changes
- 005-ui-polish-markdown: Added TypeScript 5.x (frontend only) + React 18, react-markdown (new), remark-gfm (new)
- 004-candlestick-analysis-view: Added Python 3.10+ (backend), TypeScript 5.x (frontend) + FastAPI, yfinance (backend); React 18, Zustand,
- 003-paper-trading-simulation: Added Python 3.10+ (backend), TypeScript 5.x (frontend) — existing stack + FastAPI, SQLAlchemy, yfinance (backend); React 18, Zustand, Recharts (frontend — Recharts new for equity curve)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
