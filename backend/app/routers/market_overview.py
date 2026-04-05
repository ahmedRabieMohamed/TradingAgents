"""Market Overview router -- stocks, indices, movers, and news."""

from fastapi import APIRouter, HTTPException, Query

from app.services.market_data import get_market_overview
from app.services.news import get_market_news, get_ticker_news

router = APIRouter(prefix="/market-overview", tags=["market-overview"])

VALID_MARKETS = {"us", "egypt"}


def _validate_market(market_id: str) -> None:
    if market_id not in VALID_MARKETS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown market_id: {market_id}. Must be one of {sorted(VALID_MARKETS)}.",
        )


@router.get("/{market_id}")
async def market_overview(market_id: str):
    """Return the full market overview: indices, stocks, movers, and summary."""
    _validate_market(market_id)
    return await get_market_overview(market_id)


@router.get("/{market_id}/news")
async def market_news(
    market_id: str,
    limit: int = Query(15, ge=1, le=50),
    ticker: str | None = Query(None),
):
    """Return market-level or ticker-specific news articles."""
    _validate_market(market_id)
    if ticker:
        articles = await get_ticker_news(ticker, market_id, limit)
    else:
        articles = await get_market_news(market_id, limit)
    return {"market_id": market_id, "ticker": ticker, "articles": articles}
