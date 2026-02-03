"""FastAPI application setup and lifecycle management."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

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

app.include_router(api_router, prefix=settings.api_prefix)
