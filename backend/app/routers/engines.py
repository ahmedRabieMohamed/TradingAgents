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
    limit: int = Query(50, ge=1, le=228),
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


def _discover_candidates(market_id: str) -> list[tuple[str, str]]:
    """Discover candidate stocks from multiple sources. Returns [(ticker, reason)]."""
    import yfinance as yf
    from tradingagents.default_config import MARKET_REGIONS

    suffix = MARKET_REGIONS.get(market_id, {}).get("ticker_suffix", "")
    candidates: dict[str, str] = {}  # ticker → reason

    # Source 1: EGX30 blue chips (always interesting)
    egx30 = ["COMI", "TMGH", "SWDY", "ETEL", "MFPC", "EGAL", "EAST", "ABUK",
             "ALCN", "HDBK", "EFIH", "FWRY", "ORAS", "ADIB", "HRHO", "EMFD"]
    for t in egx30:
        candidates[t] = "EGX30 component"

    # Source 2: Top movers — stocks with biggest price changes
    try:
        extra_tickers = ["IRON", "CLHO", "JUFO", "SKPC", "ORWE", "PHDC", "OCDI",
                         "ARCC", "MCQE", "POUL", "EGCH", "RAYA", "CIRA", "DOMT",
                         "ISPH", "AMOC", "SUGR", "BINV", "TALM", "MASR"]
        symbols = [f"{t}{suffix}" for t in extra_tickers]
        data = yf.download(" ".join(symbols), period="5d", progress=False)
        if not data.empty and "Close" in data.columns:
            close = data["Close"]
            if hasattr(close, "columns"):
                for sym in close.columns:
                    col = close[sym].dropna()
                    if len(col) >= 2:
                        change = ((col.iloc[-1] / col.iloc[0]) - 1) * 100
                        clean = str(sym).replace(suffix, "")
                        # Only add if significant move (>2% in 5 days)
                        if abs(change) > 2:
                            reason = f"Top mover: {change:+.1f}% in 5d"
                            candidates[clean] = reason
    except Exception:
        pass

    return list(candidates.items())


def _compute_smart_picks(market_id: str, limit: int) -> dict:
    """Discover candidates, batch-fetch prices, score all, rank. Runs in a thread."""
    from tradingagents.dataflows.egypt_tickers import EGX_TICKERS
    from app.services.engines import batch_fetch_price_data, compute_all_engines_from_data

    # Step 1: Discover candidates (NOT all 228)
    candidate_list = _discover_candidates(market_id)
    tickers = [t for t, _ in candidate_list]
    reasons = {t: r for t, r in candidate_list}

    # Step 2: Batch download ALL price data in ONE call (~3-5 seconds)
    logger.info("Smart picks: batch downloading %d tickers...", len(tickers))
    price_data = batch_fetch_price_data(tickers, market_id, days=250)
    logger.info("Smart picks: got data for %d tickers", len(price_data))

    # Step 3: Run engines on each (pure math, no API calls — very fast)
    picks = []
    scored = 0
    failed = 0

    for ticker in tickers:
        reason = reasons.get(ticker, "")
        data = price_data.get(ticker)
        if data is None:
            failed += 1
            continue

        prices, volumes = data
        try:
            result = compute_all_engines_from_data(ticker, prices, volumes, market_id)
            if result.get("error"):
                failed += 1
                continue

            company_info = EGX_TICKERS.get(ticker, {})
            mc = result["engines"].get("monte_carlo", {})
            mom = result["engines"].get("momentum", {})
            vol = result["engines"].get("volume", {})
            sr = result["engines"].get("support_resistance", {})
            mr = result["engines"].get("mean_reversion", {})
            bb = result["engines"].get("bollinger", {})
            corr = result["engines"].get("correlation", {})

            # Count bullish engines
            bullish_count = sum(
                1 for eng in result["engines"].values()
                if eng.get("verdict") == "BULLISH"
            )

            picks.append({
                "ticker": ticker,
                "company_name": company_info.get("name_en", ticker),
                "company_name_ar": company_info.get("name_ar", ticker),
                "sector": company_info.get("sector", "Unknown"),
                "market_id": market_id,
                "reason": reason,
                "combined_score": result["combined_score"],
                "combined_score_raw": result.get("combined_score_raw", result["combined_score"]),
                "volatility_regime_tag": result.get("volatility_regime_tag", "normal"),
                "signal": result["combined_signal"],
                "bullish_engines": bullish_count,
                "total_engines": 7,
                # Monte Carlo details
                "mc_probability": mc.get("prob_up"),
                "mc_expected": mc.get("expected_change"),
                "mc_best_case": mc.get("best_case"),
                "mc_worst_case": mc.get("worst_case"),
                # Momentum details
                "momentum_score": mom.get("score"),
                "momentum_roc_5d": mom.get("roc_5d"),
                "momentum_roc_20d": mom.get("roc_20d"),
                "momentum_trend": mom.get("trend_strength"),
                # Volume details
                "volume_score": vol.get("score"),
                "volume_ratio": vol.get("volume_ratio"),
                "volume_is_real": vol.get("is_real_move"),
                "price_change_pct": vol.get("price_change_pct"),
                # Support/Resistance
                "sr_score": sr.get("score"),
                "sr_support": sr.get("support"),
                "sr_resistance": sr.get("resistance"),
                "sr_current": sr.get("current"),
                "sr_risk_reward": sr.get("risk_reward"),
                "sr_upside_pct": sr.get("upside_pct"),
                "sr_downside_pct": sr.get("downside_pct"),
                # Mean Reversion
                "mr_score": mr.get("score"),
                "mr_distance_pct": mr.get("distance_pct"),
                "mr_is_oversold": mr.get("is_oversold"),
                "mr_is_overbought": mr.get("is_overbought"),
                # Bollinger
                "bb_score": bb.get("score"),
                "bb_band_width": bb.get("band_width"),
                "bb_position": bb.get("position"),
                # Correlation
                "corr_score": corr.get("score"),
                "corr_sector": corr.get("sector"),
                "corr_peers_bullish": corr.get("peers_bullish"),
                "corr_peers_total": corr.get("peers_total"),
                # Full engines for expandable detail
                "engines": result["engines"],
            })
            scored += 1
        except Exception as exc:
            logger.warning("Failed to score %s: %s", ticker, exc)
            failed += 1

    # Sort by combined score descending
    picks.sort(key=lambda p: p["combined_score"], reverse=True)

    # Apply limit if requested
    if limit and limit < len(picks):
        picks = picks[:limit]

    # Assign ranks
    for i, pick in enumerate(picks):
        pick["rank"] = i + 1

    return {
        "market_id": market_id,
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "total_scored": scored,
        "total_failed": failed,
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
