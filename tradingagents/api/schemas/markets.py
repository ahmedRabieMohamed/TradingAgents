"""Market discovery response models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MarketResponse(BaseModel):
    market_id: str
    name: str
    mic: str
    timezone: str
    currency: str
    session_open: str
    session_close: str
    trading_days: list[int]
    data_delay_minutes: int
    realtime_available: bool
    status: str
    next_open: Optional[datetime]
    next_close: Optional[datetime]


class MarketListResponse(BaseModel):
    count: int
    items: list[MarketResponse]
