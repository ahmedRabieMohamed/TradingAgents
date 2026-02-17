"""Historical data endpoints."""

from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request, status

from tradingagents.api.deps import rate_limit
from tradingagents.api.deps.auth import optional_current_account
from tradingagents.api.deps.errors import ApiError
from tradingagents.api.schemas.historical import (
    CorporateActionsResponse,
    DailyHistoryResponse,
    IntradayHistoryResponse,
)
from tradingagents.api.services import historical as historical_service

_SUPPORTED_MARKETS = {"US", "EGX"}
_SUPPORTED_INTRADAY_RANGES = {"1D", "1W", "1M", "1Y"}

router = APIRouter(prefix="/historical", tags=["historical"])


def _validate_market(market_id: str) -> str:
    market_key = market_id.upper()
    if market_key not in _SUPPORTED_MARKETS:
        raise ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="MARKET_NOT_FOUND",
            message="Market not found",
        )
    return market_key


def _validate_intraday_range(range_key: str) -> str:
    range_value = range_key.upper()
    if range_value not in _SUPPORTED_INTRADAY_RANGES:
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INTRADAY_RANGE_INVALID",
            message="Intraday range must be one of 1D, 1W, 1M, 1Y",
        )
    return range_value


@router.get("/daily", response_model=DailyHistoryResponse)
async def get_daily_history(
    request: Request,
    market_id: str = Query(...),
    symbol: str = Query(..., min_length=1),
    start_date: date = Query(...),
    end_date: date = Query(...),
) -> DailyHistoryResponse:
    market_key = _validate_market(market_id)
    await rate_limit.enforce_rate_limits(request, is_authenticated=False)
    return historical_service.get_daily_history(
        market_key, symbol, start_date, end_date
    )


@router.get("/intraday", response_model=IntradayHistoryResponse)
async def get_intraday_history(
    request: Request,
    market_id: str = Query(...),
    symbol: str = Query(..., min_length=1),
    range: str = Query(..., alias="range"),
    _: Optional[dict[str, Optional[str]]] = Depends(optional_current_account),
) -> IntradayHistoryResponse:
    market_key = _validate_market(market_id)
    range_value = _validate_intraday_range(range)
    is_authenticated = bool(getattr(request.state, "account_id", None))
    await rate_limit.enforce_rate_limits(request, is_authenticated=is_authenticated)
    return historical_service.get_intraday_history(
        market_key, symbol, range_value, is_authenticated=is_authenticated
    )


@router.get("/actions", response_model=CorporateActionsResponse)
async def get_corporate_actions(
    request: Request,
    market_id: str = Query(...),
    symbol: str = Query(..., min_length=1),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
) -> CorporateActionsResponse:
    market_key = _validate_market(market_id)
    await rate_limit.enforce_rate_limits(request, is_authenticated=False)
    return historical_service.get_corporate_actions(
        market_key, symbol, start_date, end_date
    )
