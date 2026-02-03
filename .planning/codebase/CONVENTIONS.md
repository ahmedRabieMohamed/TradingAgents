# Coding Conventions

**Analysis Date:** 2026-02-03

## Naming Patterns

**Files:**
- Use `snake_case.py` for modules (e.g., `tradingagents/graph/trading_graph.py`, `tradingagents/agents/utils/agent_utils.py`).

**Functions:**
- Use `snake_case` for functions and methods (e.g., `create_market_analyst` in `tradingagents/agents/analysts/market_analyst.py`, `process_signal` in `tradingagents/graph/trading_graph.py`).

**Variables:**
- Use `snake_case` for locals and attributes (e.g., `selected_analysts`, `message_buffer` in `cli/main.py`).

**Types:**
- Use `CamelCase` for classes and type aliases (e.g., `TradingAgentsGraph` in `tradingagents/graph/trading_graph.py`, `FinancialSituationMemory` in `tradingagents/agents/utils/memory.py`).
- Use `UPPER_SNAKE_CASE` for module-level constants (e.g., `DEFAULT_CONFIG` in `tradingagents/default_config.py`, `EGYPTIAN_CONFIG` in `tradingagents/egyptian_config.py`).

## Code Style

**Formatting:**
- Tool used: Not detected (no `.prettierrc*`, `pyproject.toml` tool section, or formatter config).
- Use standard PEP 8 styling by default.

**Linting:**
- Tool used: Not detected (no `ruff.toml`, `.flake8`, or `pyproject.toml` lint sections).

## Import Organization

**Order:**
1. Standard library imports (e.g., `import os`, `from datetime import date` in `tradingagents/graph/trading_graph.py`).
2. Third-party libraries (e.g., `from langchain_openai import ChatOpenAI` in `tradingagents/graph/trading_graph.py`).
3. Internal modules (e.g., `from tradingagents.default_config import DEFAULT_CONFIG` in `tradingagents/graph/trading_graph.py`).
4. Relative imports for same package (e.g., `from .setup import GraphSetup` in `tradingagents/graph/trading_graph.py`).

**Path Aliases:**
- Not detected; use absolute package imports from `tradingagents.*` and `cli.*` (e.g., `from tradingagents.graph.trading_graph import TradingAgentsGraph` in `main.py`, `from cli.utils import *` in `cli/main.py`).

## Error Handling

**Patterns:**
- Use explicit `try/except` blocks with user-facing output in scripts (e.g., `test_egyptian_stocks.py`).
- Raise explicit exceptions for unsupported options (e.g., `raise ValueError` in `tradingagents/graph/trading_graph.py`).

## Logging

**Framework:** `print` and `rich` console output.

**Patterns:**
- Use `print` for script/test output (e.g., `test_egyptian_stocks.py`).
- Use Rich UI components for CLI output (e.g., `Console`, `Panel` in `cli/main.py`).

## Comments

**When to Comment:**
- Use docstrings for module/class/function descriptions (e.g., `TradingAgentsGraph` docstring in `tradingagents/graph/trading_graph.py`).
- Use inline comments to explain steps in scripts and workflows (e.g., `cli/main.py`, `test_egyptian_stocks.py`).

**JSDoc/TSDoc:**
- Not applicable (Python codebase; uses Python docstrings instead).

## Function Design

**Size:**
- Prefer small single-purpose functions in analyst/tool modules (e.g., `create_market_analyst` in `tradingagents/agents/analysts/market_analyst.py`).
- CLI orchestration can be long-form; keep helper functions for reusable blocks (e.g., `create_layout`, `update_display` in `cli/main.py`).

**Parameters:**
- Use explicit parameters with descriptive names and, when used, `typing.Annotated` for tool argument metadata (e.g., `get_YFin_data` in `tradingagents/agents/utils/agent_utils.py`).

**Return Values:**
- Return dictionaries for graph state updates (e.g., `create_market_analyst` returns `{"messages": ..., "market_report": ...}` in `tradingagents/agents/analysts/market_analyst.py`).

## Module Design

**Exports:**
- Use explicit exports through package `__init__.py` and `__all__` for public API (e.g., `tradingagents/agents/__init__.py`).

**Barrel Files:**
- Use package-level barrel in `tradingagents/agents/__init__.py` and import with `from tradingagents.agents import *` in `tradingagents/graph/trading_graph.py`.

---

*Convention analysis: 2026-02-03*
