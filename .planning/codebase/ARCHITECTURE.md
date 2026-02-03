# Architecture

**Analysis Date:** 2026-02-03

## Pattern Overview

**Overall:** LangGraph state-machine orchestration of LLM agent teams (analysts → researchers → trader → risk)

**Key Characteristics:**
- Orchestrates agents as nodes in a `langgraph` `StateGraph` with explicit conditional edges in `tradingagents/graph/setup.py`.
- Central shared state (`AgentState`) carries reports and debate state across nodes in `tradingagents/agents/utils/agent_states.py`.
- Tool-augmented analysts call dataflow utilities via `ToolNode` wrappers in `tradingagents/graph/trading_graph.py` and `tradingagents/agents/utils/agent_utils.py`.

## Layers

**CLI Interface:**
- Purpose: Collect user inputs, configure runs, render live progress, and persist reports/logs.
- Location: `cli/`
- Contains: Typer apps, Rich UI, Questionary prompts.
- Depends on: `tradingagents.graph` classes and configs (`tradingagents/default_config.py`, `tradingagents/egyptian_config.py`).
- Used by: Console entrypoint in `setup.py` and direct script execution (`cli/main.py`, `cli/egyptian_main.py`).

**Graph Orchestration:**
- Purpose: Build and execute the LangGraph workflow and invoke agents/tools.
- Location: `tradingagents/graph/`
- Contains: `TradingAgentsGraph`, `EgyptianTradingAgentsGraph`, `GraphSetup`, `EgyptianGraphSetup`, `Propagator`, `ConditionalLogic`.
- Depends on: `tradingagents/agents/*`, `tradingagents/dataflows/interface.py` (via `Toolkit`), LangGraph.
- Used by: CLI (`cli/main.py`, `cli/egyptian_main.py`) and example runner (`main.py`).

**Agent Nodes:**
- Purpose: LLM prompts that generate reports and decisions (analysts, researchers, trader, risk managers).
- Location: `tradingagents/agents/`
- Contains: analyst factories like `tradingagents/agents/analysts/market_analyst.py`, managers like `tradingagents/agents/managers/research_manager.py`, trader `tradingagents/agents/trader/trader.py`, risk debators in `tradingagents/agents/risk_mgmt/*.py`.
- Depends on: `Toolkit` tools and `FinancialSituationMemory`.
- Used by: `GraphSetup` and `EgyptianGraphSetup`.

**Dataflows & Tools:**
- Purpose: Fetch market/news/fundamentals data and expose them as LangChain tools.
- Location: `tradingagents/dataflows/` and `tradingagents/agents/utils/agent_utils.py`.
- Contains: data fetching functions (`tradingagents/dataflows/interface.py`) and tool wrappers (`Toolkit` in `tradingagents/agents/utils/agent_utils.py`).
- Depends on: external data libraries (e.g., yfinance) and config (`tradingagents/dataflows/config.py`).
- Used by: Analyst nodes through `ToolNode`.

**Memory & Reflection:**
- Purpose: Persist and retrieve past situations for improved decision-making.
- Location: `tradingagents/agents/utils/memory.py`, `tradingagents/graph/reflection.py`.
- Contains: ChromaDB-backed memory, reflection prompts.
- Depends on: OpenAI embeddings and ChromaDB client.
- Used by: Research manager and trader nodes, and optional `TradingAgentsGraph.reflect_and_remember()`.

## Data Flow

**CLI Analysis Run:**

1. User selections captured in `cli/utils.py` and `cli/models.py`.
2. Configuration assembled in `cli/main.py` (or `cli/egyptian_main.py`) using `tradingagents/default_config.py` or `tradingagents/egyptian_config.py`.
3. Graph initialized (`TradingAgentsGraph` in `tradingagents/graph/trading_graph.py` or `EgyptianTradingAgentsGraph` in `tradingagents/graph/egyptian_trading_graph.py`).
4. Initial state built by `Propagator.create_initial_state()` in `tradingagents/graph/propagation.py`.
5. LangGraph stream executes nodes compiled in `GraphSetup.setup_graph()` (`tradingagents/graph/setup.py`) or `EgyptianGraphSetup.setup_graph()` (`tradingagents/graph/egyptian_trading_graph.py`).
6. Analyst nodes call `ToolNode`s defined in `tradingagents/graph/trading_graph.py` or `tradingagents/graph/egyptian_trading_graph.py`, which invoke `Toolkit` tools in `tradingagents/agents/utils/agent_utils.py` backed by `tradingagents/dataflows/interface.py`.
7. Debate → trader → risk nodes update `investment_debate_state`, `trader_investment_plan`, and `risk_debate_state` in `AgentState` (`tradingagents/agents/utils/agent_states.py`).
8. Final decision extracted by `SignalProcessor.process_signal()` in `tradingagents/graph/signal_processing.py`.
9. CLI writes reports/logs to `results/` or `egyptian_results/` (`cli/main.py`). Graphs persist full state logs in `eval_results/` or `egyptian_results/` (`TradingAgentsGraph._log_state()` and `EgyptianTradingAgentsGraph._log_state()`).

**Reflection Loop (Optional):**

1. Call `TradingAgentsGraph.reflect_and_remember()` or `EgyptianTradingAgentsGraph.reflect_and_remember()`.
2. `Reflector` in `tradingagents/graph/reflection.py` generates analysis and stores into `FinancialSituationMemory` in `tradingagents/agents/utils/memory.py`.

**State Management:**
- Single shared `AgentState` dict (TypedDict) lives in `tradingagents/agents/utils/agent_states.py` and is mutated by nodes.
- Egyptian flow maps market-specific report names to standard fields using `create_egyptian_state_mapper()` in `tradingagents/graph/egyptian_trading_graph.py`.

## Key Abstractions

**TradingAgentsGraph:**
- Purpose: Orchestrates US-market graph lifecycle and state logging.
- Examples: `tradingagents/graph/trading_graph.py`.
- Pattern: Facade over LangGraph setup + propagation + signal processing.

**EgyptianTradingAgentsGraph:**
- Purpose: Orchestrates EGX market flow with specialized toolkit and state mapping.
- Examples: `tradingagents/graph/egyptian_trading_graph.py`.
- Pattern: Parallel graph implementation mirroring US flow with mapping layer.

**GraphSetup / EgyptianGraphSetup:**
- Purpose: Define nodes and edges of the LangGraph workflow.
- Examples: `tradingagents/graph/setup.py`, `tradingagents/graph/egyptian_trading_graph.py`.
- Pattern: Builder with conditional edges via `ConditionalLogic`.

**Toolkit:**
- Purpose: Expose dataflow functions as LangChain tools.
- Examples: `tradingagents/agents/utils/agent_utils.py`.
- Pattern: `@tool`-decorated static methods used by `ToolNode`.

**AgentState:**
- Purpose: Shared state schema between nodes.
- Examples: `tradingagents/agents/utils/agent_states.py`.
- Pattern: `TypedDict` extending `MessagesState`.

## Entry Points

**CLI App:**
- Location: `cli/main.py`
- Triggers: `tradingagents` console script defined in `setup.py` (`tradingagents=cli.main:app`).
- Responsibilities: User prompts, config selection, run orchestration, live UI, report persistence.

**Egyptian CLI App:**
- Location: `cli/egyptian_main.py`
- Triggers: Direct module execution or external script.
- Responsibilities: EGX-specific CLI flows and reports.

**Example Runner:**
- Location: `main.py`
- Triggers: `python main.py`
- Responsibilities: Simple example of graph execution with custom config.

## Error Handling

**Strategy:** Propagate exceptions to CLI and terminate with Typer exits; validate analyst selection and dates before graph execution.

**Patterns:**
- Guard clauses and `ValueError` in graph setup (`tradingagents/graph/setup.py`, `tradingagents/graph/egyptian_trading_graph.py`).
- CLI input validation with `typer.Exit` in `cli/egyptian_main.py` and interactive validation in `cli/utils.py`.

## Cross-Cutting Concerns

**Logging:**
- State logging to JSON in `TradingAgentsGraph._log_state()` (`tradingagents/graph/trading_graph.py`) and `EgyptianTradingAgentsGraph._log_state()` (`tradingagents/graph/egyptian_trading_graph.py`).
- CLI run-time logs stored in `message_tool.log` via decorators in `cli/main.py`.

**Validation:**
- Analyst selection and dates validated in `cli/utils.py` and `cli/egyptian_main.py`.

**Authentication:**
- LLM providers configured via `DEFAULT_CONFIG` and `EGYPTIAN_CONFIG` (`tradingagents/default_config.py`, `tradingagents/egyptian_config.py`).
- API clients instantiated in dataflows (`tradingagents/dataflows/interface.py`) and memory (`tradingagents/agents/utils/memory.py`).

---

*Architecture analysis: 2026-02-03*
