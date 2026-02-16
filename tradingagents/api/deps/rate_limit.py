"""Rate limit dependency helpers."""

import logging

from typing import Iterable, Optional

from fastapi import Request, Response

try:
    from fastapi_limiter import FastAPILimiter
    from fastapi_limiter.depends import RateLimiter
    import redis.asyncio as redis
except ImportError:  # pragma: no cover - fastapi-limiter optional at import time
    FastAPILimiter = None
    redis = None

    class RateLimiter:  # type: ignore[no-redef]
        def __init__(self, *_: object, **__: object) -> None:
            pass

        async def __call__(self, *_: object, **__: object) -> None:
            raise RuntimeError("fastapi-limiter is required for rate limiting.")


from tradingagents.api.settings import settings

_limiter_disabled_logged = False


def _log_limiter_disabled(message: str) -> None:
    global _limiter_disabled_logged
    if _limiter_disabled_logged:
        return
    _limiter_disabled_logged = True
    logging.getLogger(__name__).warning(message)


async def limiter_identifier(request: Request) -> Optional[str]:
    limiter_id = getattr(request.state, "limiter_id", None)
    if limiter_id:
        return str(limiter_id)
    if request.client:
        return request.client.host
    return "unknown"


auth_per_minute_limiter = RateLimiter(times=settings.auth_per_minute, seconds=60)
auth_per_day_limiter = RateLimiter(times=settings.auth_per_day, seconds=60 * 60 * 24)
anon_per_minute_limiter = RateLimiter(times=settings.anon_per_minute, seconds=60)
anon_per_day_limiter = RateLimiter(times=settings.anon_per_day, seconds=60 * 60 * 24)


async def _apply_limiters(limiters: Iterable[RateLimiter], request: Request) -> None:
    response = Response()
    for limiter in limiters:
        await limiter(request, response)


async def _ensure_limiter_initialized() -> bool:
    if FastAPILimiter is None or redis is None:
        _log_limiter_disabled(
            "Rate limiting disabled because fastapi-limiter is not installed."
        )
        return False
    if FastAPILimiter.redis is not None:
        return True
    if not settings.redis_url:
        if settings.app_env == "dev":
            _log_limiter_disabled(
                "Rate limiting disabled because REDIS_URL is not set."
            )
            return False
        raise RuntimeError("REDIS_URL is required to initialize rate limiting.")
    redis_client = redis.from_url(
        settings.redis_url, encoding="utf-8", decode_responses=True
    )
    await FastAPILimiter.init(redis_client, identifier=limiter_identifier)
    return True


async def enforce_rate_limits(request: Request, is_authenticated: bool) -> None:
    if not await _ensure_limiter_initialized():
        return
    if is_authenticated:
        await _apply_limiters([auth_per_minute_limiter, auth_per_day_limiter], request)
        return
    await _apply_limiters([anon_per_minute_limiter, anon_per_day_limiter], request)


async def optional_anon_per_minute_limiter(
    request: Request, response: Response
) -> None:
    if not await _ensure_limiter_initialized():
        return
    await anon_per_minute_limiter(request, response)


async def optional_anon_per_day_limiter(request: Request, response: Response) -> None:
    if not await _ensure_limiter_initialized():
        return
    await anon_per_day_limiter(request, response)


async def optional_auth_per_minute_limiter(
    request: Request, response: Response
) -> None:
    if not await _ensure_limiter_initialized():
        return
    await auth_per_minute_limiter(request, response)


async def optional_auth_per_day_limiter(request: Request, response: Response) -> None:
    if not await _ensure_limiter_initialized():
        return
    await auth_per_day_limiter(request, response)
