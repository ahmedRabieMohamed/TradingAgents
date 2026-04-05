# Data Model: Trading Web Application

**Feature**: 001-trading-web-app  
**Date**: 2026-04-04

## Entities

### Market

Represents a supported exchange context.

| Field | Type | Constraints |
|-------|------|------------|
| id | string | "us" or "egypt" — primary key |
| name | string | Display name (e.g., "US Market", "Egypt Market") |
| exchange | string | Exchange code (e.g., "NYSE/NASDAQ", "EGX") |
| currency | string | Currency code (e.g., "USD", "EGP") |
| trading_days | list[string] | Weekdays when market is open |
| ticker_suffix | string | Suffix applied to tickers (e.g., ".CA" for EGX, "" for US) |

**Notes**: Static/config data. Derived from existing `MARKET_REGIONS` in `default_config.py`. No database storage needed — loaded from config at startup.

---

### AnalysisSession

A single execution of the multi-agent analysis pipeline.

| Field | Type | Constraints |
|-------|------|------------|
| id | string (UUID) | Primary key, auto-generated |
| ticker | string | Stock ticker symbol (e.g., "AAPL", "COMI") |
| market_id | string | Foreign key → Market.id |
| analysis_date | date | The date for which the analysis is performed |
| created_at | datetime | When the analysis was initiated |
| completed_at | datetime | Nullable — set when analysis finishes |
| status | enum | "pending", "running", "completed", "failed", "cancelled" |
| trade_horizon | enum | "intraday", "short-term", "medium-term", "long-term" |
| research_depth | enum | "shallow", "medium", "deep" |
| analysts | list[string] | Selected analysts: ["market", "social", "news", "fundamentals"] |
| llm_provider | string | Provider name (e.g., "openai", "anthropic") |
| quick_think_model | string | Model ID for quick tasks |
| deep_think_model | string | Model ID for deep reasoning |
| recommendation | string | Nullable — "BUY", "SELL", or "HOLD" |
| confidence | float | Nullable — 0.0 to 1.0 (displayed as percentage) |
| reports_path | string | File path to the saved reports directory |
| stock_name | string | Resolved stock name (e.g., "Apple Inc.") |
| stock_price_at_analysis | float | Stock price at analysis time |

**Relationships**: Has many AgentReports. Has one optional SimulationResult.

**State Transitions**:
```
pending → running → completed
                  → failed
         → cancelled
```

---

### AgentReport

An individual output from one stage of the analysis pipeline.

| Field | Type | Constraints |
|-------|------|------------|
| id | string (UUID) | Primary key |
| session_id | string | Foreign key → AnalysisSession.id |
| agent_name | string | Agent identifier (e.g., "market_analyst", "bull_researcher") |
| phase | string | Pipeline phase: "analyst", "research", "trading", "risk", "portfolio" |
| content | text | Full report content (Markdown) |
| created_at | datetime | When this report was generated |
| sequence | integer | Order within the session (1-based) |

**Notes**: Content stored in-memory during analysis and written to disk as Markdown. SQLite stores metadata for querying; full content read from disk on demand.

---

### SimulationResult

Tracks how a past recommendation performed against actual market data.

| Field | Type | Constraints |
|-------|------|------------|
| id | string (UUID) | Primary key |
| session_id | string | Foreign key → AnalysisSession.id (unique) |
| entry_price | float | Stock price at analysis date |
| exit_price | float | Stock price at end of trade horizon |
| horizon_end_date | date | Date when the trade horizon ended |
| return_pct | float | Calculated return: (exit - entry) / entry * 100 |
| is_win | boolean | True if return direction matches recommendation |
| simulated_at | datetime | When the simulation was computed |

**Notes**: Computed lazily — when a user views a past analysis whose trade horizon has elapsed. Exit price fetched from market data at that time.

---

### UserSettings

User's persistent configuration preferences.

| Field | Type | Constraints |
|-------|------|------------|
| key | string | Setting key (primary key) |
| value | string | JSON-encoded value |

**Notes**: Key-value store for API keys, default market, default horizon, etc. Single-user app so no user_id needed.

---

## Relationships

```
Market (1) ←——— (many) AnalysisSession
AnalysisSession (1) ←——— (many) AgentReport
AnalysisSession (1) ←——— (0..1) SimulationResult
```

## Validation Rules

- **AnalysisSession.ticker**: Non-empty string, alphanumeric, max 10 characters
- **AnalysisSession.analysts**: At least one analyst must be selected
- **AnalysisSession.analysis_date**: Cannot be in the future; must be a valid trading day for the selected market
- **AnalysisSession.confidence**: Between 0.0 and 1.0 inclusive, nullable until analysis completes
- **SimulationResult.return_pct**: Calculated field, not user-input
- **UserSettings.key**: Must be from a known set of valid setting keys (API keys, defaults)
