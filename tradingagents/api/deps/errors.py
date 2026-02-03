"""API error types and exception handlers."""

from typing import Any, Optional

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from tradingagents.api.schemas.errors import ErrorDetail, ErrorResponse

try:
    from fastapi_limiter.exceptions import RateLimitExceeded
except ImportError:  # pragma: no cover - fastapi-limiter optional at import time
    RateLimitExceeded = None


class ApiError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


def _get_request_id(request: Request) -> Optional[str]:
    return request.headers.get("x-request-id")


def _error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: Optional[Any],
    request_id: Optional[str],
) -> JSONResponse:
    payload = ErrorResponse(
        error=ErrorDetail(code=code, message=message, details=details),
        request_id=request_id,
    )
    content = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    return JSONResponse(status_code=status_code, content=content)


async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    return _error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        details=exc.details,
        request_id=_get_request_id(request),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    code_map = {
        status.HTTP_401_UNAUTHORIZED: "AUTH_REQUIRED",
        status.HTTP_403_FORBIDDEN: "AUTH_INVALID",
        status.HTTP_404_NOT_FOUND: "NOT_FOUND",
        status.HTTP_429_TOO_MANY_REQUESTS: "RATE_LIMIT_EXCEEDED",
    }
    code = code_map.get(exc.status_code, "INTERNAL_ERROR")
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return _error_response(
        status_code=exc.status_code,
        code=code,
        message=message,
        details=None,
        request_id=_get_request_id(request),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return _error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="VALIDATION_ERROR",
        message="Validation failed",
        details=exc.errors(),
        request_id=_get_request_id(request),
    )


async def rate_limit_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    return _error_response(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        code="RATE_LIMIT_EXCEEDED",
        message="Rate limit exceeded",
        details=None,
        request_id=_get_request_id(request),
    )


def limiter_exception_class() -> Optional[type[BaseException]]:
    return RateLimitExceeded
