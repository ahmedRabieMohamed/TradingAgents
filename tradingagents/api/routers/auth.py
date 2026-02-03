"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from tradingagents.api.deps.errors import ApiError
from tradingagents.api.deps.rate_limit import (
    anon_per_day_limiter,
    anon_per_minute_limiter,
)
from tradingagents.api.schemas.auth import RefreshRequest, TokenRequest, TokenResponse
from tradingagents.api.services.auth_tokens import (
    create_access_token,
    create_refresh_token,
)
from tradingagents.api.services.client_registry import get_client, verify_client_secret
from tradingagents.api.services.refresh_store import (
    store_refresh_token,
    verify_and_rotate,
)
from tradingagents.api.settings import settings


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/token",
    response_model=TokenResponse,
    dependencies=[Depends(anon_per_minute_limiter), Depends(anon_per_day_limiter)],
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
    refresh_token = create_refresh_token(
        {"sub": client.account_id, "client_id": client.client_id, "type": "refresh"}
    )
    await store_refresh_token(refresh_token, client.account_id, client.client_id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_ttl_minutes * 60,
        refresh_expires_in=settings.refresh_token_ttl_days * 24 * 60 * 60,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    dependencies=[Depends(anon_per_minute_limiter), Depends(anon_per_day_limiter)],
)
async def refresh_token(payload: RefreshRequest) -> TokenResponse:
    rotated = await verify_and_rotate(payload.refresh_token)
    return TokenResponse(
        access_token=rotated["access_token"],
        refresh_token=rotated["refresh_token"],
        expires_in=settings.access_token_ttl_minutes * 60,
        refresh_expires_in=settings.refresh_token_ttl_days * 24 * 60 * 60,
    )
