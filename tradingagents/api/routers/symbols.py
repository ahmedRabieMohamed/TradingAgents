"""Symbol discovery endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, Request, status

from tradingagents.api.deps.auth import optional_current_account
from tradingagents.api.deps.errors import ApiError
from tradingagents.api.deps import rate_limit
from tradingagents.api.schemas.symbols import SymbolListResponse
from tradingagents.api.services import symbols as symbols_service


_SUPPORTED_MARKETS = {"US", "EGX"}

router = APIRouter(prefix="/symbols", tags=["symbols"])


def _validate_market(market_id: str) -> str:
    market_key = market_id.upper()
    if market_key not in _SUPPORTED_MARKETS:
        raise ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="MARKET_NOT_FOUND",
            message="Market not found",
        )
    return market_key


@router.get("/search", response_model=SymbolListResponse)
async def search_symbols(
    request: Request,
    market_id: str = Query(...),
    q: str = Query(..., min_length=1),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: Optional[dict[str, Optional[str]]] = Depends(optional_current_account),
) -> SymbolListResponse:
    _validate_market(market_id)
    await rate_limit.enforce_rate_limits(
        request, is_authenticated=bool(getattr(request.state, "account_id", None))
    )
    items, total, next_offset = symbols_service.search_symbols(
        market_id, q, limit=limit, offset=offset
    )
    return SymbolListResponse(count=total, items=items, next_offset=next_offset)


@router.get("", response_model=SymbolListResponse)
async def filter_symbols(
    request: Request,
    market_id: str = Query(...),
    sector: Optional[str] = Query(None),
    market_cap_min: Optional[float] = Query(None, ge=0),
    market_cap_max: Optional[float] = Query(None, ge=0),
    sort: Optional[str] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: Optional[dict[str, Optional[str]]] = Depends(optional_current_account),
) -> SymbolListResponse:
    _validate_market(market_id)
    await rate_limit.enforce_rate_limits(
        request, is_authenticated=bool(getattr(request.state, "account_id", None))
    )
    items, total, next_offset = symbols_service.filter_symbols(
        market_id,
        sector=sector,
        market_cap_min=market_cap_min,
        market_cap_max=market_cap_max,
        sort=sort,
        limit=limit,
        offset=offset,
    )
    return SymbolListResponse(count=total, items=items, next_offset=next_offset)


@router.get("/most-active", response_model=SymbolListResponse)
async def most_active_symbols(
    request: Request,
    market_id: str = Query(...),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    window: str = Query("1w"),
    _: Optional[dict[str, Optional[str]]] = Depends(optional_current_account),
) -> SymbolListResponse:
    _validate_market(market_id)
    await rate_limit.enforce_rate_limits(
        request, is_authenticated=bool(getattr(request.state, "account_id", None))
    )
    items, total, next_offset, meta = symbols_service.get_most_active(
        market_id, limit=limit, offset=offset, window=window
    )
    return SymbolListResponse(
        count=total, items=items, next_offset=next_offset, meta=meta
    )


@router.get("/trending", response_model=SymbolListResponse)
async def trending_symbols(
    request: Request,
    market_id: str = Query(...),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    window: str = Query("1w"),
    _: Optional[dict[str, Optional[str]]] = Depends(optional_current_account),
) -> SymbolListResponse:
    _validate_market(market_id)
    await rate_limit.enforce_rate_limits(
        request, is_authenticated=bool(getattr(request.state, "account_id", None))
    )
    items, total, next_offset, meta = symbols_service.get_trending(
        market_id, limit=limit, offset=offset, window=window
    )
    return SymbolListResponse(
        count=total, items=items, next_offset=next_offset, meta=meta
    )
