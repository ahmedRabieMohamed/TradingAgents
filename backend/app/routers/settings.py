"""Settings router for user preferences and API key management."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.schemas import UserSettingsResponse, SettingsUpdateRequest
from app.services.settings import get_all_settings, update_settings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=UserSettingsResponse)
async def get_settings(db: AsyncSession = Depends(get_db)):
    """Get all user settings."""
    data = await get_all_settings(db)
    return UserSettingsResponse(**data)


@router.patch("", response_model=UserSettingsResponse)
async def patch_settings(
    body: SettingsUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update user settings."""
    updates = body.model_dump(exclude_none=True)
    data = await update_settings(db, updates)
    return UserSettingsResponse(**data)
