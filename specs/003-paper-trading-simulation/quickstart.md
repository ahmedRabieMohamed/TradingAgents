# Quickstart: Paper Trading & Portfolio Simulation

**Feature**: 003-paper-trading-simulation  
**Depends on**: 001-trading-web-app

## New Files

### Backend
- `backend/app/routers/portfolio.py` — 6 endpoints (portfolio, trade, close, trades, analytics, ai-comparison)
- `backend/app/services/portfolio.py` — Trade execution, P&L calculation, analytics
- `backend/app/models/database.py` — Modified: Portfolio, Position, EquitySnapshot models
- `backend/app/models/schemas.py` — Modified: Portfolio Pydantic schemas

### Frontend
- `frontend/src/pages/Portfolio.tsx` — New page
- `frontend/src/components/portfolio/` — 7 new components
- `frontend/src/hooks/usePortfolio.ts` — Portfolio data hook
- `frontend/src/stores/portfolioStore.ts` — Portfolio state
- `frontend/package.json` — Modified: add recharts dependency

## Testing Flow

1. Run an analysis for AAPL (US market)
2. On results page, click "Execute Trade"
3. Set quantity (e.g., 50 shares), confirm
4. Navigate to Portfolio page
5. See the open position with live P&L
6. Click "Close Position" on the row
7. Confirm close → see realized P&L
8. Check trade history and analytics
9. Run more analyses without executing → check AI comparison
