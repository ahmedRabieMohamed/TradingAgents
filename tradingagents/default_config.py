import os

# Market region definitions
MARKET_REGIONS = {
    "us": {
        "currency": "USD",
        "exchange": "NYSE/NASDAQ",
        "ticker_suffix": "",
        "weekend_days": [5, 6],  # Saturday, Sunday
        "global_news_queries": [
            "stock market economy",
            "Federal Reserve interest rates",
            "inflation economic outlook",
            "global markets trading",
        ],
        "central_bank": "Federal Reserve",
        "macro_topics": "financial_markets,economy_macro,economy_monetary",
        "market_context": (
            "This is a US-listed stock trading on NYSE/NASDAQ. "
            "Currency is USD. The relevant central bank is the Federal Reserve. "
            "Financial reporting follows US GAAP standards."
        ),
    },
    "egypt": {
        "currency": "EGP",
        "exchange": "EGX (Egyptian Exchange)",
        "ticker_suffix": ".CA",  # Cairo exchange suffix for yfinance
        "weekend_days": [4, 5],  # Friday, Saturday
        "global_news_queries": [
            # English queries
            "Egypt stock market EGX",
            "Central Bank of Egypt interest rates",
            "Egypt economy inflation outlook",
            "Egyptian pound exchange rate EGP",
            "MENA emerging markets trading",
            # Arabic queries (for Google News / Serper)
            "البورصة المصرية اليوم",
            "البنك المركزي المصري قرارات",
            "الاقتصاد المصري",
            "سعر صرف الجنيه المصري",
        ],
        "central_bank": "Central Bank of Egypt (CBE)",
        "macro_topics": "financial_markets,economy_macro,emerging_markets",
        "market_context": (
            "This is an Egyptian stock trading on the EGX (Egyptian Exchange). "
            "Currency is EGP (Egyptian Pound). The relevant central bank is the "
            "Central Bank of Egypt (CBE). Financial reporting follows Egyptian "
            "Accounting Standards (based on IFRS). The EGX trades Sunday-Thursday "
            "and is closed on Fridays and Saturdays. Key macro factors include "
            "EGP/USD exchange rate, CBE monetary policy, Suez Canal revenues, "
            "tourism sector, and remittances from Egyptians abroad."
        ),
        # Route news to egypt_news vendor automatically
        "vendor_overrides": {
            "news_data": "egypt_news",
        },
    },
}

# Trade horizon definitions
TRADE_HORIZONS = {
    "intraday": {
        "label": "Intraday (1-4 hours)",
        "description": (
            "Ultra-short-term trade. Focus on momentum, order flow, intraday "
            "catalysts, and technical breakouts. Ignore long-term fundamentals "
            "unless there is an imminent event (earnings, dividend, major "
            "announcement) within the next few hours."
        ),
        "lookback_days": 5,
    },
    "short-term": {
        "label": "Short-Term (1-5 days)",
        "description": (
            "Short swing trade. Focus on technical patterns, news catalysts, "
            "and short-term momentum. Fundamentals matter only if there is a "
            "near-term catalyst."
        ),
        "lookback_days": 30,
    },
    "medium-term": {
        "label": "Medium-Term (1-4 weeks)",
        "description": (
            "Swing/position trade. Balance technical and fundamental analysis. "
            "Consider earnings cycles, sector rotation, and macro trends."
        ),
        "lookback_days": 90,
    },
    "long-term": {
        "label": "Long-Term (1+ months)",
        "description": (
            "Position/investment. Emphasize fundamentals, valuation, and macro "
            "trends. Technical analysis is secondary."
        ),
        "lookback_days": 365,
    },
}

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # Market region: "us" or "egypt"
    "market_region": "us",
    # Trade horizon: "intraday", "short-term", "medium-term", "long-term"
    "trade_horizon": "short-term",
    # LLM settings
    "llm_provider": "openai",
    "deep_think_llm": "gpt-5.2",
    "quick_think_llm": "gpt-5-mini",
    "backend_url": "https://api.openai.com/v1",
    # Provider-specific thinking configuration
    "google_thinking_level": None,      # "high", "minimal", etc.
    "openai_reasoning_effort": None,    # "medium", "high", "low"
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Data vendor configuration
    # Category-level configuration (default for all tools in category)
    "data_vendors": {
        "core_stock_apis": "yfinance",       # Options: alpha_vantage, yfinance
        "technical_indicators": "yfinance",  # Options: alpha_vantage, yfinance
        "fundamental_data": "yfinance",      # Options: alpha_vantage, yfinance
        "news_data": "yfinance",             # Options: alpha_vantage, yfinance
    },
    # Tool-level configuration (takes precedence over category-level)
    "tool_vendors": {
        # Example: "get_stock_data": "alpha_vantage",  # Override category default
    },
}
