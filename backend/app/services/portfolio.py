"""Portfolio & paper-trading service layer."""

from __future__ import annotations

from datetime import datetime, date as date_type
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database import (
    AnalysisSession,
    EquitySnapshot,
    Portfolio,
    Position,
    SimulationResult,
)
from app.models.schemas import (
    AIComparisonResponse,
    AIComparisonSide,
    ClosePositionResponse,
    EquityPointSchema,
    MarketBreakdown,
    PortfolioAnalyticsResponse,
    PortfolioResponse,
    PositionResponse,
    TradeExecutionResponse,
    TradeHistoryItem,
    TradeHistoryResponse,
    TradeRequest,
    TradeSummary,
)

from tradingagents.default_config import MARKET_REGIONS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_yf_symbol(ticker: str, market_id: str) -> str:
    """Return the yfinance-compatible symbol for *ticker* in *market_id*."""
    region_cfg = MARKET_REGIONS.get(market_id, {})
    suffix = region_cfg.get("ticker_suffix", "")
    return f"{ticker.upper()}{suffix}"


def _fetch_current_price(ticker: str, market_id: str) -> float | None:
    """Fetch the current/latest market price via yfinance (synchronous).

    Uses history API as primary source (more reliable for EGX and other
    emerging-market exchanges where .info can return stale prices), with
    .info as fallback.

    Returns *None* when the price cannot be determined so callers can fall
    back gracefully.
    """
    import yfinance  # lazy import

    symbol = _get_yf_symbol(ticker, market_id)
    try:
        yf_ticker = yfinance.Ticker(symbol)

        # Primary: last close from recent history (most reliable across all markets)
        hist = yf_ticker.history(period="5d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])

        # Fallback: .info fields
        info: dict = yf_ticker.info or {}
        price = info.get("regularMarketPrice") or info.get("currentPrice")
        return float(price) if price is not None else None
    except Exception:
        return None


def _days_between(start: datetime, end: datetime | None = None) -> int:
    end = end or datetime.utcnow()
    return max((end - start).days, 0)


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


async def get_or_create_portfolio(db: AsyncSession) -> Portfolio:
    """Return the single portfolio, creating one if it doesn't exist."""
    result = await db.execute(select(Portfolio).limit(1))
    portfolio = result.scalar_one_or_none()
    if portfolio is None:
        portfolio = Portfolio(id=str(uuid4()))
        db.add(portfolio)
        await db.flush()
    return portfolio


async def get_portfolio_with_positions(db: AsyncSession) -> PortfolioResponse:
    """Load the portfolio and enrich open positions with live prices."""
    portfolio = await get_or_create_portfolio(db)

    result = await db.execute(
        select(Position)
        .where(Position.portfolio_id == portfolio.id, Position.status == "open")
        .options(selectinload(Position.analysis_session))
    )
    open_positions = result.scalars().all()

    positions_value = 0.0
    enriched: list[PositionResponse] = []

    for pos in open_positions:
        current_price = _fetch_current_price(pos.ticker, pos.market_id)
        if current_price is None:
            current_price = pos.entry_price  # fallback

        if pos.direction == "long":
            unrealized_pnl = (current_price - pos.entry_price) * pos.quantity
        else:
            unrealized_pnl = (pos.entry_price - current_price) * pos.quantity

        unrealized_pnl_pct = (
            (unrealized_pnl / (pos.entry_price * pos.quantity)) * 100
            if pos.entry_price
            else 0.0
        )
        market_value = current_price * pos.quantity
        positions_value += market_value

        session = pos.analysis_session
        enriched.append(
            PositionResponse(
                id=pos.id,
                portfolio_id=pos.portfolio_id,
                analysis_session_id=pos.analysis_session_id,
                ticker=pos.ticker,
                market_id=pos.market_id,
                direction=pos.direction,
                quantity=pos.quantity,
                entry_price=pos.entry_price,
                entry_date=pos.entry_date,
                exit_price=pos.exit_price,
                exit_date=pos.exit_date,
                status=pos.status,
                realized_pnl=pos.realized_pnl,
                realized_pnl_pct=pos.realized_pnl_pct,
                current_price=round(current_price, 4),
                unrealized_pnl=round(unrealized_pnl, 2),
                unrealized_pnl_pct=round(unrealized_pnl_pct, 2),
                days_held=_days_between(pos.entry_date),
                recommendation=session.recommendation if session else None,
                confidence=session.confidence if session else None,
            )
        )

    total_value = portfolio.cash_balance + positions_value
    total_pnl = total_value - portfolio.starting_balance
    total_pnl_pct = (
        (total_pnl / portfolio.starting_balance) * 100
        if portfolio.starting_balance
        else 0.0
    )

    return PortfolioResponse(
        id=portfolio.id,
        starting_balance=portfolio.starting_balance,
        cash_balance=round(portfolio.cash_balance, 2),
        currency=portfolio.currency,
        total_value=round(total_value, 2),
        total_pnl=round(total_pnl, 2),
        total_pnl_pct=round(total_pnl_pct, 2),
        open_positions_count=len(enriched),
        open_positions=enriched,
    )


async def execute_trade(
    db: AsyncSession, request: TradeRequest
) -> TradeExecutionResponse:
    """Open a new position (paper trade)."""
    portfolio = await get_or_create_portfolio(db)

    current_price = _fetch_current_price(request.ticker, request.market_id)
    if current_price is None:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot fetch price for {request.ticker} in market {request.market_id}",
        )

    total_cost = current_price * request.quantity

    # Cash validation
    if request.direction == "long":
        if total_cost > portfolio.cash_balance:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient cash. Need ${total_cost:,.2f}, have ${portfolio.cash_balance:,.2f}",
            )
        portfolio.cash_balance -= total_cost
    else:
        # Short: require margin equal to position value
        if total_cost > portfolio.cash_balance:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient margin. Need ${total_cost:,.2f}, have ${portfolio.cash_balance:,.2f}",
            )
        portfolio.cash_balance -= total_cost

    position = Position(
        id=str(uuid4()),
        portfolio_id=portfolio.id,
        analysis_session_id=request.analysis_session_id,
        ticker=request.ticker.upper(),
        market_id=request.market_id,
        direction=request.direction,
        quantity=request.quantity,
        entry_price=current_price,
    )
    db.add(position)
    await db.flush()

    # Record equity snapshot
    await _record_snapshot(db, portfolio)

    return TradeExecutionResponse(
        position_id=position.id,
        ticker=position.ticker,
        direction=position.direction,
        quantity=position.quantity,
        entry_price=round(current_price, 4),
        total_cost=round(total_cost, 2),
        remaining_cash=round(portfolio.cash_balance, 2),
    )


async def close_position(
    db: AsyncSession, position_id: str
) -> ClosePositionResponse:
    """Close an open position at the current market price."""
    result = await db.execute(
        select(Position).where(Position.id == position_id)
    )
    position = result.scalar_one_or_none()
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")
    if position.status == "closed":
        raise HTTPException(status_code=400, detail="Position already closed")

    current_price = _fetch_current_price(position.ticker, position.market_id)
    if current_price is None:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot fetch exit price for {position.ticker}",
        )

    if position.direction == "long":
        realized_pnl = (current_price - position.entry_price) * position.quantity
    else:
        realized_pnl = (position.entry_price - current_price) * position.quantity

    realized_pnl_pct = (
        (realized_pnl / (position.entry_price * position.quantity)) * 100
        if position.entry_price
        else 0.0
    )

    position.exit_price = current_price
    position.exit_date = datetime.utcnow()
    position.status = "closed"
    position.realized_pnl = round(realized_pnl, 2)
    position.realized_pnl_pct = round(realized_pnl_pct, 2)

    # Return cash
    portfolio = await db.get(Portfolio, position.portfolio_id)
    if position.direction == "long":
        portfolio.cash_balance += current_price * position.quantity
    else:
        # Short close: return margin + pnl
        portfolio.cash_balance += (position.entry_price * position.quantity) + realized_pnl

    await db.flush()
    await _record_snapshot(db, portfolio)

    hold_days = _days_between(position.entry_date, position.exit_date)

    return ClosePositionResponse(
        position_id=position.id,
        ticker=position.ticker,
        direction=position.direction,
        entry_price=round(position.entry_price, 4),
        exit_price=round(current_price, 4),
        quantity=position.quantity,
        realized_pnl=round(realized_pnl, 2),
        realized_pnl_pct=round(realized_pnl_pct, 2),
        hold_days=hold_days,
        cash_balance=round(portfolio.cash_balance, 2),
    )


async def get_trade_history(
    db: AsyncSession,
    market: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> TradeHistoryResponse:
    """Query closed positions with optional market filter."""
    base = (
        select(Position)
        .where(Position.status == "closed")
        .options(selectinload(Position.analysis_session))
    )
    count_base = select(func.count()).select_from(Position).where(
        Position.status == "closed"
    )

    if market:
        base = base.where(Position.market_id == market)
        count_base = count_base.where(Position.market_id == market)

    total = (await db.execute(count_base)).scalar() or 0

    result = await db.execute(
        base.order_by(Position.exit_date.desc()).limit(limit).offset(offset)
    )
    positions = result.scalars().all()

    trades: list[TradeHistoryItem] = []
    for pos in positions:
        session = pos.analysis_session
        trades.append(
            TradeHistoryItem(
                id=pos.id,
                ticker=pos.ticker,
                market_id=pos.market_id,
                direction=pos.direction,
                quantity=pos.quantity,
                entry_price=pos.entry_price,
                exit_price=pos.exit_price,
                entry_date=pos.entry_date,
                exit_date=pos.exit_date,
                realized_pnl=pos.realized_pnl,
                realized_pnl_pct=pos.realized_pnl_pct,
                hold_days=_days_between(pos.entry_date, pos.exit_date),
                recommendation=session.recommendation if session else None,
                confidence=session.confidence if session else None,
            )
        )

    return TradeHistoryResponse(total=total, trades=trades)


async def get_analytics(db: AsyncSession) -> PortfolioAnalyticsResponse:
    """Compute analytics from all positions (closed + open with unrealized P&L)."""
    result = await db.execute(select(Position))
    all_positions = result.scalars().all()

    total_trades = len(all_positions)
    if total_trades == 0:
        return PortfolioAnalyticsResponse(
            total_trades=0,
            win_rate=0.0,
            avg_return_pct=0.0,
            total_realized_pnl=0.0,
        )

    # Compute P&L for each position
    pnl_data: list[tuple[Position, float, float]] = []  # (pos, pnl, pnl_pct)
    for p in all_positions:
        if p.status == "closed":
            pnl = p.realized_pnl or 0
            pnl_pct = p.realized_pnl_pct or 0
        else:
            current = _fetch_current_price(p.ticker, p.market_id)
            if current is None:
                current = p.entry_price
            if p.direction == "long":
                pnl = (current - p.entry_price) * p.quantity
            else:
                pnl = (p.entry_price - current) * p.quantity
            pnl_pct = (pnl / (p.entry_price * p.quantity)) * 100 if p.entry_price else 0
        pnl_data.append((p, round(pnl, 2), round(pnl_pct, 2)))

    wins = sum(1 for _, pnl, _ in pnl_data if pnl > 0)
    win_rate = round((wins / total_trades) * 100, 1)
    total_realized_pnl = sum(pnl for _, pnl, _ in pnl_data)
    avg_return_pct = round(sum(pct for _, _, pct in pnl_data) / total_trades, 2)

    # Best / worst
    best_item = max(pnl_data, key=lambda x: x[1])
    worst_item = min(pnl_data, key=lambda x: x[1])
    best_trade = TradeSummary(
        ticker=best_item[0].ticker,
        pnl=best_item[1],
        pnl_pct=best_item[2],
    )
    worst_trade = TradeSummary(
        ticker=worst_item[0].ticker,
        pnl=worst_item[1],
        pnl_pct=worst_item[2],
    )

    # By market
    by_market: dict[str, MarketBreakdown] = {}
    market_groups: dict[str, list[tuple[Position, float, float]]] = {}
    for item in pnl_data:
        market_groups.setdefault(item[0].market_id, []).append(item)
    for mid, group in market_groups.items():
        m_wins = sum(1 for _, pnl, _ in group if pnl > 0)
        by_market[mid] = MarketBreakdown(
            count=len(group),
            win_rate=round((m_wins / len(group)) * 100, 1),
            avg_return_pct=round(
                sum(pct for _, _, pct in group) / len(group), 2
            ),
        )

    # Equity curve from snapshots
    portfolio = await get_or_create_portfolio(db)
    snap_result = await db.execute(
        select(EquitySnapshot)
        .where(EquitySnapshot.portfolio_id == portfolio.id)
        .order_by(EquitySnapshot.date)
    )
    snapshots = snap_result.scalars().all()
    equity_curve = [
        EquityPointSchema(date=s.date.isoformat(), value=round(s.total_value, 2))
        for s in snapshots
    ]

    return PortfolioAnalyticsResponse(
        total_trades=total_trades,
        win_rate=win_rate,
        avg_return_pct=avg_return_pct,
        total_realized_pnl=round(total_realized_pnl, 2),
        best_trade=best_trade,
        worst_trade=worst_trade,
        by_market=by_market,
        equity_curve=equity_curve,
    )


async def get_ai_comparison(db: AsyncSession) -> AIComparisonResponse:
    """Compare trades that followed AI recommendations vs ignored ones.

    - **Followed**: Closed positions that have an ``analysis_session_id`` link.
    - **Ignored**: Completed AnalysisSessions that have no linked position but
      do have a SimulationResult (so we can infer what would have happened).
    """
    # Followed: all positions (open + closed) with an analysis session
    followed_result = await db.execute(
        select(Position).where(
            Position.analysis_session_id.isnot(None),
        )
    )
    followed_positions = followed_result.scalars().all()

    # Compute P&L for each position (realized for closed, unrealized for open)
    followed_count = len(followed_positions)
    followed_pnl = 0.0
    followed_returns: list[float] = []
    followed_wins = 0
    for p in followed_positions:
        if p.status == "closed":
            pnl = p.realized_pnl or 0
            pnl_pct = p.realized_pnl_pct or 0
        else:
            # Open position — compute unrealized P&L with live price
            current = _fetch_current_price(p.ticker, p.market_id)
            if current is None:
                current = p.entry_price
            if p.direction == "long":
                pnl = (current - p.entry_price) * p.quantity
            else:
                pnl = (p.entry_price - current) * p.quantity
            pnl_pct = (pnl / (p.entry_price * p.quantity)) * 100 if p.entry_price else 0
        followed_pnl += pnl
        followed_returns.append(pnl_pct)
        if pnl > 0:
            followed_wins += 1

    followed_avg = (
        round(sum(followed_returns) / followed_count, 2) if followed_count else 0.0
    )
    followed_wr = (
        round((followed_wins / followed_count) * 100, 1) if followed_count else 0.0
    )

    # Ignored: completed sessions without a linked position, but with simulation
    linked_session_ids_q = select(Position.analysis_session_id).where(
        Position.analysis_session_id.isnot(None)
    )
    linked_ids_result = await db.execute(linked_session_ids_q)
    linked_ids = {row[0] for row in linked_ids_result.all()}

    ignored_result = await db.execute(
        select(SimulationResult)
        .join(AnalysisSession, SimulationResult.session_id == AnalysisSession.id)
        .where(
            AnalysisSession.status == "completed",
            SimulationResult.session_id.notin_(linked_ids) if linked_ids else True,
        )
    )
    ignored_sims = ignored_result.scalars().all()

    ignored_count = len(ignored_sims)
    ignored_returns = [s.return_pct for s in ignored_sims]
    ignored_pnl = sum(ignored_returns)
    ignored_wins = sum(1 for s in ignored_sims if s.is_win)

    ignored_avg = (
        round(sum(ignored_returns) / ignored_count, 2) if ignored_count else 0.0
    )
    ignored_wr = (
        round((ignored_wins / ignored_count) * 100, 1) if ignored_count else 0.0
    )

    return_advantage = round(followed_avg - ignored_avg, 2)
    wr_advantage = round(followed_wr - ignored_wr, 1)

    if return_advantage > 0:
        message = f"Following AI recommendations yielded {return_advantage}% higher average return."
    elif return_advantage < 0:
        message = f"Ignoring AI recommendations would have yielded {abs(return_advantage)}% higher average return."
    else:
        message = "Following and ignoring AI recommendations produced similar returns."

    return AIComparisonResponse(
        followed=AIComparisonSide(
            count=followed_count,
            avg_return_pct=followed_avg,
            win_rate=followed_wr,
            total_pnl=round(followed_pnl, 2),
        ),
        ignored=AIComparisonSide(
            count=ignored_count,
            avg_return_pct=ignored_avg,
            win_rate=ignored_wr,
            total_pnl=round(ignored_pnl, 2),
        ),
        difference={
            "return_advantage_pct": return_advantage,
            "win_rate_advantage": wr_advantage,
            "message": message,
        },
    )


async def reset_portfolio(db: AsyncSession) -> dict:
    """Delete all positions & snapshots and reset the portfolio to defaults."""
    portfolio = await get_or_create_portfolio(db)

    await db.execute(
        delete(EquitySnapshot).where(EquitySnapshot.portfolio_id == portfolio.id)
    )
    await db.execute(
        delete(Position).where(Position.portfolio_id == portfolio.id)
    )

    portfolio.cash_balance = portfolio.starting_balance
    portfolio.reset_at = datetime.utcnow()
    await db.flush()

    return {
        "status": "ok",
        "message": "Portfolio reset to starting balance",
        "cash_balance": portfolio.cash_balance,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _record_snapshot(db: AsyncSession, portfolio: Portfolio) -> None:
    """Persist an equity snapshot for the current date."""
    # Compute positions value (use entry_price as quick estimate to avoid
    # extra yfinance calls during write path).
    result = await db.execute(
        select(Position).where(
            Position.portfolio_id == portfolio.id, Position.status == "open"
        )
    )
    open_positions = result.scalars().all()
    positions_value = sum(p.entry_price * p.quantity for p in open_positions)

    total_value = portfolio.cash_balance + positions_value
    today = date_type.today()

    snapshot = EquitySnapshot(
        id=str(uuid4()),
        portfolio_id=portfolio.id,
        date=today,
        total_value=round(total_value, 2),
        cash_balance=round(portfolio.cash_balance, 2),
        positions_value=round(positions_value, 2),
    )
    db.add(snapshot)
    await db.flush()
