"""Egypt-specific news vendor combining Google News API and RSS feeds.

This module is registered as the "egypt_news" vendor in interface.py.
It automatically becomes the primary news source when market_region="egypt".
"""

from datetime import datetime, timedelta

from .egypt_tickers import get_company_names
from .egypt_news_google import (
    search_ticker_news,
    search_global_egypt_news,
    EgyptNewsError,
)
from .egypt_news_rss import fetch_rss_news, search_rss_for_ticker
from .config import get_market_region


def _deduplicate(articles: list) -> list:
    """Remove duplicate articles by title similarity."""
    seen = set()
    unique = []
    for article in articles:
        # Normalize title for dedup
        key = article["title"].strip().lower()[:60]
        if key not in seen:
            seen.add(key)
            unique.append(article)
    return unique


def _format_articles(articles: list, header: str) -> str:
    """Format a list of article dicts into a markdown string."""
    if not articles:
        return f"{header}\n\nNo articles found."

    news_str = ""
    for article in articles:
        news_str += f"### {article['title']} (source: {article['source']})\n"
        if article.get("snippet"):
            news_str += f"{article['snippet']}\n"
        if article.get("url"):
            news_str += f"Link: {article['url']}\n"
        if article.get("date"):
            news_str += f"Date: {article['date']}\n"
        news_str += "\n"

    return f"{header}\n\n{news_str}"


def get_news(ticker: str, start_date: str, end_date: str) -> str:
    """Get news for a specific EGX ticker.

    Combines Google News search + RSS feed filtering.
    Matches the vendor contract used by route_to_vendor().

    Args:
        ticker: Stock ticker (e.g., "COMI" or "COMI.CA").
        start_date: Start date in yyyy-mm-dd format.
        end_date: End date in yyyy-mm-dd format.

    Returns:
        Formatted markdown string with news articles.
    """
    company = get_company_names(ticker)
    name_en = company["name_en"]
    name_ar = company["name_ar"]

    # Calculate date range
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        date_range_days = max((end_dt - start_dt).days, 7)
    except ValueError:
        date_range_days = 7

    all_articles = []

    # Tier 1: Google News search
    try:
        google_results = search_ticker_news(
            name_en, name_ar,
            num_results=10, date_range_days=date_range_days,
        )
        all_articles.extend(google_results)
    except EgyptNewsError:
        pass  # Will fall through to RSS

    # Tier 2: RSS feed search
    try:
        rss_results = search_rss_for_ticker(
            name_en, name_ar, max_age_days=date_range_days,
        )
        all_articles.extend(rss_results)
    except Exception:
        pass

    # Deduplicate and format
    articles = _deduplicate(all_articles)

    clean_ticker = ticker.upper().replace(".CA", "")
    header = f"## {clean_ticker} ({name_en}) News, from {start_date} to {end_date}:"

    if not articles:
        return f"No news found for {clean_ticker} ({name_en}) between {start_date} and {end_date}"

    return _format_articles(articles, header)


def get_global_news(curr_date: str, look_back_days: int = 7, limit: int = 10) -> str:
    """Get Egypt macro/market news.

    Combines Google News search + RSS feeds.
    Matches the vendor contract used by route_to_vendor().

    Args:
        curr_date: Current date in yyyy-mm-dd format.
        look_back_days: Number of days to look back.
        limit: Maximum number of articles.

    Returns:
        Formatted markdown string with global Egypt news.
    """
    region = get_market_region()
    custom_queries = region.get("global_news_queries", None)

    all_articles = []

    # Tier 1: Google News search
    try:
        google_results = search_global_egypt_news(
            custom_queries=custom_queries,
            num_results=limit,
            date_range_days=look_back_days,
        )
        all_articles.extend(google_results)
    except EgyptNewsError:
        pass  # Will fall through to RSS

    # Tier 2: RSS feeds (general news, not ticker-specific)
    try:
        rss_results = fetch_rss_news(
            max_age_days=look_back_days, limit=limit,
        )
        all_articles.extend(rss_results)
    except Exception:
        pass

    # Deduplicate and limit
    articles = _deduplicate(all_articles)[:limit]

    # Calculate start date for header
    try:
        curr_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        start_dt = curr_dt - timedelta(days=look_back_days)
        start_date = start_dt.strftime("%Y-%m-%d")
    except ValueError:
        start_date = "N/A"

    header = f"## Egypt Market News, from {start_date} to {curr_date}:"

    if not articles:
        return f"No Egypt market news found for {curr_date}"

    return _format_articles(articles, header)
