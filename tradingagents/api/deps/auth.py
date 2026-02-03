"""Auth dependencies for authenticated and optional contexts."""

from __future__ import annotations

from typing import Optional

from fastapi import Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from tradingagents.api.deps.errors import ApiError
from tradingagents.api.services.auth_tokens import decode_token


_bearer_required = HTTPBearer()
_bearer_optional = HTTPBearer(auto_error=False)


def _apply_request_state(request: Request, payload: dict) -> dict[str, Optional[str]]:
    account_id = payload.get("sub")
    client_id = payload.get("client_id")
    if not account_id:
        raise ApiError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTH_INVALID",
            message="Token is missing subject",
        )
    request.state.account_id = account_id
    request.state.client_id = client_id
    request.state.limiter_id = account_id
    return {"account_id": account_id, "client_id": client_id}


async def get_current_account(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_required),
) -> dict[str, Optional[str]]:
    if credentials.scheme.lower() != "bearer":
        raise ApiError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTH_INVALID",
            message="Authorization scheme must be Bearer",
        )
    payload = decode_token(credentials.credentials)
    return _apply_request_state(request, payload)


async def optional_current_account(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_optional),
) -> Optional[dict[str, Optional[str]]]:
    if credentials is None:
        return None
    if credentials.scheme.lower() != "bearer":
        raise ApiError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTH_INVALID",
            message="Authorization scheme must be Bearer",
        )
    payload = decode_token(credentials.credentials)
    return _apply_request_state(request, payload)
