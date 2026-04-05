"""News service -- wraps tradingagents dataflow news functions with caching.

Produces normalised ``NewsArticle`` dicts:
    {title, snippet, source, url, published_at, is_hot}
"""

import logging
import re
import time
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

_news_cache: dict[str, tuple[float, list[dict]]] = {}
NEWS_CACHE_TTL = 600  # 10 minutes


# ---------------------------------------------------------------------------
# Internal parsers
# ---------------------------------------------------------------------------


def _parse_yfinance_article(article: dict) -> dict[str, Any] | None:
    """Convert a raw yfinance article (flat or nested 'content') into a NewsArticle dict."""
    try:
        if "content" in article:
            content = article["content"]
            title = content.get("title", "")
            snippet = content.get("summary", "")
            provider = content.get("provider", {})
            source = provider.get("displayName", "Unknown")
            url_obj = content.get("canonicalUrl") or content.get("clickThroughUrl") or {}
            url = url_obj.get("url", "")
            pub_date_str = content.get("pubDate", "")
        else:
            title = article.get("title", "")
            snippet = article.get("summary", "")
            source = article.get("publisher", "Unknown")
            url = article.get("link", "")
            pub_date_str = ""

        if not title:
            return None

        published_at: str | None = None
        if pub_date_str:
            try:
                dt = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
                published_at = dt.isoformat()
            except (ValueError, AttributeError):
                pass

        return {
            "title": title,
            "snippet": snippet,
            "source": source,
            "url": url,
            "published_at": published_at,
            "is_hot": False,
        }
    except Exception:
        return None


def _parse_egypt_article(article: dict) -> dict[str, Any] | None:
    """Convert a raw Egypt news article dict into a normalised NewsArticle dict.

    Egypt news modules (google + rss) return dicts with keys:
        title, snippet, source, url, date
    """
    try:
        title = article.get("title", "")
        if not title:
            return None
        return {
            "title": title,
            "snippet": article.get("snippet", ""),
            "source": article.get("source", "Unknown"),
            "url": article.get("url", ""),
            "published_at": article.get("date"),
            "is_hot": False,
        }
    except Exception:
        return None


def _parse_markdown_news(raw: str) -> list[dict[str, Any]]:
    """Fallback: parse the formatted markdown string returned by news functions.

    Pattern per article:
        ### Title (source: Publisher)
        Summary text
        Link: https://...
        Date: ...
    """
    articles: list[dict] = []
    # Split on markdown H3 headers
    blocks = re.split(r"^### ", raw, flags=re.MULTILINE)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        # First line: "Title (source: Publisher)"
        header_match = re.match(r"^(.+?)\s*\(source:\s*(.+?)\)\s*$", block.split("\n")[0])
        if not header_match:
            continue
        title = header_match.group(1).strip()
        source = header_match.group(2).strip()

        lines = block.split("\n")[1:]
        snippet = ""
        url = ""
        pub_date = None
        for line in lines:
            line = line.strip()
            if line.startswith("Link:"):
                url = line[5:].strip()
            elif line.startswith("Date:"):
                pub_date = line[5:].strip()
            elif line and not snippet:
                snippet = line

        articles.append({
            "title": title,
            "snippet": snippet,
            "source": source,
            "url": url,
            "published_at": pub_date,
            "is_hot": False,
        })
    return articles


# ---------------------------------------------------------------------------
# Fetchers that call into tradingagents dataflows directly (structured data)
# ---------------------------------------------------------------------------


def _fetch_egypt_global_articles(limit: int, look_back_days: int) -> list[dict]:
    """Fetch Egypt global news using the underlying structured functions."""
    from tradingagents.dataflows.egypt_news_google import search_global_egypt_news, EgyptNewsError
    from tradingagents.dataflows.egypt_news_rss import fetch_rss_news
    from tradingagents.dataflows.config import get_market_region

    region = get_market_region()
    custom_queries = region.get("global_news_queries", None)

    all_articles: list[dict] = []

    try:
        google_results = search_global_egypt_news(
            custom_queries=custom_queries,
            num_results=limit,
            date_range_days=look_back_days,
        )
        for a in google_results:
            parsed = _parse_egypt_article(a)
            if parsed:
                all_articles.append(parsed)
    except (EgyptNewsError, Exception):
        pass

    try:
        rss_results = fetch_rss_news(max_age_days=look_back_days, limit=limit)
        for a in rss_results:
            parsed = _parse_egypt_article(a)
            if parsed:
                all_articles.append(parsed)
    except Exception:
        pass

    # Deduplicate by title prefix
    seen: set[str] = set()
    unique: list[dict] = []
    for art in all_articles:
        key = art["title"].strip().lower()[:60]
        if key not in seen:
            seen.add(key)
            unique.append(art)

    return unique[:limit]


def _fetch_egypt_ticker_articles(ticker: str, limit: int, look_back_days: int) -> list[dict]:
    """Fetch Egypt ticker news using structured google + rss functions."""
    from tradingagents.dataflows.egypt_tickers import get_company_names
    from tradingagents.dataflows.egypt_news_google import search_ticker_news, EgyptNewsError
    from tradingagents.dataflows.egypt_news_rss import search_rss_for_ticker

    company = get_company_names(ticker)
    name_en = company["name_en"]
    name_ar = company["name_ar"]

    all_articles: list[dict] = []

    try:
        google_results = search_ticker_news(
            name_en, name_ar,
            num_results=limit,
            date_range_days=look_back_days,
        )
        for a in google_results:
            parsed = _parse_egypt_article(a)
            if parsed:
                all_articles.append(parsed)
    except (EgyptNewsError, Exception):
        pass

    try:
        rss_results = search_rss_for_ticker(name_en, name_ar, max_age_days=look_back_days)
        for a in rss_results:
            parsed = _parse_egypt_article(a)
            if parsed:
                all_articles.append(parsed)
    except Exception:
        pass

    # Deduplicate
    seen: set[str] = set()
    unique: list[dict] = []
    for art in all_articles:
        key = art["title"].strip().lower()[:60]
        if key not in seen:
            seen.add(key)
            unique.append(art)

    return unique[:limit]


def _fetch_us_global_articles(limit: int, look_back_days: int) -> list[dict]:
    """Fetch US global news via yfinance Search (structured)."""
    import yfinance as yf

    from tradingagents.default_config import MARKET_REGIONS

    region = MARKET_REGIONS.get("us", {})
    queries = region.get("global_news_queries", [
        "stock market economy",
        "Federal Reserve interest rates",
    ])

    all_articles: list[dict] = []
    seen_titles: set[str] = set()

    try:
        for query in queries:
            search = yf.Search(query=query, news_count=limit, enable_fuzzy_query=True)
            if search.news:
                for article in search.news:
                    parsed = _parse_yfinance_article(article)
                    if parsed and parsed["title"]:
                        key = parsed["title"].strip().lower()[:60]
                        if key not in seen_titles:
                            seen_titles.add(key)
                            all_articles.append(parsed)
            if len(all_articles) >= limit:
                break
    except Exception:
        logger.exception("Failed to fetch US global news via yfinance")

    return all_articles[:limit]


def _fetch_us_ticker_articles(ticker: str, limit: int) -> list[dict]:
    """Fetch US ticker news via yfinance Ticker.get_news()."""
    import yfinance as yf

    articles: list[dict] = []
    try:
        stock = yf.Ticker(ticker)
        news = stock.get_news(count=limit * 2)  # fetch extra, some may be filtered
        if news:
            for article in news:
                parsed = _parse_yfinance_article(article)
                if parsed:
                    articles.append(parsed)
    except Exception:
        logger.exception("Failed to fetch ticker news for %s", ticker)

    return articles[:limit]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def get_market_news(market_id: str, limit: int = 15) -> list[dict]:
    """Get market-level news articles."""
    cache_key = f"market_{market_id}"
    if cache_key in _news_cache:
        ts, articles = _news_cache[cache_key]
        if time.time() - ts < NEWS_CACHE_TTL:
            return articles[:limit]

    articles: list[dict] = []
    try:
        if market_id == "egypt":
            articles = _fetch_egypt_global_articles(limit, look_back_days=3)
        else:
            articles = _fetch_us_global_articles(limit, look_back_days=3)
    except Exception:
        logger.exception("Failed to fetch market news for %s", market_id)

    _news_cache[cache_key] = (time.time(), articles)
    return articles[:limit]


async def get_ticker_news(ticker: str, market_id: str, limit: int = 10) -> list[dict]:
    """Get news for a specific ticker."""
    cache_key = f"ticker_{market_id}_{ticker}"
    if cache_key in _news_cache:
        ts, articles = _news_cache[cache_key]
        if time.time() - ts < NEWS_CACHE_TTL:
            return articles[:limit]

    articles: list[dict] = []
    try:
        if market_id == "egypt":
            articles = _fetch_egypt_ticker_articles(ticker, limit, look_back_days=7)
        else:
            articles = _fetch_us_ticker_articles(ticker, limit)
    except Exception:
        logger.exception("Failed to fetch ticker news for %s/%s", market_id, ticker)

    _news_cache[cache_key] = (time.time(), articles)
    return articles[:limit]
