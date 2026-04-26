# Quickstart: Trading Web Application

**Feature**: 001-trading-web-app

## Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend build)
- Existing TradingAgents project cloned and dependencies installed
- At least one LLM provider API key configured

## Setup

### Backend

```bash
# From project root
cd backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
# From project root
cd frontend
npm install

# Start dev server
npm run dev
# Opens at http://localhost:5173
```

## First Analysis

1. Open http://localhost:5173
2. Select a market (US or EGX)
3. Enter a ticker (e.g., AAPL for US, COMI for EGX)
4. Configure: trade horizon, analysts, depth, LLM provider
5. Click "Start Analysis"
6. Watch real-time progress as agents work
7. View the BUY/SELL/HOLD recommendation with confidence

## Project Structure

```
TradingAgents/
├── backend/                    # FastAPI backend (NEW)
│   ├── app/
│   │   ├── main.py            # FastAPI app, CORS, routers
│   │   ├── routers/           # API route handlers
│   │   │   ├── analysis.py    # Analysis CRUD + WebSocket
│   │   │   ├── markets.py     # Market info endpoints
│   │   │   ├── stocks.py      # Ticker validation
│   │   │   ├── performance.py # Performance stats
│   │   │   └── settings.py    # User settings
│   │   ├── models/            # Pydantic schemas + DB models
│   │   ├── services/          # Business logic
│   │   │   ├── analysis.py    # Wraps TradingAgentsGraph
│   │   │   ├── simulation.py  # Result simulation
│   │   │   └── streaming.py   # WebSocket event adapter
│   │   └── database.py        # SQLite setup
│   ├── requirements.txt
│   ├── .env.example
│   └── tests/
│       ├── test_analysis.py
│       ├── test_markets.py
│       └── test_simulation.py
│
├── frontend/                   # React + TypeScript (NEW)
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── NewAnalysis.tsx
│   │   │   ├── History.tsx
│   │   │   ├── Performance.tsx
│   │   │   └── Settings.tsx
│   │   ├── components/
│   │   │   ├── MarketSelector.tsx
│   │   │   ├── TickerInput.tsx
│   │   │   ├── ConfigPanel.tsx
│   │   │   ├── AnalysisProgress.tsx
│   │   │   ├── ResultHero.tsx
│   │   │   ├── ReportSection.tsx
│   │   │   └── PerformanceChart.tsx
│   │   ├── hooks/
│   │   │   ├── useAnalysis.ts
│   │   │   └── useWebSocket.ts
│   │   ├── services/
│   │   │   └── api.ts
│   │   └── types/
│   │       └── index.ts
│   ├── package.json
│   └── tests/
│
├── tradingagents/              # Existing (UNCHANGED)
├── cli/                        # Existing (UNCHANGED)
└── main.py                     # Existing (UNCHANGED)
```

## Key Integration Points

- `backend/app/services/analysis.py` imports `TradingAgentsGraph` from `tradingagents.graph.trading_graph`
- `backend/app/services/streaming.py` adapts LangGraph `.stream()` chunks to WebSocket events
- `backend/app/services/analysis.py` uses `StatsCallbackHandler` from `cli/stats_handler.py`
- Market config loaded from `tradingagents/default_config.py`

## Running Tests

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test

# E2E (requires both servers running)
cd frontend && npx playwright test
```
