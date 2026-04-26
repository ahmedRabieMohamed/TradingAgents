"""Portfolio router: paper-trading endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.schemas import (
    AIComparisonResponse,
    ClosePositionResponse,
    PortfolioAnalyticsResponse,
    PortfolioResponse,
    TradeExecutionResponse,
    TradeHistoryResponse,
    TradeRequest,
)
from app.services import portfolio as portfolio_svc

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("", response_model=PortfolioResponse)
async def get_portfolio(db: AsyncSession = Depends(get_db)):
    """Return the portfolio with enriched open positions."""
    return await portfolio_svc.get_portfolio_with_positions(db)


@router.post("/trade", response_model=TradeExecutionResponse)
async def execute_trade(
    request: TradeRequest,
    db: AsyncSession = Depends(get_db),
):
    """Open a new paper-trade position."""
    return await portfolio_svc.execute_trade(db, request)


@router.post(
    "/positions/{position_id}/close", response_model=ClosePositionResponse
)
async def close_position(
    position_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Close an open position at the current market price."""
    return await portfolio_svc.close_position(db, position_id)


@router.get("/trades", response_model=TradeHistoryResponse)
async def get_trade_history(
    market: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Return closed trades with optional market filter."""
    return await portfolio_svc.get_trade_history(db, market=market, limit=limit, offset=offset)


@router.get("/analytics", response_model=PortfolioAnalyticsResponse)
async def get_analytics(db: AsyncSession = Depends(get_db)):
    """Return portfolio analytics and equity curve."""
    return await portfolio_svc.get_analytics(db)


@router.get("/ai-comparison", response_model=AIComparisonResponse)
async def get_ai_comparison(db: AsyncSession = Depends(get_db)):
    """Compare trades that followed AI vs ignored recommendations."""
    return await portfolio_svc.get_ai_comparison(db)


@router.post("/reset")
async def reset_portfolio(db: AsyncSession = Depends(get_db)):
    """Reset portfolio to starting balance, delete all positions."""
    return await portfolio_svc.reset_portfolio(db)
