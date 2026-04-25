"""Engines router: compute scores, smart picks, and danger alerts."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.database import Position, Portfolio
from app.services.engines import compute_all_engines

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/engines", tags=["engines"])

# In-memory cache for smart picks
_smart_picks_cache: dict[str, Any] = {}


@router.get("/score/{ticker}")
async def get_engine_score(
    ticker: str,
    market_id: str = Query("egypt"),
    days: int = Query(7, ge=1, le=30),
):
    """Compute all 7 engine scores for a single stock."""
    try:
        result = await asyncio.to_thread(
            compute_all_engines, ticker, market_id, mc_days=days
        )
    except Exception as exc:
        logger.exception("Engine computation failed for %s", ticker)
        raise HTTPException(status_code=500, detail=str(exc))

    if result.get("error"):
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/smart-picks")
async def get_smart_picks(
    market_id: str = Query("egypt"),
    limit: int = Query(10, ge=1, le=15),
):
    """Get today's ranked stock opportunities based on news + engines.

    Uses cached results if available (< 1 hour old).
    """
    cache_key = f"{market_id}_{limit}"
    cached = _smart_picks_cache.get(cache_key)

    if cached:
        cache_time = datetime.fromisoformat(cached["computed_at"])
        age = (datetime.now(timezone.utc) - cache_time).total_seconds()
        if age < 3600:  # 1 hour cache
            return cached

    # Discover candidates and score them
    try:
        result = await asyncio.to_thread(
            _compute_smart_picks, market_id, limit
        )
        _smart_picks_cache[cache_key] = result
        return result
    except Exception as exc:
        logger.exception("Smart picks computation failed")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/danger-alerts")
async def get_danger_alerts(
    db: AsyncSession = Depends(get_db),
):
    """Get danger alerts for all open portfolio positions.

    Always computed fresh (not cached) since positions change.
    """
    # Get portfolio with open positions
    result = await db.execute(select(Portfolio).limit(1))
    portfolio = result.scalar_one_or_none()
    if portfolio is None:
        return {"computed_at": datetime.now(timezone.utc).isoformat(), "alerts": []}

    pos_result = await db.execute(
        select(Position).where(
            Position.portfolio_id == portfolio.id,
            Position.status == "open",
        )
    )
    positions = pos_result.scalars().all()

    if not positions:
        return {"computed_at": datetime.now(timezone.utc).isoformat(), "alerts": []}

    # Score each position's stock
    alerts = []
    for pos in positions:
        try:
            scores = await asyncio.to_thread(
                compute_all_engines, pos.ticker, pos.market_id
            )

            combined = scores.get("combined_score", 50)

            # Classify alert level
            if combined < 35:
                alert_level = "red"
                primary_reason = _get_worst_reason(scores)
            elif combined < 55:
                alert_level = "yellow"
                primary_reason = _get_warning_reason(scores)
            else:
                alert_level = "green"
                primary_reason = _get_positive_reason(scores)

            alerts.append({
                "position_id": pos.id,
                "ticker": pos.ticker,
                "market_id": pos.market_id,
                "direction": pos.direction,
                "alert_level": alert_level,
                "combined_score": combined,
                "combined_signal": scores.get("combined_signal", "N/A"),
                "primary_reason": primary_reason,
                "engines": scores.get("engines", {}),
            })
        except Exception as exc:
            logger.warning("Failed to score position %s (%s): %s", pos.ticker, pos.id, exc)
            alerts.append({
                "position_id": pos.id,
                "ticker": pos.ticker,
                "market_id": pos.market_id,
                "direction": pos.direction,
                "alert_level": "yellow",
                "combined_score": 50,
                "combined_signal": "N/A",
                "primary_reason": f"Engine computation failed: {exc}",
                "engines": {},
            })

    # Sort: red first, then yellow, then green
    level_order = {"red": 0, "yellow": 1, "green": 2}
    alerts.sort(key=lambda a: level_order.get(a["alert_level"], 1))

    return {
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "alerts": alerts,
    }


def _compute_smart_picks(market_id: str, limit: int) -> dict:
    """Discover candidate stocks and score them. Runs in a thread."""
    from tradingagents.dataflows.egypt_tickers import EGX_TICKERS

    # Candidates: use top EGX30 stocks + a few others (simulating news + movers discovery)
    # In the future, this will be replaced by real news mention extraction
    # For now, use EGX30 components as candidates
    egx30 = [
        "COMI", "TMGH", "SWDY", "ETEL", "MFPC", "EGAL", "EAST", "ABUK",
        "ALCN", "HDBK", "EFIH", "FWRY", "ORAS", "ADIB", "HRHO",
    ]

    picks = []
    for ticker in egx30[:limit + 5]:  # score a few extra, then trim
        try:
            result = compute_all_engines(ticker, market_id)
            if result.get("error"):
                continue

            company_info = EGX_TICKERS.get(ticker, {})

            picks.append({
                "ticker": ticker,
                "company_name": company_info.get("name_en", ticker),
                "company_name_ar": company_info.get("name_ar", ticker),
                "sector": company_info.get("sector", "Unknown"),
                "market_id": market_id,
                "combined_score": result["combined_score"],
                "signal": result["combined_signal"],
                "mc_probability": result["engines"].get("monte_carlo", {}).get("prob_up"),
                "mc_expected": result["engines"].get("monte_carlo", {}).get("expected_change"),
                "momentum_score": result["engines"].get("momentum", {}).get("score"),
                "volume_ratio": result["engines"].get("volume", {}).get("volume_ratio"),
                "engines": result["engines"],
            })
        except Exception as exc:
            logger.warning("Failed to score %s: %s", ticker, exc)

    # Sort by combined score descending
    picks.sort(key=lambda p: p["combined_score"], reverse=True)
    picks = picks[:limit]

    # Assign ranks
    for i, pick in enumerate(picks):
        pick["rank"] = i + 1

    return {
        "market_id": market_id,
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "picks": picks,
    }


def _get_worst_reason(scores: dict) -> str:
    engines = scores.get("engines", {})
    reasons = []
    mc = engines.get("monte_carlo", {})
    if mc.get("prob_up", 50) < 40:
        reasons.append(f"MC: only {mc['prob_up']}% chance up")
    vol = engines.get("volume", {})
    if vol.get("volume_ratio", 1) > 2 and vol.get("price_change_pct", 0) < 0:
        reasons.append(f"Volume spike {vol['volume_ratio']}x on price drop")
    sr = engines.get("support_resistance", {})
    if sr.get("score", 50) < 30:
        reasons.append("Near or below support level")
    mom = engines.get("momentum", {})
    if mom.get("score", 50) < 30:
        reasons.append("Weak momentum")
    return " · ".join(reasons) if reasons else "Multiple bearish signals"


def _get_warning_reason(scores: dict) -> str:
    engines = scores.get("engines", {})
    reasons = []
    mr = engines.get("mean_reversion", {})
    if mr.get("is_overbought"):
        reasons.append("Overbought — may pull back")
    sr = engines.get("support_resistance", {})
    if sr.get("score", 50) < 45:
        reasons.append("Approaching resistance")
    return " · ".join(reasons) if reasons else "Mixed signals"


def _get_positive_reason(scores: dict) -> str:
    engines = scores.get("engines", {})
    reasons = []
    mc = engines.get("monte_carlo", {})
    if mc.get("prob_up", 50) > 60:
        reasons.append(f"MC: {mc['prob_up']}% chance up")
    mom = engines.get("momentum", {})
    if mom.get("verdict") == "BULLISH":
        reasons.append("Strong momentum")
    vol = engines.get("volume", {})
    if vol.get("is_real_move"):
        reasons.append("Volume confirms move")
    return " · ".join(reasons) if reasons else "Positive signals overall"
