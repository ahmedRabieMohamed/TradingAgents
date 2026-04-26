# WebSocket API Contract: Analysis Streaming

**Endpoint**: `WS /api/ws/analysis/{session_id}`

## Connection Flow

1. Client creates analysis via `POST /api/analysis` → receives `session_id`
2. Client connects to `WS /api/ws/analysis/{session_id}`
3. Server streams events as the analysis pipeline executes
4. Connection closes when analysis completes, fails, or is cancelled

## Event Types

All messages are JSON with a `type` field.

---

### `agent_started`

Sent when an agent begins execution.

```json
{
  "type": "agent_started",
  "timestamp": "2026-04-04T10:30:05Z",
  "agent_name": "market_analyst",
  "phase": "analyst",
  "description": "Technical indicators, price patterns, volume analysis"
}
```

### `agent_message`

Sent when an agent produces a log message or tool call.

```json
{
  "type": "agent_message",
  "timestamp": "2026-04-04T10:30:08Z",
  "agent_name": "market_analyst",
  "content": "Fetching 30-day price data for AAPL...",
  "message_type": "tool_call"
}
```

`message_type` values: `"info"`, `"tool_call"`, `"tool_result"`, `"thinking"`

### `agent_completed`

Sent when an agent finishes and a report is available.

```json
{
  "type": "agent_completed",
  "timestamp": "2026-04-04T10:30:45Z",
  "agent_name": "market_analyst",
  "phase": "analyst",
  "report_preview": "SMA(20) shows bullish crossover above SMA(50)...",
  "report_full": "## Market Analysis\n\n..."
}
```

### `debate_round`

Sent during bull/bear or risk debate rounds.

```json
{
  "type": "debate_round",
  "timestamp": "2026-04-04T10:32:10Z",
  "debate_type": "investment",
  "round": 1,
  "total_rounds": 3,
  "bull_argument": "Services revenue growing 20% YoY...",
  "bear_argument": "Hardware sales plateauing..."
}
```

For risk debates:
```json
{
  "type": "debate_round",
  "debate_type": "risk",
  "round": 1,
  "aggressive": "Strong buy with 5% position...",
  "neutral": "Moderate buy with 3% position...",
  "conservative": "Small buy with 1.5% position..."
}
```

### `stats_update`

Sent periodically with cumulative statistics.

```json
{
  "type": "stats_update",
  "timestamp": "2026-04-04T10:31:00Z",
  "agents_completed": 2,
  "agents_total": 9,
  "llm_calls": 7,
  "tool_calls": 12,
  "tokens_in": 4800,
  "tokens_out": 2100,
  "reports_generated": 2,
  "elapsed_seconds": 55
}
```

### `analysis_completed`

Sent when the full pipeline finishes successfully.

```json
{
  "type": "analysis_completed",
  "timestamp": "2026-04-04T10:35:42Z",
  "recommendation": "BUY",
  "confidence": 0.85,
  "summary": "Portfolio Manager approved moderate long position. Entry at $205.40..."
}
```

### `analysis_failed`

Sent if the pipeline encounters an unrecoverable error.

```json
{
  "type": "analysis_failed",
  "timestamp": "2026-04-04T10:33:12Z",
  "error": "OpenAI API key is invalid or expired",
  "phase": "analyst",
  "agent_name": "market_analyst"
}
```

### `analysis_cancelled`

Sent if the user cancels the analysis.

```json
{
  "type": "analysis_cancelled",
  "timestamp": "2026-04-04T10:34:00Z"
}
```

---

## Client → Server Messages

### Cancel Analysis

```json
{
  "type": "cancel"
}
```

Server responds with `analysis_cancelled` and closes the connection.

---

## Connection Lifecycle

```
Client                          Server
  |-- WS Connect ------------------>|
  |<-- agent_started (market) ------|
  |<-- agent_message (tool call) ---|
  |<-- agent_message (tool call) ---|
  |<-- stats_update ----------------|
  |<-- agent_completed (market) ----|
  |<-- agent_started (news) --------|
  |           ...                    |
  |<-- debate_round (invest, 1/3) --|
  |<-- debate_round (invest, 2/3) --|
  |<-- debate_round (invest, 3/3) --|
  |           ...                    |
  |<-- analysis_completed ----------|
  |-- WS Close -------------------->|
```

## Reconnection

If the client disconnects during analysis:
- The analysis continues running on the server
- Client can reconnect to the same WebSocket URL
- Server replays the latest `stats_update` and any completed `agent_completed` events
- Streaming resumes from the current point
