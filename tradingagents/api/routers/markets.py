"""Market discovery endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Request, status

from tradingagents.api.deps.auth import optional_current_account
from tradingagents.api.deps.errors import ApiError
from tradingagents.api.deps import rate_limit
from tradingagents.api.schemas.markets import MarketListResponse, MarketResponse
from tradingagents.api.services import market_registry


router = APIRouter(prefix="/markets", tags=["markets"])


@router.get("", response_model=MarketListResponse)
async def list_markets_endpoint(
    request: Request,
    _: Optional[dict] = Depends(optional_current_account),
) -> MarketListResponse:
    account_id = getattr(request.state, "account_id", None)
    await rate_limit.enforce_rate_limits(request, is_authenticated=bool(account_id))
    markets = market_registry.list_markets()
    return MarketListResponse(count=len(markets), items=markets)


@router.get("/{market_id}", response_model=MarketResponse)
async def get_market_endpoint(
    market_id: str,
    request: Request,
    _: Optional[dict] = Depends(optional_current_account),
) -> MarketResponse:
    account_id = getattr(request.state, "account_id", None)
    await rate_limit.enforce_rate_limits(request, is_authenticated=bool(account_id))
    market = market_registry.get_market(market_id)
    if not market:
        raise ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="MARKET_NOT_FOUND",
            message="Market not found",
        )
    return MarketResponse(**market)
