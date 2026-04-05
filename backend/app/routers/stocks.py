"""Stocks router — ticker validation."""

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import StockValidationError, StockValidationResponse
from app.services.stock_info import validate_stock

router = APIRouter(prefix="/stocks", tags=["stocks"])


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
