"""FastAPI application setup and lifecycle management."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from tradingagents.api.deps.errors import (
    ApiError,
    api_error_handler,
    http_exception_handler,
    limiter_exception_class,
    rate_limit_exception_handler,
    validation_exception_handler,
)
from tradingagents.api.deps.rate_limit import limiter_identifier
from tradingagents.api.routers import api_router
from tradingagents.api.settings import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    from fastapi_limiter import FastAPILimiter
    import redis.asyncio as redis

    if not settings.redis_url:
        raise RuntimeError("REDIS_URL is required to initialize rate limiting.")

    redis_client = redis.from_url(
        settings.redis_url, encoding="utf-8", decode_responses=True
    )
    await FastAPILimiter.init(redis_client, identifier=limiter_identifier)
    yield
    await FastAPILimiter.close()


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan,
)

app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
limiter_exception = limiter_exception_class()
if limiter_exception is not None:
    app.add_exception_handler(limiter_exception, rate_limit_exception_handler)

app.include_router(api_router, prefix=settings.api_prefix)
