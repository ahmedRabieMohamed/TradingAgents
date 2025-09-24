from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel


class MarketType(str, Enum):
    US = "US Market"
    EGYPTIAN = "Egyptian Market"


class AnalystType(str, Enum):
    MARKET = "market"
    SOCIAL = "social"
    NEWS = "news"
    FUNDAMENTALS = "fundamentals"
    # Egyptian analysts
    EGYPTIAN_MARKET = "egyptian_market"
    EGYPTIAN_NEWS = "egyptian_news"
    EGYPTIAN_FUNDAMENTALS = "egyptian_fundamentals"
