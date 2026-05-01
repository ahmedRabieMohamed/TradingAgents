# TradingAgents Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-05-01

## Active Technologies
- Python 3.10+ (backend), TypeScript 5.x (frontend) + FastAPI, yfinance (backend); React 18, Zustand (frontend) — all already installed from 001 (002-market-overview-news)
- In-memory caching for stock prices (refreshed on demand); existing news infrastructure reused (002-market-overview-news)
- Python 3.10+ (backend), TypeScript 5.x (frontend) — existing stack + FastAPI, SQLAlchemy, yfinance (backend); React 18, Zustand, Recharts (frontend — Recharts new for equity curve) (003-paper-trading-simulation)
- SQLite — new tables for Portfolio, Position, Trade alongside existing AnalysisSession (003-paper-trading-simulation)
- Python 3.10+ (backend), TypeScript 5.x (frontend) + FastAPI, yfinance (backend); React 18, Zustand, (004-candlestick-analysis-view)
- N/A — no database changes (004-candlestick-analysis-view)
- TypeScript 5.x (frontend only) + React 18, react-markdown (new), remark-gfm (new) (005-ui-polish-markdown)
- N/A — no backend changes (005-ui-polish-markdown)
- TypeScript 5.9 (frontend), Python 3.10+ (backend) + React 19, Ant Design 5.x (new), react-i18next (new), i18next (new), @ant-design/icons (new), dayjs (new — antd peer dep); FastAPI, SQLAlchemy (backend — existing) (006-pro-ui-arabic-support)
- localStorage (language preference), SQLite (language column on AnalysisSession) (006-pro-ui-arabic-support)
- TypeScript 5.9 (frontend), Python 3.10+ (backend — unchanged for this feature) + React 19, React Router 7, Ant Design 6.x, Zustand 5, react-i18next 17, recharts 3, lightweight-charts 5 (existing); **`motion` v11+** (new — Framer Motion successor, React 19 compatible), **`@react-spring/web`** considered and rejected (see research.md) (011-animated-ui-redesign)
- N/A (frontend-only feature; no schema or persistence changes) (011-animated-ui-redesign)
- Python 3.10+ (backend), TypeScript 5.9 (frontend) + FastAPI, SQLAlchemy, NumPy (backend — all already present); React 19, AntD 6, react-i18next 17, `motion` v11+, Recharts (frontend — all from prior branches) (012-smart-picks-overhaul)
- No schema changes. Smart Picks is computed in-memory on demand; results are not persisted. (012-smart-picks-overhaul)

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
- 012-smart-picks-overhaul: Added Python 3.10+ (backend), TypeScript 5.9 (frontend) + FastAPI, SQLAlchemy, NumPy (backend — all already present); React 19, AntD 6, react-i18next 17, `motion` v11+, Recharts (frontend — all from prior branches)
- 011-animated-ui-redesign: Added TypeScript 5.9 (frontend), Python 3.10+ (backend — unchanged for this feature) + React 19, React Router 7, Ant Design 6.x, Zustand 5, react-i18next 17, recharts 3, lightweight-charts 5 (existing); **`motion` v11+** (new — Framer Motion successor, React 19 compatible), **`@react-spring/web`** considered and rejected (see research.md)
- 006-pro-ui-arabic-support: Added TypeScript 5.9 (frontend), Python 3.10+ (backend) + React 19, Ant Design 5.x (new), react-i18next (new), i18next (new), @ant-design/icons (new), dayjs (new — antd peer dep); FastAPI, SQLAlchemy (backend — existing)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
