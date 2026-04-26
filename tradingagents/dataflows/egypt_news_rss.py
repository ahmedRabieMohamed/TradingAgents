"""RSS feed aggregator for Egypt financial news.

Uses Google News RSS (free, no API key) + Daily News Egypt as sources.
"""

import re
import feedparser
import requests
from datetime import datetime, timedelta
from time import mktime
from urllib.parse import quote


# Google News RSS base URL (free, no API key needed)
_GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"

# Static RSS feeds that work reliably
EGYPT_RSS_FEEDS = {
    "dailynewsegypt": {
        "name": "Daily News Egypt",
        "url": "https://dailynewsegypt.com/feed/",
        "language": "en",
    },
}


def _build_google_news_rss_url(query: str, language: str = "ar",
                                country: str = "EG") -> str:
    """Build a Google News RSS URL for a search query."""
    encoded_query = quote(query)
    lang_code = f"{country}:{language}"
    return f"{_GOOGLE_NEWS_RSS}?q={encoded_query}&hl={language}&gl={country}&ceid={lang_code}"


def _parse_feed_date(entry) -> datetime:
    """Extract publication date from an RSS entry."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime.fromtimestamp(mktime(entry.published_parsed))
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        return datetime.fromtimestamp(mktime(entry.updated_parsed))
    return None


def _strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text).strip()
    if len(clean) > 300:
        clean = clean[:297] + "..."
    return clean


def _fetch_single_feed(url: str, source_name: str, max_age_days: int) -> list:
    """Fetch articles from a single RSS feed URL."""
    cutoff = datetime.now() - timedelta(days=max_age_days)
    articles = []

    try:
        response = requests.get(
            url, timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        if response.status_code != 200:
            return []

        feed = feedparser.parse(response.text)

        for entry in feed.entries:
            pub_date = _parse_feed_date(entry)
            if pub_date and pub_date < cutoff:
                continue

            title = entry.get("title", "").strip()
            if not title:
                continue

            summary = _strip_html(
                entry.get("summary", entry.get("description", ""))
            )

            # Google News titles often include " - Source Name"
            display_source = source_name
            if " - " in title:
                parts = title.rsplit(" - ", 1)
                if len(parts) == 2 and len(parts[1]) < 50:
                    title = parts[0]
                    display_source = parts[1]

            articles.append({
                "title": title,
                "snippet": summary,
                "source": display_source,
                "url": entry.get("link", ""),
                "date": pub_date.strftime("%Y-%m-%d") if pub_date else "",
            })

    except Exception:
        pass

    return articles


def fetch_rss_news(max_age_days: int = 7, limit: int = 20) -> list:
    """Fetch Egypt macro/market news from Google News RSS + static feeds.

    Args:
        max_age_days: Only include articles from the last N days.
        limit: Maximum total articles to return.

    Returns:
        List of dicts: {title, snippet, source, url, date}
    """
    all_articles = []

    # Google News RSS — Arabic Egypt market news (free, high volume)
    google_queries_ar = [
        "البورصة المصرية",
        "البنك المركزي المصري",
    ]
    for query in google_queries_ar:
        url = _build_google_news_rss_url(query, language="ar")
        all_articles.extend(
            _fetch_single_feed(url, "Google News", max_age_days)
        )

    # Google News RSS — English Egypt market news
    google_queries_en = [
        "Egypt stock market EGX",
        "Central Bank of Egypt",
    ]
    for query in google_queries_en:
        url = _build_google_news_rss_url(query, language="en")
        all_articles.extend(
            _fetch_single_feed(url, "Google News", max_age_days)
        )

    # Static RSS feeds
    for feed_id, feed_info in EGYPT_RSS_FEEDS.items():
        all_articles.extend(
            _fetch_single_feed(feed_info["url"], feed_info["name"], max_age_days)
        )

    # Deduplicate by title
    seen = set()
    unique = []
    for article in all_articles:
        key = article["title"].strip().lower()[:60]
        if key not in seen:
            seen.add(key)
            unique.append(article)

    # Sort by date (newest first)
    unique.sort(key=lambda x: x.get("date", ""), reverse=True)

    return unique[:limit]


def search_rss_for_ticker(
    company_name_en: str,
    company_name_ar: str,
    max_age_days: int = 7,
) -> list:
    """Search Google News RSS for a specific EGX company.

    Args:
        company_name_en: English company name.
        company_name_ar: Arabic company name.
        max_age_days: Only include articles from the last N days.

    Returns:
        List of matching article dicts.
    """
    articles = []

    # Direct Google News RSS search for the company
    for query, lang in [(company_name_ar, "ar"), (company_name_en + " EGX", "en")]:
        url = _build_google_news_rss_url(query, language=lang)
        articles.extend(
            _fetch_single_feed(url, "Google News", max_age_days)
        )

    # Deduplicate
    seen = set()
    unique = []
    for article in articles:
        key = article["title"].strip().lower()[:60]
        if key not in seen:
            seen.add(key)
            unique.append(article)

    return unique
