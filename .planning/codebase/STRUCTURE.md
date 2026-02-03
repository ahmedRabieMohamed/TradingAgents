# Codebase Structure

**Analysis Date:** 2026-02-03

## Directory Layout

```
[project-root]/
├── assets/                    # Static assets for docs/branding
├── cli/                       # Typer CLI apps, UI, and prompts
├── egyptian_results/          # Generated EGX analysis outputs
├── results/                   # Generated US analysis outputs
├── tradingagents/             # Core Python package
├── tradingagents/api/         # FastAPI API layer (routers, deps, schemas, services)
├── tradingagents.egg-info/    # Packaging metadata
├── main.py                    # Example runner script
├── setup.py                   # Packaging + console entrypoints
├── requirements.txt           # Python dependencies
└── pyproject.toml             # Python project metadata
```

## Directory Purposes

**cli/**
- Purpose: CLI interface for running analyses.
- Contains: Typer apps, Rich UI rendering, Questionary prompts.
- Key files: `cli/main.py`, `cli/egyptian_main.py`, `cli/utils.py`, `cli/models.py`, `cli/static/welcome.txt`.

**tradingagents/**
- Purpose: Core application logic and agent orchestration.
- Contains: Graph orchestration, agent factories, dataflow utilities, configs.
- Key files: `tradingagents/graph/trading_graph.py`, `tradingagents/graph/egyptian_trading_graph.py`, `tradingagents/default_config.py`, `tradingagents/egyptian_config.py`.

**tradingagents/api/**
- Purpose: FastAPI API layer for Market Access & Discovery endpoints.
- Contains: Routers, dependencies, schemas, services, settings, and seed data.
- Key files: `tradingagents/api/app.py`, `tradingagents/api/routers/auth.py`, `tradingagents/api/services/auth_tokens.py`, `tradingagents/api/data/markets.json`.

**tradingagents/graph/**
- Purpose: LangGraph workflow definitions and execution helpers.
- Contains: Graph setup, propagation, conditional logic, reflection, signal processing.
- Key files: `tradingagents/graph/setup.py`, `tradingagents/graph/propagation.py`, `tradingagents/graph/conditional_logic.py`.

**tradingagents/agents/**
- Purpose: LLM agent node implementations.
- Contains: Analyst agents, researchers, risk debators, managers, trader.
- Key files: `tradingagents/agents/analysts/market_analyst.py`, `tradingagents/agents/researchers/bull_researcher.py`, `tradingagents/agents/risk_mgmt/aggresive_debator.py`, `tradingagents/agents/trader/trader.py`, `tradingagents/agents/managers/research_manager.py`.

**tradingagents/agents/utils/**
- Purpose: Shared utilities for agent state, tools, and memory.
- Contains: `Toolkit`, state schema, ChromaDB-backed memory.
- Key files: `tradingagents/agents/utils/agent_utils.py`, `tradingagents/agents/utils/agent_states.py`, `tradingagents/agents/utils/memory.py`.

**tradingagents/dataflows/**
- Purpose: Data retrieval and processing utilities used by tools.
- Contains: News/market/fundamentals fetchers and configs.
- Key files: `tradingagents/dataflows/interface.py`, `tradingagents/dataflows/yfin_utils.py`, `tradingagents/dataflows/finnhub_utils.py`, `tradingagents/dataflows/egyptian_utils.py`.

**results/**
- Purpose: Generated US market analysis outputs.
- Contains: Per-ticker/date report markdown files (e.g., `results/AAPL/2025-09-14/reports/*.md`).

**egyptian_results/**
- Purpose: Generated EGX market analysis outputs.
- Contains: Per-ticker/date report markdown files (e.g., `egyptian_results/COMI/2025-09-14/reports/*.md`).

## Key File Locations

**Entry Points:**
- `cli/main.py`: Primary Typer CLI app (console script `tradingagents` in `setup.py`).
- `cli/egyptian_main.py`: EGX-specific CLI app.
- `main.py`: Example script invoking `TradingAgentsGraph` directly.

**Configuration:**
- `tradingagents/default_config.py`: Default US market runtime config.
- `tradingagents/egyptian_config.py`: EGX market configuration and utilities.

**Core Logic:**
- `tradingagents/graph/trading_graph.py`: Graph orchestration and tool node definitions.
- `tradingagents/graph/setup.py`: LangGraph node/edge wiring.
- `tradingagents/agents/`: Agent node factories for analysts/researchers/risk/trader.
- `tradingagents/dataflows/interface.py`: Data retrieval functions used by tools.

**Testing:**
- `test_egyptian_stocks.py`: Single test module in project root.

## Naming Conventions

**Files:**
- Snake_case Python modules (e.g., `tradingagents/graph/signal_processing.py`).
- Agent factory files use role names (e.g., `tradingagents/agents/analysts/market_analyst.py`).

**Directories:**
- Feature-based subfolders under `tradingagents/agents/` (`analysts/`, `researchers/`, `risk_mgmt/`, `managers/`, `trader/`, `utils/`).
- Pipeline modules under `tradingagents/graph/`.

## Where to Add New Code

**New Analyst/Agent:**
- Implementation: add to `tradingagents/agents/analysts/` (or appropriate role folder).
- Export: update `tradingagents/agents/__init__.py`.
- Graph wiring: register node and tool node in `tradingagents/graph/setup.py` (and `tradingagents/graph/egyptian_trading_graph.py` if EGX-specific).

**New Data Source / Tool:**
- Dataflow logic: add to `tradingagents/dataflows/` (e.g., `tradingagents/dataflows/new_source_utils.py`).
- Tool wrapper: add a `@tool` method in `tradingagents/agents/utils/agent_utils.py`.
- Graph tool nodes: include tool in `TradingAgentsGraph._create_tool_nodes()` in `tradingagents/graph/trading_graph.py`.

**New CLI Command:**
- Implementation: add a new `@app.command()` in `cli/main.py` or `cli/egyptian_main.py`.
- Shared prompt logic: add helpers in `cli/utils.py` if needed.

**Utilities:**
- Shared agent utilities: `tradingagents/agents/utils/`.
- Data transformation helpers: `tradingagents/dataflows/`.

## Special Directories

**tradingagents/dataflows/data_cache/**
- Purpose: Local cache for dataflow outputs.
- Generated: Yes (created in `TradingAgentsGraph.__init__()` in `tradingagents/graph/trading_graph.py`).
- Committed: No.

**results/** and **egyptian_results/**
- Purpose: Generated reports/logs from runs.
- Generated: Yes (created in `cli/main.py` and `cli/egyptian_main.py`).
- Committed: No (output artifacts).

---

*Structure analysis: 2026-02-03*
