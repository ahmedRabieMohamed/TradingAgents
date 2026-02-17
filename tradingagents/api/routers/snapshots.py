"""Snapshot quote endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, Request, status

from tradingagents.api.deps import rate_limit
from tradingagents.api.deps.auth import optional_current_account
from tradingagents.api.deps.errors import ApiError
from tradingagents.api.schemas.snapshots import SnapshotResponse
from tradingagents.api.services import snapshots as snapshots_service


_SUPPORTED_MARKETS = {"US", "EGX"}

router = APIRouter(prefix="/snapshots", tags=["snapshots"])


def _validate_market(market_id: str) -> str:
    market_key = market_id.upper()
    if market_key not in _SUPPORTED_MARKETS:
        raise ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="MARKET_NOT_FOUND",
            message="Market not found",
        )
    return market_key


@router.get("", response_model=SnapshotResponse)
async def get_snapshot(
    request: Request,
    market_id: str = Query(...),
    symbol: str = Query(..., min_length=1),
    _: Optional[dict[str, Optional[str]]] = Depends(optional_current_account),
) -> SnapshotResponse:
    market_key = _validate_market(market_id)
    is_authenticated = bool(getattr(request.state, "account_id", None))
    await rate_limit.enforce_rate_limits(request, is_authenticated=is_authenticated)
    return snapshots_service.get_snapshot(
        market_key, symbol, is_authenticated=is_authenticated
    )
