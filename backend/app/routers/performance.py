"""Performance router: aggregate simulation metrics."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.database import AnalysisSession, SimulationResult
from app.models.schemas import PerformanceResponse

router = APIRouter(prefix="/performance", tags=["performance"])


@router.get("", response_model=PerformanceResponse)
async def get_performance(
    market: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Return aggregated performance metrics across all simulated analyses.

    Optionally filter by market_id.
    """
    # Base query: join SimulationResult with AnalysisSession
    base = (
        select(
            AnalysisSession.id,
            AnalysisSession.market_id,
            AnalysisSession.trade_horizon,
            AnalysisSession.recommendation,
            SimulationResult.return_pct,
            SimulationResult.is_win,
        )
        .join(SimulationResult, SimulationResult.session_id == AnalysisSession.id)
    )

    if market:
        base = base.where(AnalysisSession.market_id == market)

    result = await db.execute(base)
    rows = result.all()

    # Total analyses (with or without simulation)
    total_q = select(func.count()).select_from(AnalysisSession)
    if market:
        total_q = total_q.where(AnalysisSession.market_id == market)
    total_analyses = (await db.execute(total_q)).scalar() or 0

    simulated_count = len(rows)

    if simulated_count == 0:
        return PerformanceResponse(
            total_analyses=total_analyses,
            total_simulations=0,
        )

    wins = sum(1 for r in rows if r.is_win)
    win_rate = round((wins / simulated_count) * 100, 1)
    avg_return = round(sum(r.return_pct for r in rows) / simulated_count, 2)

    # Group by market
    by_market: dict[str, dict] = {}
    market_groups: dict[str, list] = {}
    for r in rows:
        market_groups.setdefault(r.market_id, []).append(r)
    for mid, group in market_groups.items():
        m_wins = sum(1 for r in group if r.is_win)
        by_market[mid] = {
            "count": len(group),
            "win_rate": round((m_wins / len(group)) * 100, 1),
            "avg_return_pct": round(sum(r.return_pct for r in group) / len(group), 2),
        }

    # Group by horizon
    by_horizon: dict[str, dict] = {}
    horizon_groups: dict[str, list] = {}
    for r in rows:
        horizon_groups.setdefault(r.trade_horizon, []).append(r)
    for h, group in horizon_groups.items():
        h_wins = sum(1 for r in group if r.is_win)
        by_horizon[h] = {
            "count": len(group),
            "win_rate": round((h_wins / len(group)) * 100, 1),
        }

    return PerformanceResponse(
        total_analyses=total_analyses,
        total_simulations=simulated_count,
        win_rate=win_rate,
        avg_return_pct=avg_return,
        by_market=by_market,
        by_horizon=by_horizon,
    )
