"""Markets router — returns available market regions."""

from fastapi import APIRouter

from tradingagents.default_config import MARKET_REGIONS

from app.models.schemas import MarketSchema, MarketsResponse

router = APIRouter(prefix="/markets", tags=["markets"])

# Human-readable names and example tickers per market
_MARKET_META: dict[str, dict] = {
    "us": {
        "name": "United States",
        "trading_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "example_tickers": ["AAPL", "NVDA", "TSLA", "MSFT", "SPY"],
    },
    "egypt": {
        "name": "Egypt",
        "trading_days": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"],
        "example_tickers": ["COMI", "HRHO", "TMGH", "EFIH", "SWDY"],
    },
}


@router.get("", response_model=MarketsResponse)
async def get_markets():
    """Return every market region defined in the parent tradingagents config."""
    markets: list[MarketSchema] = []
    for market_id, cfg in MARKET_REGIONS.items():
        meta = _MARKET_META.get(market_id, {})
        markets.append(
            MarketSchema(
                id=market_id,
                name=meta.get("name", market_id.title()),
                exchange=cfg["exchange"],
                currency=cfg["currency"],
                trading_days=meta.get("trading_days", []),
                ticker_suffix=cfg.get("ticker_suffix", ""),
                example_tickers=meta.get("example_tickers", []),
            )
        )
    return MarketsResponse(markets=markets)
