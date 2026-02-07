import os
from datetime import datetime, timedelta

# Egyptian Exchange (EGX) Configuration
EGYPTIAN_CONFIG = {
    # Market Information
    "market_name": "Egyptian Exchange (EGX)",
    "market_code": "EGX",
    "currency": "EGP",
    "country": "Egypt",
    "timezone": "Africa/Cairo",
    # Trading Hours (Sunday to Thursday)
    "trading_hours": {
        "start": "10:00",
        "end": "14:30",
        "days": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"],
        "timezone": "Africa/Cairo",
    },
    # Major Egyptian Stocks
    "major_stocks": {
        "COMI": {
            "name": "Commercial International Bank",
            "sector": "Banking",
            "yahoo_symbol": "COMI.CA",
        },
        "ORAS": {
            "name": "Orascom Construction",
            "sector": "Construction",
            "yahoo_symbol": "ORAS.CA",
        },
        "EFID": {
            "name": "EFG Hermes",
            "sector": "Financial Services",
            "yahoo_symbol": "EFID.CA",
        },
        "EGBE": {
            "name": "Egyptian Bank",
            "sector": "Banking",
            "yahoo_symbol": "EGBE.CA",
        },
        "SWDY": {
            "name": "El Sewedy Electric",
            "sector": "Industrial",
            "yahoo_symbol": "SWDY.CA",
        },
        "OCIC": {
            "name": "Orascom Investment",
            "sector": "Investment",
            "yahoo_symbol": "OCIC.CA",
        },
        "FWRY": {"name": "Fawry", "sector": "Technology", "yahoo_symbol": "FWRY.CA"},
        "RAPH": {
            "name": "Raya Holding",
            "sector": "Technology",
            "yahoo_symbol": "RAPH.CA",
        },
        "ABUK": {
            "name": "Abu Qir Fertilizers",
            "sector": "Chemicals",
            "yahoo_symbol": "ABUK.CA",
        },
        "EGTS": {
            "name": "Egyptian Tourism",
            "sector": "Tourism",
            "yahoo_symbol": "EGTS.CA",
        },
    },
    # Data Sources Configuration
    "data_sources": {
        "primary": "yahoo_finance",
        "backup": "eodhd",
        "eodhd_api_key": None,  # Set your EODHD API key here
        "yahoo_suffix": ".CA",  # Egyptian stocks suffix on Yahoo Finance
    },
    # Egyptian Market Specific Settings
    "market_specific": {
        "trading_days_per_week": 5,  # Sunday to Thursday
        "market_cap_categories": {
            "large_cap": 10000000000,  # 10B EGP
            "mid_cap": 1000000000,  # 1B EGP
            "small_cap": 100000000,  # 100M EGP
        },
        "volatility_threshold": 0.05,  # 5% daily volatility threshold
        "liquidity_threshold": 1000000,  # 1M EGP daily volume threshold
    },
    # Egyptian Holidays (2025)
    "holidays_2025": [
        "2025-01-01",  # New Year
        "2025-01-25",  # Revolution Day
        "2025-04-10",  # Sham El Nessim
        "2025-04-21",  # Coptic Easter Monday
        "2025-05-01",  # Labor Day
        "2025-05-05",  # Liberation Day
        "2025-05-15",  # Sinai Liberation Day
        "2025-06-30",  # Revolution Day
        "2025-07-23",  # Revolution Day
        "2025-10-06",  # Armed Forces Day
        "2025-12-25",  # Christmas
    ],
    # News Sources for Egyptian Market
    "news_sources": {
        "arabic": ["الأهرام", "الوفد", "المصري اليوم", "اليوم السابع", "الوطن"],
        "english": [
            "Egypt Today",
            "Ahram Online",
            "Daily News Egypt",
            "Egypt Independent",
        ],
        "financial": ["Al Mal News", "Al Borsa News", "Mubasher Info"],
    },
    # Economic Indicators
    "economic_indicators": {
        "currency": "EGP",
        "inflation_target": 0.07,  # 7% target
        "interest_rate_range": [0.18, 0.25],  # 18-25% range
        "gdp_growth_target": 0.05,  # 5% target
    },
    # Project Directories
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./egyptian_results"),
    "data_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")), "egyptian_data"
    ),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/egyptian_data_cache",
    ),
    # LLM Settings (same as default)
    "llm_provider": "openai",
    "deep_think_llm": "o4-mini",
    "quick_think_llm": "gpt-4o-mini",
    "backend_url": "https://api.openai.com/v1",
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Tool settings
    "online_tools": True,
    # Validation settings
    "validate_state": True,
    # Egyptian Market Analysis Settings
    "analysis_settings": {
        "lookback_days": 30,
        "technical_indicators": [
            "close_50_sma",
            "close_200_sma",
            "close_10_ema",
            "macd",
            "macds",
            "macdh",
            "rsi",
            "boll",
            "boll_ub",
            "boll_lb",
            "atr",
            "vwma",
        ],
        "fundamental_metrics": [
            "pe_ratio",
            "pb_ratio",
            "debt_to_equity",
            "roe",
            "roa",
            "current_ratio",
            "quick_ratio",
        ],
    },
}


def get_egyptian_stock_info(symbol):
    """Get information about an Egyptian stock symbol"""
    return EGYPTIAN_CONFIG["major_stocks"].get(symbol.upper(), None)


def is_egyptian_trading_day(date_str):
    """Check if a given date is an Egyptian trading day"""
    date = datetime.strptime(date_str, "%Y-%m-%d")

    # Check if it's a weekend (Friday or Saturday)
    if date.weekday() in [4, 5]:  # Friday=4, Saturday=5
        return False

    # Check if it's a holiday
    if date_str in EGYPTIAN_CONFIG["holidays_2025"]:
        return False

    return True


def get_next_egyptian_trading_day(date_str):
    """Get the next Egyptian trading day"""
    date = datetime.strptime(date_str, "%Y-%m-%d")

    while True:
        date += timedelta(days=1)
        date_str = date.strftime("%Y-%m-%d")

        if is_egyptian_trading_day(date_str):
            return date_str


def format_egyptian_price(price):
    """Format price in Egyptian Pounds"""
    return f"{price:.2f} EGP"
