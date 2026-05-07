# Contract — Engines API

**Feature**: Smart Picks Overhaul (`012-smart-picks-overhaul`)
**Stability**: Backwards-compatible extension. Existing fields keep their names, types, and meaning. New fields are additive.

This contract documents the changes to the two engine endpoints. Authoritative shape definitions live in `data-model.md`; this document focuses on the wire format and the back-compat rules.

---

## `GET /api/engines/score/{ticker}`

Per-ticker, on-demand engine run.

### Query / path

- `ticker` (path) — string, required
- `market` (query) — `egypt` | `us`, required

### Response (additive changes)

The response keeps its existing top-level shape:

```json
{
  "ticker": "COMI",
  "market_id": "egypt",
  "combined_score": 64,
  "combined_signal": "BUY",
  "engines": { ... },
  "news_sentiment": { ... }
}
```

**New top-level field**:

| Field | Type | Notes |
|-------|------|-------|
| `combined_score_raw` | int 0–100 | The combined score *before* volatility-regime dampening. Equals `combined_score` when regime is `calm` or `normal`. Provided so the UI can show "this score was dampened by N points". |
| `volatility_regime_tag` | string enum | Mirror of `engines.volatility_regime.regime_tag`. Hoisted to the top so the table doesn't need to dig into the engines dict for the badge. |

**Extensions inside the existing `engines` dict**:

Three new keys are added:

| Key | Engine type | New per-engine extras |
|-----|-------------|------------------------|
| `rsi` | Oscillator | `rsi_value` (raw 0–100 RSI) |
| `macd` | Trend / crossover | `macd_line`, `signal_line`, `histogram`, `crossover_age_bars` |
| `volatility_regime` | Regime classifier | `realized_vol_annualized`, `regime_tag` (`calm` \| `normal` \| `elevated` \| `extreme`), `pull_alpha` (0.00 / 0.15 / 0.30) |

All three follow the standard Engine Result shape from `data-model.md` (i.e., `score`, `signal`, `reason`, `data_sufficient`, `weight`).

**Per-engine `weight` semantics**:

- For engines that contribute to the combined-score blend, `weight` reports the actual fractional share they had after redistribution.
- For `volatility_regime`, `weight` is always `0.0` — the engine adjusts the score via dampening, not via the weighted sum. This is documented in the engine reference and surfaced in the UI popover as "this engine adjusts the final score; it doesn't add to it directly".
- For `news_sentiment`, the existing top-level field is unchanged (it is not in the engines dict).

### Insufficient data

Engines may return `data_sufficient: false` when input bars are too short. In that case:

- `score` and `signal` MAY be omitted.
- `weight` is `0.0` for that engine.
- Other engines' weights are renormalized so they sum to 1.0 across the engines that did contribute (FR-010).
- The pick is still returned; it is not dropped because of one missing engine (FR-009 / SC-007).

### Backwards compatibility

A pre-v0.3 client reading the response sees:

- All previous fields with previous values.
- An `engines` dict with three additional keys it can ignore.
- Two new top-level fields it can ignore.
- The `combined_score` value is computed from the new blend AND dampened. A client that only reads `combined_score` will see scores that may differ slightly from before — this is expected and is what SC-005 budgets at ±10 points for 90%+ of tickers.

---

## `GET /api/engines/smart-picks`

Smart Picks discovery + scoring across a market.

### Query

- `market` — `egypt` | `us`, required
- `limit` — int, default 50

### Response (additive changes)

The response keeps its existing shape:

```json
{
  "market_id": "egypt",
  "computed_at": "2026-05-01T12:00:00Z",
  "total_scored": 50,
  "total_failed": 3,
  "picks": [ SmartPick, SmartPick, ... ]
}
```

Per-pick (`picks[i]`) gains the same new fields documented above:

- `combined_score_raw` (int)
- `volatility_regime_tag` (enum string)
- `engines.rsi`, `engines.macd`, `engines.volatility_regime` (objects)

Existing per-pick fields (`bullish_engines`, `total_engines`, `mc_probability`, `mc_expected`, `momentum_score`, …) are unchanged. The numeric values of `bullish_engines` and `total_engines` may shift because the divisor grows from 7 to up to 9 (rsi + macd added; volatility_regime is excluded since it does not vote).

### Backwards compatibility

Same rule as the per-ticker endpoint. Extra keys in `engines`, two new top-level fields, no removed fields.

---

## Determinism (FR-013 / SC-009)

All engines (existing + new) MUST be pure functions of their inputs. Two consecutive calls with the same prices, volumes, dates, and parameters MUST return byte-identical engine outputs. Verification: `quickstart.md` includes a "diff two runs" step that asserts identical JSON.

NumPy operations that depend on iteration order (e.g., `np.unique` without `return_index`) must be deterministic; new engines must avoid any non-deterministic library calls (no random sampling, no thread-pool reductions over float arrays).

---

## Error responses

Existing error shape unchanged. The pipeline continues to return a 200 response with `total_failed > 0` when individual tickers fail; only an outright market-config failure produces a 4xx/5xx.

---

## Versioning note

This is **not** a breaking change. No version bump needed at the API level. Frontend consumers can roll forward at their own pace; older builds will simply ignore the new keys and the new score values will look like a normal recompute.
