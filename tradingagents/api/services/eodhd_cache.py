"""EODHD response caching helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from tradingagents.api.settings import settings


def ensure_cache_dir(cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _cache_path(cache_key: str) -> Path:
    safe_key = cache_key.replace("/", "_").replace(":", "_")
    cache_dir = ensure_cache_dir(Path(settings.eodhd_cache_dir))
    return cache_dir / f"{safe_key}.json"


def _parse_iso_datetime(timestamp: str) -> Optional[datetime]:
    if not timestamp:
        return None
    cleaned = timestamp.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        return None


def load_cached_payload(cache_key: str, ttl_seconds: int) -> Optional[Any]:
    cache_file = _cache_path(cache_key)
    if not cache_file.exists():
        return None

    try:
        payload = json.loads(cache_file.read_text())
    except json.JSONDecodeError:
        return None

    fetched_at = _parse_iso_datetime(payload.get("fetched_at"))
    if fetched_at is None:
        return None

    age_seconds = (datetime.now(timezone.utc) - fetched_at).total_seconds()
    if age_seconds > ttl_seconds:
        return None

    return payload.get("data")


def save_cached_payload(cache_key: str, data: Any) -> None:
    cache_file = _cache_path(cache_key)
    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }
    cache_file.write_text(json.dumps(payload))
