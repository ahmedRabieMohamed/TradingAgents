# Technology Stack

**Analysis Date:** 2026-02-03

## Languages

**Primary:**
- Python >=3.10 - core package and CLI (`pyproject.toml`, `setup.py`, `tradingagents/`)

**Secondary:**
- Not detected

## Runtime

**Environment:**
- Python 3.10+ (`pyproject.toml`, `setup.py`)

**Package Manager:**
- pip (requirements file) (`requirements.txt`)
- uv (lockfile present) (`uv.lock`)
- Lockfile: present (`uv.lock`)

## Frameworks

**Core:**
- LangChain - LLM wrappers and prompts (`tradingagents/graph/trading_graph.py`, `tradingagents/agents/utils/agent_utils.py`)
- LangGraph - agent graph orchestration (`tradingagents/graph/trading_graph.py`, `tradingagents/graph/setup.py`)

**Testing:**
- Not detected (no test runner config files found)

**Build/Dev:**
- setuptools - packaging and CLI entry point (`setup.py`)

## Key Dependencies

**Critical:**
- openai - OpenAI client used for web search + embeddings (`tradingagents/dataflows/interface.py`, `tradingagents/dataflows/egyptian_interface.py`, `tradingagents/agents/utils/memory.py`)
- yfinance - market data retrieval (`tradingagents/dataflows/yfin_utils.py`, `tradingagents/dataflows/stockstats_utils.py`, `tradingagents/dataflows/egyptian_utils.py`)
- pandas - data processing (`tradingagents/dataflows/interface.py`, `tradingagents/dataflows/stockstats_utils.py`)
- stockstats - technical indicators (`tradingagents/dataflows/stockstats_utils.py`)
- chromadb - local vector memory store (`tradingagents/agents/utils/memory.py`)

**Infrastructure:**
- requests - HTTP for news scraping and EODHD backup (`tradingagents/dataflows/googlenews_utils.py`, `tradingagents/dataflows/egyptian_utils.py`)
- questionary + rich - CLI prompts and formatting (`cli/utils.py`)

## Configuration

**Environment:**
- Results directory override via `TRADINGAGENTS_RESULTS_DIR` (`tradingagents/default_config.py`, `tradingagents/egyptian_config.py`)
- OpenAI/Finnhub API keys expected via environment variables (documented in `README.md`)
- LLM provider + backend URL configured in `DEFAULT_CONFIG` and `EGYPTIAN_CONFIG` (`tradingagents/default_config.py`, `tradingagents/egyptian_config.py`)

**Build:**
- `pyproject.toml` (dependency list)
- `requirements.txt` (pip install list)
- `setup.py` (package metadata + CLI entry point)

## Platform Requirements

**Development:**
- Local data directory for cached datasets (configured in `tradingagents/default_config.py`, `tradingagents/egyptian_config.py`)
- Internet access for online tools (OpenAI web search, Yahoo Finance, Google News)

**Production:**
- Not specified; runs as a Python package/CLI (`setup.py`, `cli/main.py`)

---

*Stack analysis: 2026-02-03*
