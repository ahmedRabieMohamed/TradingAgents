"""Stocks router — ticker validation and price history."""

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import PriceHistoryResponse, StockValidationError, StockValidationResponse
from app.services.market_data import get_price_history
from app.services.stock_info import validate_stock

router = APIRouter(prefix="/stocks", tags=["stocks"])

VALID_PERIODS = {"1w", "1mo", "3mo", "6mo", "1y"}


@router.get("/price-history", response_model=PriceHistoryResponse)
async def price_history_endpoint(
    ticker: str = Query(..., min_length=1, max_length=10, description="Stock ticker symbol"),
    market_id: str = Query(..., description="Market id (e.g. 'us' or 'egypt')"),
    period: str = Query("3mo", description="Time period: 1w, 1mo, 3mo, 6mo, 1y"),
):
    """Fetch OHLC candlestick data for a ticker."""
    if period not in VALID_PERIODS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid period. Must be one of: {', '.join(sorted(VALID_PERIODS))}",
        )

    try:
        result = await get_price_history(ticker=ticker, market_id=market_id, period=period)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to fetch price history. Please try again.") from exc

    if not result["bars"]:
        # Still return 200 with empty bars — ticker may be valid but no data for period
        pass

    return result


@router.get("/validate", response_model=StockValidationResponse, responses={404: {"model": StockValidationError}})
async def validate_stock_endpoint(
    ticker: str = Query(..., min_length=1, max_length=10, description="Stock ticker symbol"),
    market: str = Query(..., description="Market id (e.g. 'us' or 'egypt')"),
):
    """Validate a stock ticker and return basic price info."""
    try:
        result = await validate_stock(ticker=ticker, market_id=market)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return StockValidationResponse(
        valid=result["valid"],
        ticker=result["ticker"],
        name=result["name"],
        price=result["price"],
        currency=result["currency"],
        exchange=None,
    )
