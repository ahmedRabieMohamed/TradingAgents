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

# Single source of truth for env-var → config-key overrides. To expose
# a new config key for environment-based override, add a row here — no
# entry-point script changes required. Coercion is driven by the type
# of the existing default, so users can keep writing plain strings in
# their .env file.
_ENV_OVERRIDES = {
    "TRADINGAGENTS_LLM_PROVIDER":         "llm_provider",
    "TRADINGAGENTS_DEEP_THINK_LLM":       "deep_think_llm",
    "TRADINGAGENTS_QUICK_THINK_LLM":      "quick_think_llm",
    "TRADINGAGENTS_LLM_BACKEND_URL":      "backend_url",
    "TRADINGAGENTS_OUTPUT_LANGUAGE":      "output_language",
    "TRADINGAGENTS_MAX_DEBATE_ROUNDS":    "max_debate_rounds",
    "TRADINGAGENTS_MAX_RISK_ROUNDS":      "max_risk_discuss_rounds",
    "TRADINGAGENTS_CHECKPOINT_ENABLED":   "checkpoint_enabled",
    "TRADINGAGENTS_BENCHMARK_TICKER":     "benchmark_ticker",
    "TRADINGAGENTS_TEMPERATURE":          "temperature",
}


def _coerce(value: str, reference):
    """Coerce env-var string to the type of the existing default value."""
    if isinstance(reference, bool):
        return value.strip().lower() in ("true", "1", "yes", "on")
    if isinstance(reference, int) and not isinstance(reference, bool):
        return int(value)
    if isinstance(reference, float):
        return float(value)
    return value


def _apply_env_overrides(config: dict) -> dict:
    """Apply TRADINGAGENTS_* env vars to the config dict in-place."""
    for env_var, key in _ENV_OVERRIDES.items():
        raw = os.environ.get(env_var)
        if raw is None or raw == "":
            continue
        config[key] = _coerce(raw, config.get(key))
    return config


DEFAULT_CONFIG = _apply_env_overrides({
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
    "deep_think_llm": "gpt-5.5",
    "quick_think_llm": "gpt-5.4-mini",
    # When None, each provider's client falls back to its own default endpoint
    # (api.openai.com for OpenAI, generativelanguage.googleapis.com for Gemini, ...).
    # The CLI overrides this per provider when the user picks one. Keeping a
    # provider-specific URL here would leak (e.g. OpenAI's /v1 was previously
    # being forwarded to Gemini, producing malformed request URLs).
    "backend_url": None,
    # Provider-specific thinking configuration
    "google_thinking_level": None,      # "high", "minimal", etc.
    "openai_reasoning_effort": None,    # "medium", "high", "low"
    "anthropic_effort": None,           # "high", "medium", "low"
    # Sampling temperature, forwarded to every provider when set. None leaves
    # each provider at its own default. Lower values reduce run-to-run
    # variation on models that honor it; reasoning models largely ignore it
    # and no setting makes LLM output bit-identical across runs (see README).
    "temperature": None,
    # Checkpoint/resume: when True, LangGraph saves state after each node
    # so a crashed run can resume from the last successful step.
    "checkpoint_enabled": False,
    # Output language for analyst reports and final decision
    # Internal agent debate stays in English for reasoning quality
    "output_language": "English",
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    "analyst_concurrency_limit": 1,
    # News / data fetching parameters
    # Increase for longer lookback strategies or to broaden macro coverage;
    # decrease to reduce token usage in agent prompts.
    "news_article_limit": 20,             # max articles per ticker (ticker-news)
    "global_news_article_limit": 10,      # max articles for global/macro news
    "global_news_lookback_days": 7,       # macro news lookback window
    # Search queries used by get_global_news for macro headlines. Extend or
    # replace to broaden geographic / sector coverage.
    "global_news_queries": [
        "Federal Reserve interest rates inflation",
        "S&P 500 earnings GDP economic outlook",
        "geopolitical risk trade war sanctions",
        "ECB Bank of England BOJ central bank policy",
        "oil commodities supply chain energy",
    ],
    # Data vendor configuration
    # Category-level configuration (default for all tools in category).
    # The configured value is the exact vendor chain — requests are NOT silently
    # routed to vendors you didn't choose. For ordered fallback, list several,
    # e.g. "yfinance,alpha_vantage". "default" uses all available vendors.
    "data_vendors": {
        "core_stock_apis": "yfinance",       # Options: alpha_vantage, yfinance
        "technical_indicators": "yfinance",  # Options: alpha_vantage, yfinance
        "fundamental_data": "yfinance",      # Options: alpha_vantage, yfinance
        "news_data": "yfinance",             # Options: alpha_vantage, yfinance
        "macro_data": "fred",                # Options: fred (needs FRED_API_KEY)
        "prediction_markets": "polymarket",  # Options: polymarket (keyless)
    },
    # Tool-level configuration (takes precedence over category-level)
    "tool_vendors": {
        # Example: "get_stock_data": "alpha_vantage",  # Override category default
    },
    # Language instruction appended to all agent prompts (empty = English default)
    "language_instruction": "",

    # Benchmark for alpha calculation in the reflection layer.
    # ``benchmark_ticker`` (when set) overrides the suffix map for all
    # tickers; leave it None to use ``benchmark_map`` for auto-detection
    # based on the ticker's exchange suffix. SPY remains the US default
    # so the reflection label keeps reading "Alpha vs SPY" for US tickers
    # while non-US tickers get their regional index automatically.
    "benchmark_ticker": None,
    "benchmark_map": {
        ".NS":  "^NSEI",       # NSE India (Nifty 50)
        ".BO":  "^BSESN",      # BSE India (Sensex)
        ".T":   "^N225",       # Tokyo (Nikkei 225)
        ".HK":  "^HSI",        # Hong Kong (Hang Seng)
        ".L":   "^FTSE",       # London (FTSE 100)
        ".TO":  "^GSPTSE",     # Toronto (TSX Composite)
        ".AX":  "^AXJO",       # Australia (ASX 200)
        ".SS":  "000001.SS",   # Shanghai (SSE Composite)
        ".SZ":  "399001.SZ",   # Shenzhen (SZSE Component)
        "":     "SPY",         # default for US-listed tickers (no suffix)
    },
})
