"""Symbol discovery response models."""

from typing import List, Optional

from pydantic import BaseModel


class ListMeta(BaseModel):
    definition: str
    window: str


class SymbolResponse(BaseModel):
    ticker: str
    name: str
    sector: str
    market_cap: float
    avg_volume_1w: float
    price_change_pct_1w: float
    currency: str


class SymbolListResponse(BaseModel):
    count: int
    items: List[SymbolResponse]
    next_offset: Optional[int] = None
    meta: Optional[ListMeta] = None
