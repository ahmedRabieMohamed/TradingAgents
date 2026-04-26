"""FastAPI application entry point for TradingAgents API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import (
    markets,
    stocks,
    analysis,
    performance,
    settings as settings_router,
    llm_providers,
    market_overview,
    portfolio,
    watchlist,
    engines,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize DB on startup."""
    await init_db()
    yield


app = FastAPI(
    title="TradingAgents API",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(markets.router, prefix="/api")
app.include_router(stocks.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(performance.router, prefix="/api")
app.include_router(settings_router.router, prefix="/api")
app.include_router(llm_providers.router, prefix="/api")
app.include_router(market_overview.router, prefix="/api")
app.include_router(portfolio.router, prefix="/api")
app.include_router(watchlist.router, prefix="/api")
app.include_router(engines.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
