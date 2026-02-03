"""API routers for versioned endpoints."""

from fastapi import APIRouter

from tradingagents.api.routers.auth import router as auth_router

api_router = APIRouter()
api_router.include_router(auth_router)

__all__ = ["api_router"]
