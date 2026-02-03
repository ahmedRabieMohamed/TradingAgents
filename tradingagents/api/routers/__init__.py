"""API routers for versioned endpoints."""

from fastapi import APIRouter

from tradingagents.api.routers.auth import router as auth_router
from tradingagents.api.routers.markets import router as markets_router
from tradingagents.api.routers.symbols import router as symbols_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(markets_router)
api_router.include_router(symbols_router)

__all__ = ["api_router"]
