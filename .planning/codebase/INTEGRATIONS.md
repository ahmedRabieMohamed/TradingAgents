# External Integrations

**Analysis Date:** 2026-02-03

## APIs & External Services

**LLM Providers:**
- OpenAI API - LLM reasoning + web search tools via OpenAI SDK (`tradingagents/dataflows/interface.py`, `tradingagents/dataflows/egyptian_interface.py`, `tradingagents/agents/utils/memory.py`)
  - SDK/Client: `openai`
  - Auth: `OPENAI_API_KEY` (documented in `README.md`)
- Anthropic API - optional provider through LangChain (`tradingagents/graph/trading_graph.py`, `tradingagents/graph/egyptian_trading_graph.py`)
  - SDK/Client: `langchain-anthropic`
  - Auth: via provider environment variables (configured by SDK)
- Google GenAI API - optional provider through LangChain (`tradingagents/graph/trading_graph.py`, `tradingagents/graph/egyptian_trading_graph.py`)
  - SDK/Client: `langchain-google-genai`
  - Auth: via provider environment variables (configured by SDK)
- OpenRouter/Ollama - optional LLM endpoints via configurable `backend_url` (`tradingagents/default_config.py`, `cli/utils.py`)

**Market Data Providers:**
- Yahoo Finance - online price/metadata lookup (`tradingagents/dataflows/yfin_utils.py`, `tradingagents/dataflows/egyptian_utils.py`, `tradingagents/dataflows/stockstats_utils.py`)
  - SDK/Client: `yfinance`
  - Auth: none
- EODHD - backup data source for Egyptian stocks (`tradingagents/dataflows/egyptian_utils.py`)
  - SDK/Client: direct HTTP via `requests`
  - Auth: API token configured in `EGYPTIAN_CONFIG` (`tradingagents/egyptian_config.py`)
- EODHD - market/symbol discovery and EOD series (`tradingagents/api/services/eodhd_client.py`)
  - SDK/Client: direct HTTP via `requests`
  - Auth: `EODHD_API_KEY` (settings in `tradingagents/api/settings.py`)
- Finnhub - used via cached JSON datasets (not live API calls) (`tradingagents/dataflows/finnhub_utils.py`, `tradingagents/dataflows/interface.py`)
  - SDK/Client: local JSON reads
  - Auth: `FINNHUB_API_KEY` documented for data acquisition (`README.md`)

**News & Web Sources:**
- Google News (web scraping) - Google News search scraping (`tradingagents/dataflows/googlenews_utils.py`)
  - SDK/Client: `requests` + `bs4`
  - Auth: none
- OpenAI Web Search - news/social search through OpenAI tools (`tradingagents/dataflows/interface.py`, `tradingagents/dataflows/egyptian_interface.py`)
  - SDK/Client: `openai` tool `web_search_preview`
  - Auth: `OPENAI_API_KEY`

**Social Sources:**
- Reddit data - uses local JSONL datasets (no live API usage) (`tradingagents/dataflows/reddit_utils.py`, `tradingagents/dataflows/interface.py`)
  - SDK/Client: local filesystem reads
  - Auth: none

## Data Storage

**Databases:**
- ChromaDB (local, in-process vector store) (`tradingagents/agents/utils/memory.py`)
  - Connection: local in-process client
  - Client: `chromadb`

**File Storage:**
- Local filesystem only for cached datasets and results (`tradingagents/default_config.py`, `tradingagents/dataflows/stockstats_utils.py`)
  - Examples: `data_dir/finnhub_data`, `data_dir/fundamental_data`, `data_cache_dir`

**Caching:**
- Local CSV/JSON cache on disk (`tradingagents/dataflows/stockstats_utils.py`, `tradingagents/dataflows/finnhub_utils.py`)

## Authentication & Identity

**Auth Provider:**
- Custom (API keys via environment variables; SDKs read env internally)
  - Implementation: OpenAI/Anthropic/Google SDKs initialized with `backend_url` and env-based credentials (`tradingagents/default_config.py`, `tradingagents/dataflows/interface.py`)

## Monitoring & Observability

**Error Tracking:**
- None detected

**Logs:**
- Console output only (e.g., `print()` in `tradingagents/dataflows/googlenews_utils.py`, `tradingagents/dataflows/egyptian_utils.py`)

## CI/CD & Deployment

**Hosting:**
- Not specified

**CI Pipeline:**
- None detected

## Environment Configuration

**Required env vars:**
- `OPENAI_API_KEY` (LLM + web search) (`README.md`)
- `FINNHUB_API_KEY` (data acquisition for Finnhub datasets) (`README.md`)
- `EODHD_API_KEY` (market/symbol discovery via EODHD) (`tradingagents/api/settings.py`)
- `TRADINGAGENTS_RESULTS_DIR` (optional results path override) (`tradingagents/default_config.py`, `tradingagents/egyptian_config.py`)

**Secrets location:**
- Environment variables (documented in `README.md`)

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- None detected

---

*Integration audit: 2026-02-03*
