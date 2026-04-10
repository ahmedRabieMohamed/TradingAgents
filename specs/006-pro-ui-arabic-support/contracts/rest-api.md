# API Contract Changes: 006 — Professional UI Redesign & Arabic/English Bilingual Support

**Date**: 2026-04-10

## Modified Endpoints

### POST /api/analysis — Create Analysis

**Change**: Add optional `language` field to request body.

**Request body** (additions only):

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `language` | string | No | `"en"` | Language for AI agent reports. Values: `"en"`, `"ar"` |

**Example request** (Arabic):
```json
{
  "ticker": "JUFO",
  "market_id": "egypt",
  "analysis_date": "2026-04-10",
  "trade_horizon": "short-term",
  "language": "ar",
  "...": "other existing fields unchanged"
}
```

**Response**: No changes. The `session_id` and `websocket_url` remain the same.

**Backward compatibility**: Field is optional with default `"en"`. Existing clients that don't send `language` continue to work identically.

### GET /api/analysis/{session_id} — Get Analysis Detail

**Change**: Include `language` in response.

**Response body** (additions only):

| Field | Type | Description |
|-------|------|-------------|
| `language` | string | Language the analysis was generated in (`"en"` or `"ar"`) |

**Example response** (partial):
```json
{
  "id": "abc-123",
  "ticker": "JUFO",
  "language": "ar",
  "reports": [
    {
      "agent_name": "Market Analyst",
      "content": "## تحليل سوق سهم JUFO\n..."
    }
  ]
}
```

### GET /api/analysis — List Analyses

**Change**: Add optional `language` query filter.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `language` | string | No | Filter by analysis language (`"en"`, `"ar"`) |

### WS /api/analysis/ws/{session_id} — WebSocket Stream

**Change**: No protocol changes. Agent messages stream in whichever language the analysis was created with. The `content` field of `agent_report` events will contain Arabic text when `language=ar`.

## No Changes

All other endpoints remain unchanged:
- `DELETE /api/analysis/{session_id}`
- `PATCH /api/analysis/{session_id}/notes`
- `POST /api/analysis/{session_id}/simulate`
- `GET /api/analysis/{session_id}/export`
- All `/api/stocks/*` endpoints
- All `/api/watchlist/*` endpoints
- All `/api/portfolio/*` endpoints
