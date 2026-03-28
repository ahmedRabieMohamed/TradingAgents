"""Google News search via Serper.dev API for Egypt financial news."""

import os
import requests
from datetime import datetime, timedelta


class EgyptNewsError(Exception):
    """Raised when Egypt news fetching fails."""
    pass


def search_google_news(
    queries: list,
    num_results: int = 10,
    date_range_days: int = 7,
    language: str = "ar",
    country: str = "eg",
) -> list:
    """Search Google News via Serper.dev for Egypt financial news.

    Args:
        queries: List of search query strings (Arabic or English).
        num_results: Max results per query.
        date_range_days: How many days back to search.
        language: Language code (ar for Arabic, en for English).
        country: Country code (eg for Egypt).

    Returns:
        List of dicts: {title, snippet, source, url, date}

    Raises:
        EgyptNewsError: If API key is missing or request fails.
    """
    api_key = os.environ.get("SERPER_API_KEY")
    if not api_key:
        raise EgyptNewsError(
            "SERPER_API_KEY not set. Get one at https://serper.dev"
        )

    all_results = []
    seen_titles = set()

    for query in queries:
        try:
            response = requests.post(
                "https://google.serper.dev/news",
                json={
                    "q": query,
                    "gl": country,
                    "hl": language,
                    "num": num_results,
                    "tbs": f"qdr:d{date_range_days}",
                },
                headers={
                    "X-API-KEY": api_key,
                    "Content-Type": "application/json",
                },
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            for item in data.get("news", []):
                title = item.get("title", "")
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    all_results.append({
                        "title": title,
                        "snippet": item.get("snippet", ""),
                        "source": item.get("source", "Unknown"),
                        "url": item.get("link", ""),
                        "date": item.get("date", ""),
                    })

        except requests.RequestException as e:
            # Continue with other queries if one fails
            continue

    return all_results


def search_ticker_news(company_name_en: str, company_name_ar: str,
                       num_results: int = 10, date_range_days: int = 7) -> list:
    """Search for news about a specific EGX company.

    Args:
        company_name_en: English company name.
        company_name_ar: Arabic company name.
        num_results: Max results per query.
        date_range_days: How many days back to search.

    Returns:
        List of news article dicts.
    """
    queries = [
        f"{company_name_ar} البورصة",
        f"{company_name_en} EGX stock",
    ]
    return search_google_news(
        queries, num_results=num_results, date_range_days=date_range_days
    )


def search_global_egypt_news(custom_queries: list = None,
                              num_results: int = 10,
                              date_range_days: int = 7) -> list:
    """Search for Egypt macro/market news.

    Args:
        custom_queries: Optional list of queries. Uses defaults if None.
        num_results: Max results per query.
        date_range_days: How many days back to search.

    Returns:
        List of news article dicts.
    """
    if custom_queries is None:
        custom_queries = [
            "البورصة المصرية اليوم",
            "البنك المركزي المصري قرارات",
            "سعر صرف الجنيه المصري",
            "Egypt stock market EGX",
            "Central Bank of Egypt",
        ]
    return search_google_news(
        custom_queries, num_results=num_results, date_range_days=date_range_days
    )
