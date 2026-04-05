"""Simulation service: evaluate analysis predictions against actual market data."""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database import AnalysisSession, SimulationResult

logger = logging.getLogger(__name__)

# Trading-day offsets for each horizon
HORIZON_TRADING_DAYS: dict[str, int] = {
    "intraday": 0,
    "short-term": 5,
    "medium-term": 20,
    "long-term": 60,
}


def _add_trading_days(start: date, trading_days: int) -> date:
    """Advance *start* by *trading_days* business days (Mon-Fri).

    For intraday (0), the horizon end is the same day.
    """
    if trading_days == 0:
        return start
    current = start
    added = 0
    while added < trading_days:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Mon-Fri
            added += 1
    return current


def _compute_horizon_end(analysis_date: date, trade_horizon: str) -> date:
    days = HORIZON_TRADING_DAYS.get(trade_horizon)
    if days is None:
        raise ValueError(f"Unknown trade horizon: {trade_horizon}")
    return _add_trading_days(analysis_date, days)


def _fetch_price_yfinance(ticker: str, target_date: date) -> float | None:
    """Fetch the closing price for *ticker* on or near *target_date* via yfinance.

    Returns None if no data is available.
    """
    try:
        import yfinance as yf

        # Fetch a small window around the target date to handle weekends/holidays
        start = target_date - timedelta(days=5)
        end = target_date + timedelta(days=5)
        df = yf.download(ticker, start=start.isoformat(), end=end.isoformat(), progress=False)

        if df.empty:
            return None

        # Find the closest date on or before target_date
        valid = df.loc[df.index.date <= target_date]
        if valid.empty:
            # Fall back to closest date after
            valid = df
        row = valid.iloc[-1]
        close = row["Close"]
        # yfinance may return a Series for multi-ticker; handle scalar
        if hasattr(close, "item"):
            return float(close.item())
        return float(close)
    except Exception:
        logger.exception("Failed to fetch price for %s on %s", ticker, target_date)
        return None


def _determine_win(recommendation: str | None, return_pct: float) -> bool:
    """Determine whether the recommendation was correct.

    - BUY wins if return > 0
    - SELL wins if return < 0
    - HOLD wins if abs(return) < 2%
    """
    rec = (recommendation or "").upper()
    if rec == "BUY":
        return return_pct > 0
    elif rec == "SELL":
        return return_pct < 0
    else:
        # HOLD or unknown
        return abs(return_pct) < 2.0


async def simulate_analysis(session_id: str, db: AsyncSession) -> SimulationResult:
    """Run a simulation for a completed analysis session.

    Raises ValueError for invalid state, RuntimeError for data issues.
    """
    # Load session with existing simulation
    result = await db.execute(
        select(AnalysisSession)
        .where(AnalysisSession.id == session_id)
        .options(selectinload(AnalysisSession.simulation_result))
    )
    session = result.scalar_one_or_none()

    if session is None:
        raise ValueError("Analysis session not found")

    if session.status != "completed":
        raise ValueError(f"Session status is '{session.status}', must be 'completed'")

    if session.simulation_result is not None:
        raise ValueError("Simulation already exists for this session")

    # Compute horizon end date
    horizon_end = _compute_horizon_end(session.analysis_date, session.trade_horizon)

    # Check if horizon has elapsed
    today = date.today()
    if today < horizon_end:
        raise ValueError(
            f"Trade horizon has not elapsed yet. End date: {horizon_end.isoformat()}"
        )

    # Entry price
    entry_price = session.stock_price_at_analysis
    if entry_price is None:
        # Try to fetch it
        entry_price_fetched = _fetch_price_yfinance(session.ticker, session.analysis_date)
        if entry_price_fetched is None:
            raise RuntimeError(
                f"Cannot determine entry price for {session.ticker} on {session.analysis_date}"
            )
        entry_price = entry_price_fetched

    # Exit price
    exit_price = _fetch_price_yfinance(session.ticker, horizon_end)
    if exit_price is None:
        raise RuntimeError(
            f"Cannot fetch exit price for {session.ticker} on {horizon_end}"
        )

    # Compute return
    return_pct = ((exit_price - entry_price) / entry_price) * 100.0

    # Determine win
    is_win = _determine_win(session.recommendation, return_pct)

    # Persist
    sim = SimulationResult(
        session_id=session_id,
        entry_price=entry_price,
        exit_price=exit_price,
        horizon_end_date=horizon_end,
        return_pct=round(return_pct, 2),
        is_win=is_win,
    )
    db.add(sim)
    await db.flush()
    await db.refresh(sim)

    logger.info(
        "Simulation for session %s: entry=%.2f exit=%.2f return=%.2f%% win=%s",
        session_id,
        entry_price,
        exit_price,
        return_pct,
        is_win,
    )

    return sim
