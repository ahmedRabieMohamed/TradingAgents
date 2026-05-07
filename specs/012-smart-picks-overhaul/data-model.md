# Phase 1 — Data Model

**Feature**: Smart Picks Overhaul (`012-smart-picks-overhaul`)
**Date**: 2026-05-01

This feature does not introduce persistent entities. Smart Picks runs in-memory; nothing is written to SQLite. The "data model" below documents the in-memory and transport shapes that the spec's Key Entities require.

---

## Entity 1 — Engine Result

The output of a single engine for a single ticker. Same shape across all 10 engines. Lives in the `engines` dict that the orchestrator returns.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `score` | int 0–100 | Yes (when `data_sufficient` is true) | Engine's bullish/bearish view. 50 = neutral, > 50 = bullish, < 50 = bearish. |
| `signal` | string | Yes | One of `STRONG BUY`, `BUY`, `HOLD`, `NEUTRAL`, `SELL`, `STRONG SELL`. Engine's standalone view, not the combined signal. |
| `reason` | string | Yes | One-line plain-English rationale (e.g., "RSI 28 — oversold rebound setup"). |
| `data_sufficient` | bool | Yes | `false` if input bars are too short for this engine's lookbacks. |
| `weight` | float 0.0–1.0 | Yes (when included in the combined score) | The engine's contribution weight in the combined-score blend. Reported per-pick because the weight may shift if other engines are unavailable (FR-010). |

### Engine-specific extensions

Engines may report extra fields that are useful for the UI but are *not* part of the standard contract. These never affect the combined score; they exist only for display.

- `momentum`: `roc_5d`, `roc_20d`
- `volume`: `volume_ratio`
- `monte_carlo`: `probability`, `expected`, `best_case`, `worst_case`
- `support_resistance`: `nearest_support`, `nearest_resistance`
- `bollinger`: `state` (squeeze | breakout-up | breakout-down | normal)
- `mean_reversion`: `pct_above_sma_50`
- `correlation`: `peer_alignment_pct`
- **NEW** `rsi`: `rsi_value` (the raw 0–100 RSI — distinct from the engine `score`)
- **NEW** `macd`: `macd_line`, `signal_line`, `histogram`, `crossover_age_bars`
- **NEW** `volatility_regime`: `realized_vol_annualized`, `regime_tag` (`calm` | `normal` | `elevated` | `extreme`), `pull_alpha` (0.0–1.0 — the dampening factor applied to the combined score)

### Validation rules

- `score` MUST be an int in [0, 100] (0 and 100 are clamps, never NaN).
- `signal` MUST be one of the six allowed values; `engine.score` and `engine.signal` MUST be consistent under the standard score→signal mapping.
- When `data_sufficient` is `false`, `score` and `signal` MAY be omitted; `reason` MUST explain why ("Insufficient bars: needs ≥ 14, got 9.").
- `weight` MUST sum to 1.0 across the engines that contribute to the combined score for a given ticker. Engines with `data_sufficient: false` report `weight: 0.0`.

### State / lifecycle

Engine Results are emitted on demand by the pipeline. They are never persisted. Successive runs on the same input MUST produce identical results (FR-013/SC-009).

---

## Entity 2 — Smart Pick

The full per-ticker output. This is what `GET /api/engines/smart-picks` returns in its `picks[]` array.

| Field | Type | Description |
|-------|------|-------------|
| `ticker` | string | e.g., `"COMI"` |
| `company_name` | string | e.g., `"Commercial International Bank"` |
| `company_name_ar` | string | Arabic name when available |
| `sector` | string | e.g., `"Banking"` |
| `market_id` | string | `"egypt"` or `"us"` |
| `reason` | string | Top-level rationale (`"EGX30 component"` etc.) |
| `combined_score` | int 0–100 | After news weighting AND volatility-regime dampening |
| `combined_score_raw` | int 0–100 | Score *before* dampening (debugging / transparency aid) |
| `signal` | string | Final signal mapped from `combined_score` |
| `bullish_engines` | int | Count of engines (out of `total_engines`) currently signalling bullish |
| `total_engines` | int | Number of engines that contributed (excludes `data_sufficient: false`) |
| `engines` | object | `{name: EngineResult}`. Includes all 10 engine slots — `rsi`, `macd`, `volatility_regime` plus the existing 7. |
| `news_sentiment` | object | `{score, headline_count}` from the news pipeline (unchanged from today) |
| `volatility_regime_tag` | string | Top-level mirror of `engines.volatility_regime.regime_tag` for fast UI access |
| `display_metrics` | object | Convenience fields the table wants without reaching into engines (e.g., `mc_probability`, `mc_expected`, `momentum_roc_5d`) — same fields the current API returns; preserved for backwards compatibility |

### State / lifecycle

Smart Picks are returned to the frontend and not persisted. Refresh re-runs the pipeline.

---

## Entity 3 — Engine Reference

Per-engine educational metadata used by the inline popover and detail drawer. Lives **in frontend i18n only** — never in API responses.

### Storage

- `frontend/src/locales/en/engines.json`
- `frontend/src/locales/ar/engines.json`

### Shape per engine

```json
{
  "rsi": {
    "label": "RSI",
    "category": "Oscillator",
    "measures": "Whether the recent price moves leave the stock oversold or overbought.",
    "scoreRange": "0–30: bullish (oversold). 70–100: bearish (overbought). 40–60: neutral.",
    "whyMatters": "Identifies stretched moves that often snap back. Best paired with a trend signal."
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `label` | string | Yes | Display name shown in the table column header and popover title. Single line. |
| `category` | string | Yes | Short tag (`Oscillator`, `Trend`, `Volume`, `Volatility`, `Statistical`, `Sentiment`). Helps users group similar engines. |
| `measures` | string | Yes | One sentence: what numerical thing does this engine compute? Plain language. |
| `scoreRange` | string | Yes | One or two sentences: how to read the engine's 0–100 score. |
| `whyMatters` | string | Yes | One or two sentences: when is this engine's signal most useful, and what trader-facing decision does it inform? |

### Validation rules

- Every engine name returned in the API's `engines` dict MUST have a corresponding entry in BOTH `en/engines.json` AND `ar/engines.json`. CI / lint checks the symmetry.
- All four text fields MUST be plain language — no jargon a beginner trader couldn't follow (FR-014).
- Both locales' content must convey the same meaning; differences in length are acceptable, factual differences are not.

---

## Entity 4 — Volatility Regime Tag

A coarse classification of the market state for one ticker, emitted by the `volatility_regime` engine.

| Tag | Realized-vol percentile vs. trailing 1-year | Combined-score dampener α |
|-----|---------------------------------------------|---------------------------|
| `calm` | ≤ 25th | 0.00 |
| `normal` | 25th – 75th | 0.00 |
| `elevated` | 75th – 95th | 0.15 |
| `extreme` | > 95th | 0.30 |

### Validation rules

- Tag MUST be one of the four enum values.
- α must come from the table above (deterministic, not a free parameter per ticker).
- The tag is computed once per ticker per pipeline run and cached on the Smart Pick output.

### Lifecycle

Computed on demand inside the `volatility_regime` engine; surfaced both as `engines.volatility_regime.regime_tag` (for the per-engine drawer) and as `volatility_regime_tag` on the Smart Pick (for the pill-badge in the table header).

---

## Relationships

```text
Smart Pick (per ticker)
├── combined_score                ← derived from
│   ├── monte_carlo             ╮
│   ├── news_sentiment          │ weighted blend (R5)
│   └── tech_avg of 8 engines:  │
│       ├── momentum            │
│       ├── volume              │
│       ├── support_resistance  │
│       ├── mean_reversion      │
│       ├── bollinger           │
│       ├── correlation         │
│       ├── rsi (NEW)           │
│       └── macd (NEW)          ╯
│
├── volatility_regime (NEW)
│   └── pulls combined_score toward 50 by α (R4)
│
├── volatility_regime_tag         ← mirror of engines.volatility_regime.regime_tag
│
└── per-engine display fields     ← consumed by Engine Cell + Education Popover
                                   ↑
                                   │
                                   └─ Engine Reference (frontend i18n)
                                       — never travels in API
                                       — keyed by engine name
```

The diagram is one-way: backend produces engine results and combined scores; frontend reads engine references; references never feed back into score computation.
