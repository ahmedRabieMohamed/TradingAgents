"""JWT creation and verification helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt
from fastapi import status
from jwt import ExpiredSignatureError, InvalidTokenError

from tradingagents.api.deps.errors import ApiError
from tradingagents.api.settings import settings


def _jwt_secret() -> str:
    if settings.app_env != "dev" and settings.jwt_secret == "dev-jwt-secret":
        raise ApiError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="AUTH_CONFIG_ERROR",
            message="JWT secret is not configured",
        )
    return settings.jwt_secret


def create_access_token(claims: dict[str, Any]) -> str:
    payload = claims.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_ttl_minutes
    )
    payload.update({"exp": expire, "type": payload.get("type", "access")})
    return jwt.encode(payload, _jwt_secret(), algorithm=settings.jwt_algorithm)


def create_refresh_token(claims: dict[str, Any]) -> str:
    payload = claims.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_ttl_days
    )
    payload.update(
        {"exp": expire, "type": payload.get("type", "refresh"), "jti": str(uuid4())}
    )
    return jwt.encode(payload, _jwt_secret(), algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            _jwt_secret(),
            algorithms=[settings.jwt_algorithm],
        )
    except (ExpiredSignatureError, InvalidTokenError) as exc:
        raise ApiError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTH_INVALID",
            message="Token is invalid or expired",
        ) from exc
    return payload
