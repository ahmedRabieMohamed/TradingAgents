"""Snapshot quote response models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SnapshotQuote(BaseModel):
    """Snapshot price and volume fields."""

    market_id: str
    symbol: str
    currency: str
    last_price: float
    change: float
    change_percent: float
    session_high: float
    session_low: float
    volume: int
    previous_close: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    spread: Optional[float] = None


class SnapshotSession(BaseModel):
    """Session status and next open/close windows."""

    status: str
    is_open: bool
    next_open: Optional[datetime]
    next_close: Optional[datetime]
    timezone: str


class SnapshotFreshness(BaseModel):
    """Freshness and cache metadata."""

    as_of: datetime
    age_seconds: int
    label: str
    is_stale: bool
    cache_status: str


class SnapshotEntitlement(BaseModel):
    """Entitlement details for quote latency."""

    realtime_available: bool
    delay_minutes: int
    effective_label: str


class SnapshotResponse(BaseModel):
    """Full snapshot response payload."""

    quote: SnapshotQuote
    session: SnapshotSession
    freshness: SnapshotFreshness
    entitlement: SnapshotEntitlement
