"""Watchlist router — save and manage favorite tickers."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.database import WatchlistItem
from app.models.schemas import WatchlistItemCreate, WatchlistItemResponse, WatchlistResponse

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=WatchlistResponse)
async def get_watchlist(db: AsyncSession = Depends(get_db)):
    """Return all watchlist items with live prices."""
    result = await db.execute(
        select(WatchlistItem).order_by(WatchlistItem.added_at.desc())
    )
    items = result.scalars().all()

    # Build response items
    response_items: list[dict] = []
    for item in items:
        data = {
            "id": item.id,
            "ticker": item.ticker,
            "market_id": item.market_id,
            "name": item.name,
            "added_at": item.added_at,
            "notes": item.notes,
            "price": None,
            "change_pct": None,
            "currency": "EGP" if item.market_id == "egypt" else "USD",
        }
        response_items.append(data)

    # Fetch live prices (best effort)
    try:
        import yfinance as yf
        from app.services.market_data import _to_yf_ticker

        if response_items:
            symbols = [_to_yf_ticker(d["ticker"], d["market_id"]) for d in response_items]
            df = yf.download(symbols, period="2d", progress=False)

            if df is not None and not df.empty:
                if hasattr(df.columns, "levels"):
                    for i, sym in enumerate(symbols):
                        try:
                            ticker_data = df.xs(sym, level="Ticker", axis=1)
                            closes = ticker_data["Close"].dropna()
                            if len(closes) >= 2:
                                last = float(closes.iloc[-1])
                                prev = float(closes.iloc[-2])
                                response_items[i]["price"] = round(last, 2)
                                response_items[i]["change_pct"] = round(
                                    ((last - prev) / prev) * 100, 2
                                ) if prev else 0.0
                            elif len(closes) == 1:
                                response_items[i]["price"] = round(float(closes.iloc[0]), 2)
                        except (KeyError, IndexError):
                            pass
                else:
                    closes = df["Close"].dropna()
                    if len(closes) >= 2:
                        last = float(closes.iloc[-1])
                        prev = float(closes.iloc[-2])
                        response_items[0]["price"] = round(last, 2)
                        response_items[0]["change_pct"] = round(
                            ((last - prev) / prev) * 100, 2
                        ) if prev else 0.0
    except Exception:
        pass  # Prices are optional

    return WatchlistResponse(items=[WatchlistItemResponse(**d) for d in response_items])


@router.post("", response_model=WatchlistItemResponse, status_code=201)
async def add_to_watchlist(body: WatchlistItemCreate, db: AsyncSession = Depends(get_db)):
    """Add a ticker to the watchlist."""
    existing = await db.execute(
        select(WatchlistItem).where(
            WatchlistItem.ticker == body.ticker.upper(),
            WatchlistItem.market_id == body.market_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Ticker already in watchlist")

    item = WatchlistItem(
        ticker=body.ticker.upper(),
        market_id=body.market_id,
        name=body.name,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)

    return WatchlistItemResponse(
        id=item.id,
        ticker=item.ticker,
        market_id=item.market_id,
        name=item.name,
        added_at=item.added_at,
        notes=item.notes,
        currency="EGP" if item.market_id == "egypt" else "USD",
    )


@router.delete("/{item_id}", status_code=204)
async def remove_from_watchlist(item_id: str, db: AsyncSession = Depends(get_db)):
    """Remove a ticker from the watchlist."""
    result = await db.execute(
        delete(WatchlistItem).where(WatchlistItem.id == item_id)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
