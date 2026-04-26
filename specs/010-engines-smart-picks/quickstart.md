# Quickstart: 010 — 7 Trading Engines + Smart Picks + Danger Alerts

**Date**: 2026-04-25

## Prerequisites

- Existing TradingAgents app running (backend + frontend)
- Python 3.10+ with numpy (add if not installed)
- yfinance (already installed)

## Install New Dependencies

```bash
cd backend
pip install numpy  # If not already installed
```

No new frontend dependencies — uses existing Ant Design + Recharts.

## Key Files to Create

### Backend

| File | Purpose |
|------|---------|
| `backend/app/services/engines/__init__.py` | Engine registry + `compute_all_engines()` orchestrator |
| `backend/app/services/engines/monte_carlo.py` | GBM simulation → prob_up, expected, range |
| `backend/app/services/engines/momentum.py` | ROC + trend strength scoring |
| `backend/app/services/engines/volume.py` | Volume ratio + real/fake move detection |
| `backend/app/services/engines/support_resistance.py` | S/R level detection + risk/reward |
| `backend/app/services/engines/mean_reversion.py` | Distance from SMA + oversold detection |
| `backend/app/services/engines/bollinger.py` | Band width + squeeze/expansion |
| `backend/app/services/engines/correlation.py` | Sector peer correlation |
| `backend/app/services/smart_picks.py` | News discovery + candidate scoring |
| `backend/app/services/news_sentiment.py` | LLM-based article sentiment scoring |
| `backend/app/routers/engines.py` | 3 API endpoints |

### Frontend

| File | Purpose |
|------|---------|
| `frontend/src/pages/SmartPicks.tsx` | Smart Picks + Danger Alerts page |
| `frontend/src/components/engines/EngineBreakdown.tsx` | Combined score + 7 gauge bars |
| `frontend/src/components/engines/MonteCarloPanel.tsx` | MC histogram + probability stats |
| `frontend/src/components/engines/VolumePanel.tsx` | Volume bar chart |
| `frontend/src/components/engines/DangerAlerts.tsx` | Red/yellow/green position alerts |
| `frontend/src/components/engines/SmartPicksTable.tsx` | Ranked picks table |
| `frontend/src/stores/engineStore.ts` | Engine scores Zustand store |
| `frontend/src/locales/en/engines.json` | English translations |
| `frontend/src/locales/ar/engines.json` | Arabic translations |

### Files to Modify

| File | Change |
|------|--------|
| `backend/app/models/database.py` | Add `engine_scores` JSON column to AnalysisSession |
| `backend/app/models/schemas.py` | Add engine score response schemas |
| `backend/app/main.py` | Register engines router |
| `frontend/src/App.tsx` | Add SmartPicks route |
| `frontend/src/components/layout/Sidebar.tsx` | Add Smart Picks nav item |
| `frontend/src/services/api.ts` | Add engine API calls |
| `frontend/src/i18n.ts` | Register engines namespace |
| `frontend/src/pages/NewAnalysis.tsx` | Show engine breakdown in results |

## Verification

```bash
# Backend
cd backend && ruff check . && python3 -m py_compile app/services/engines/__init__.py

# Frontend
cd frontend && npx tsc --noEmit && npm run build

# Manual: Open Smart Picks page → see ranked stocks
# Manual: Open any analysis → see 7 engine breakdown
# Manual: Open Danger Alerts → see position alerts
```

## Build Order

1. Backend engines (7 Python modules) — can test independently
2. Backend API endpoints (3 routes)
3. Frontend engine display components
4. Frontend Smart Picks page
5. Integration: wire engines into existing analysis flow
6. News discovery service
7. Danger Alerts
