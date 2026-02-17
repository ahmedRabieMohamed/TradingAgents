"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from tradingagents.api.deps.errors import ApiError
from tradingagents.api.deps.rate_limit import (
    optional_anon_per_day_limiter,
    optional_anon_per_minute_limiter,
)
from tradingagents.api.schemas.auth import TokenRequest, TokenResponse
from tradingagents.api.services.auth_tokens import create_access_token
from tradingagents.api.services.client_registry import get_client, verify_client_secret
from tradingagents.api.settings import settings


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/token",
    response_model=TokenResponse,
    dependencies=[
        Depends(optional_anon_per_minute_limiter),
        Depends(optional_anon_per_day_limiter),
    ],
)
async def issue_token(payload: TokenRequest) -> TokenResponse:
    client = get_client(payload.client_id)
    if not client or not verify_client_secret(client, payload.client_secret):
        raise ApiError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTH_INVALID",
            message="Invalid client credentials",
        )
    access_token = create_access_token(
        {"sub": client.account_id, "client_id": client.client_id, "type": "access"}
    )
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.access_token_ttl_minutes * 60,
    )
