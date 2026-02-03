"""Rate limit dependency helpers."""

from typing import Iterable, Optional

from fastapi import Request, Response

try:
    from fastapi_limiter.depends import RateLimiter
except ImportError:  # pragma: no cover - fastapi-limiter optional at import time

    class RateLimiter:  # type: ignore[no-redef]
        def __init__(self, *_: object, **__: object) -> None:
            pass

        async def __call__(self, *_: object, **__: object) -> None:
            raise RuntimeError("fastapi-limiter is required for rate limiting.")


from tradingagents.api.settings import settings


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


async def enforce_rate_limits(request: Request, is_authenticated: bool) -> None:
    if is_authenticated:
        await _apply_limiters([auth_per_minute_limiter, auth_per_day_limiter], request)
        return
    await _apply_limiters([anon_per_minute_limiter, anon_per_day_limiter], request)
