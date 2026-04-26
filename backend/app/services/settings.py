"""Settings service for reading and writing user preferences and API keys."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import UserSettings

# Known API key names and their DB key prefixes
API_KEY_NAMES = [
    "openai",
    "anthropic",
    "google",
    "xai",
    "openrouter",
    "serper",
    "alpha_vantage",
]

# Default setting values
DEFAULTS = {
    "default_market": "us",
    "default_horizon": "short-term",
    "default_depth": "medium",
    "default_llm_provider": "openai",
}


async def get_all_settings(db: AsyncSession) -> dict:
    """Get all settings as a structured dict."""
    result = await db.execute(select(UserSettings))
    rows = {row.key: row.value for row in result.scalars().all()}

    # Build API keys presence map
    api_keys = {}
    for key_name in API_KEY_NAMES:
        db_key = f"api_key_{key_name}"
        raw = rows.get(db_key, "")
        api_keys[key_name] = bool(raw and raw.strip())

    return {
        "default_market": rows.get("default_market", DEFAULTS["default_market"]),
        "default_horizon": rows.get("default_horizon", DEFAULTS["default_horizon"]),
        "default_depth": rows.get("default_depth", DEFAULTS["default_depth"]),
        "default_llm_provider": rows.get(
            "default_llm_provider", DEFAULTS["default_llm_provider"]
        ),
        "api_keys": api_keys,
    }


async def get_setting(db: AsyncSession, key: str) -> str | None:
    """Get a single setting value by key."""
    result = await db.execute(
        select(UserSettings).where(UserSettings.key == key)
    )
    row = result.scalar_one_or_none()
    return row.value if row else None


async def update_settings(db: AsyncSession, updates: dict) -> dict:
    """Update settings from a dict. Returns the full settings after update.

    Accepts keys: default_market, default_horizon, default_depth,
    default_llm_provider, api_keys (dict of provider_name -> key_value).
    """
    # Handle simple string settings
    for field in ("default_market", "default_horizon", "default_depth", "default_llm_provider"):
        if field in updates and updates[field] is not None:
            await _upsert_setting(db, field, updates[field])

    # Handle API keys
    api_keys = updates.get("api_keys")
    if api_keys and isinstance(api_keys, dict):
        for key_name, key_value in api_keys.items():
            if key_name in API_KEY_NAMES:
                db_key = f"api_key_{key_name}"
                await _upsert_setting(db, db_key, key_value)

    await db.flush()
    return await get_all_settings(db)


async def _upsert_setting(db: AsyncSession, key: str, value: str) -> None:
    """Insert or update a single setting."""
    result = await db.execute(
        select(UserSettings).where(UserSettings.key == key)
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.value = value
    else:
        db.add(UserSettings(key=key, value=value))
