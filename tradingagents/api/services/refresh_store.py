"""Redis-backed refresh token rotation."""

from __future__ import annotations

import json
from typing import Any

from fastapi import status
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

import redis.asyncio as redis

from tradingagents.api.deps.errors import ApiError
from tradingagents.api.services.auth_tokens import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from tradingagents.api.settings import settings


_PASSWORD_HASH = PasswordHash((Argon2Hasher(),))
_REDIS_CLIENT: redis.Redis | None = None


def _refresh_salt() -> str:
    if settings.refresh_token_salt:
        return settings.refresh_token_salt
    if settings.app_env == "dev":
        return "dev-refresh-salt"
    raise ApiError(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="AUTH_CONFIG_ERROR",
        message="REFRESH_TOKEN_SALT is not configured",
    )


def _get_redis() -> redis.Redis:
    global _REDIS_CLIENT
    if _REDIS_CLIENT is not None:
        return _REDIS_CLIENT
    if not settings.redis_url:
        raise ApiError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="REDIS_NOT_CONFIGURED",
            message="Redis is required for refresh token storage",
        )
    _REDIS_CLIENT = redis.from_url(
        settings.redis_url, encoding="utf-8", decode_responses=True
    )
    return _REDIS_CLIENT


def _hash_refresh_token(token: str) -> str:
    salted = f"{token}{_refresh_salt()}"
    return _PASSWORD_HASH.hash(salted)


def _verify_refresh_token(token: str, stored_hash: str) -> bool:
    salted = f"{token}{_refresh_salt()}"
    return _PASSWORD_HASH.verify(salted, stored_hash)


async def store_refresh_token(token: str, account_id: str, client_id: str) -> str:
    payload = decode_token(token)
    jti = payload.get("jti")
    if not jti:
        raise ApiError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTH_INVALID",
            message="Refresh token missing jti",
        )
    ttl_seconds = int(settings.refresh_token_ttl_days * 24 * 60 * 60)
    record = json.dumps(
        {
            "hash": _hash_refresh_token(token),
            "account_id": account_id,
            "client_id": client_id,
        }
    )
    redis_client = _get_redis()
    await redis_client.setex(jti, ttl_seconds, record)
    return jti


async def verify_and_rotate(refresh_token: str) -> dict[str, Any]:
    payload = decode_token(refresh_token)
    jti = payload.get("jti")
    if not jti:
        raise ApiError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTH_INVALID",
            message="Refresh token missing jti",
        )
    redis_client = _get_redis()
    stored = await redis_client.get(jti)
    if not stored:
        raise ApiError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTH_INVALID",
            message="Refresh token is invalid",
        )
    record = json.loads(stored)
    stored_hash = record.get("hash")
    if not stored_hash or not _verify_refresh_token(refresh_token, stored_hash):
        await redis_client.delete(jti)
        raise ApiError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTH_INVALID",
            message="Refresh token is invalid",
        )
    await redis_client.delete(jti)
    account_id = record.get("account_id") or payload.get("sub")
    client_id = record.get("client_id") or payload.get("client_id")
    if not account_id or not client_id:
        raise ApiError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTH_INVALID",
            message="Refresh token is missing claims",
        )
    access_token = create_access_token(
        {"sub": account_id, "client_id": client_id, "type": "access"}
    )
    new_refresh_token = create_refresh_token(
        {"sub": account_id, "client_id": client_id, "type": "refresh"}
    )
    await store_refresh_token(new_refresh_token, account_id, client_id)
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "account_id": account_id,
        "client_id": client_id,
    }
