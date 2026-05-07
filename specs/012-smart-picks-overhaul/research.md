# Phase 0 — Research

**Feature**: Smart Picks Overhaul (`012-smart-picks-overhaul`)
**Date**: 2026-05-01

This document closes every open question listed in `plan.md` so Phase 1 (data model + contracts) can proceed without `NEEDS CLARIFICATION` markers.

---

## R1. RSI engine parameters and score mapping

**Decision**: RSI(14) using **Wilder's smoothing** (the canonical Welles Wilder formulation). The engine's 0–100 score is **mean-reversion-flavored**, not raw momentum:

- RSI in [0, 30] → **bullish** (oversold; score ≈ 70–85)
- RSI in [70, 100] → **bearish** (overbought; score ≈ 15–30)
- RSI in [40, 60] → **neutral** (score ≈ 50)
- Linear interpolation in the gaps.

**Rationale**:
- 14 periods is the universal default; deviating would surprise traders and complicate the education text.
- Wilder's smoothing matches what stockstats / TA-Lib / TradingView produce, so a value computed here matches what users would see elsewhere.
- The mean-reversion mapping (oversold → bullish) is the most common interpretive convention in trading-screen tools and complements (rather than duplicates) the existing momentum engine, which already captures rate-of-change.

**Alternatives considered**:
- **RSI as raw momentum** (high RSI → high score) — rejected because it would correlate too strongly with the existing momentum engine.
- **RSI(7) or RSI(21)** — rejected; default is the right v1 choice. Period sweeps belong in a follow-up.

---

## R2. MACD engine parameters and score mapping

**Decision**: MACD(12, 26, 9) — fast EMA 12, slow EMA 26, signal-line EMA 9 of the MACD line. The 0–100 score combines:

1. **Crossover state** (50% weight inside the engine): bullish if MACD > signal line, bearish if MACD < signal.
2. **Histogram strength** (50% weight): the magnitude of MACD − signal, normalized by recent absolute-histogram standard deviation, clamped to ±2σ.

A bullish crossover within the last 1–3 bars boosts the score by an additional +5 (capped at 100). A fresh bearish crossover symmetrically subtracts 5.

**Rationale**:
- 12/26/9 is the universal default.
- Combining state and strength gives a dense 0–100 distribution (raw "is MACD above signal" is binary, which is too coarse).
- The "fresh crossover" boost rewards timeliness without dominating the score.

**Alternatives considered**:
- **Pure crossover** — rejected; binary signal hurts ensemble averaging.
- **Histogram-only** — rejected; loses the directional clarity that traders rely on for MACD.

**Insufficient-history rule**: if the input has < 35 bars (slow EMA needs ~26 + signal-line lookback ~9), the engine returns `data_sufficient: False` with no score and is excluded from the combined score for that ticker (FR-009/FR-010).

---

## R3. Volatility-regime engine: classification

**Decision**: Compute **30-bar realized volatility** (annualized standard deviation of daily log returns). Compare against per-market historical percentiles to assign one of four regime tags:

| Regime | Realized vol percentile vs. trailing 1-year history |
|--------|-----------------------------------------------------|
| `calm` | ≤ 25th |
| `normal` | 25th – 75th |
| `elevated` | 75th – 95th |
| `extreme` | > 95th |

The engine returns `regime` (tag) plus a `vol_score` 0–100 for display (low vol → high vol_score signals stability), but the engine **does not contribute its own score directly to the combined number** — instead it acts as a dampener (R4).

**Rationale**:
- 30-bar window matches typical "1-month realized vol" intuition.
- Percentile thresholds are **per-market-relative** so they self-tune to the market's natural volatility (EGX behaves differently from US large caps).
- A 4-tag classification is enough to drive a coarse dampener; finer grain would be hard for a trader to reason about.

**Alternatives considered**:
- **Absolute thresholds** (e.g., > 30% annualized = extreme) — rejected because they don't transfer between markets.
- **GARCH** — rejected on simplicity; realized stddev is sufficient for v1 dampening.

**Insufficient-history rule**: if < 60 bars are available (need 30 for current vol + ~30 for percentile context), regime defaults to `normal` and dampening is a no-op for that ticker.

---

## R4. Dampening curve (the no-invert rule)

**Decision**: The combined score (0–100) is **pulled toward 50** by a regime-dependent factor `α`:

```
adjusted = 50 + (raw - 50) * (1 - α)
```

| Regime | α (pull strength) |
|--------|-------------------|
| `calm` | 0.00 (no change) |
| `normal` | 0.00 |
| `elevated` | 0.15 |
| `extreme` | 0.30 |

The adjusted score is then re-clamped to [0, 100] and re-mapped to the existing signal thresholds (`STRONG BUY` ≥ 75, `BUY` ≥ 65, `HOLD` ≥ 55, `NEUTRAL` ≥ 45, `SELL` < 45, `STRONG SELL` ≤ 25).

**Why this satisfies FR-008 (no inversion)**:
- The pull is **always toward 50**, never past it. A raw score of 80 in extreme vol becomes `50 + 30 × 0.7 = 71`, which is still BUY territory. A raw score of 20 becomes `50 - 30 × 0.7 = 29`, still SELL territory.
- The signal direction (above/below 50) is invariant under this transformation. **Mathematically: `sign(adjusted - 50) = sign(raw - 50) × (1 - α) ⇒ same sign for any α < 1`.**

**Worst-case dampening** (α = 0.30 in `extreme` regime): a STRONG BUY at 76 collapses to `50 + 26 × 0.7 = 68.2 → BUY`. The signal weakens by exactly one tier — desirable behavior for risk-on conditions.

**Rationale**:
- A linear pull is the simplest rule that provably never inverts.
- The 0.15 / 0.30 coefficients are conservative: in elevated vol traders should be slightly more cautious; in extreme vol, decidedly so. They can be tuned later without affecting the structure.

**Alternatives considered**:
- **Multiplicative dampening on the raw score directly** (e.g., raw × 0.7) — rejected; this pulls toward 0, not 50, and could invert SELL signals into NEUTRAL.
- **Hard cap on signal tier** (e.g., never STRONG BUY in extreme regime) — rejected; opaque and harder to explain.

---

## R5. Reweighting the combined score

**Decision**: Two-step combination. First compute the **technical average** across the 8 non-Monte-Carlo, non-news engines (existing 6: momentum, volume, support/resistance, mean reversion, bollinger, correlation; new 2 that contribute scores: rsi, macd). Then combine:

| Component | Weight (with news) | Weight (no news) |
|-----------|--------------------|------------------|
| Monte Carlo | 40% | 55% |
| News sentiment | 30% | — |
| Technical average (8 engines) | 30% | 45% |

Then apply the volatility-regime dampener from R4.

**Rationale**:
- Top-level weights stay identical to today's. Stability of the blend is preserved (SC-005 is achievable: most tickers shift ≤ ±10 points).
- Adding RSI and MACD into the technical average lets them participate without forcing changes to news / MC weighting.
- Volatility regime is treated structurally separately — it doesn't get a slot in the weighted sum because dampening is a different operation from contribution.

**Alternatives considered**:
- **Promote MACD into a fourth top-level term** — rejected; would change MC and News weights and likely shift many existing scores by > ±10 points (violates SC-005 calibration goal).
- **Equal-weight across all 9 scoring engines** — rejected; throws away the deliberate emphasis on Monte Carlo's forward-looking signal.

---

## R6. Engine education location: backend metadata or frontend i18n?

**Decision**: **Frontend i18n** (`frontend/src/locales/{en,ar}/engines.json`). Backend never returns engine education text.

**Rationale**:
- Engine text is a UI concern. Backend already runs in one language (English log lines, Arabic-agnostic code). Putting Arabic translations in the backend forces a backend redeploy for a typo fix.
- react-i18next is already wired and covers the rest of the app — adding new keys is a one-line change.
- Backend payload stays small and language-agnostic; the same response serves every locale.

**Alternatives considered**:
- **Backend metadata endpoint** (`GET /api/engines/reference`) returning per-engine descriptions in the requested locale — rejected; adds an endpoint, version-skew risk between backend metadata and the actual engine algorithm, more moving parts.
- **Static markdown docs** — rejected for inline-tooltip use case (would require fetching/parsing docs at hover-time). Could exist *in addition* as a long-form reference but isn't the right answer for the popover UI.

**Implication**: each new engine added must include i18n keys in both `en/engines.json` and `ar/engines.json` — checked by an item in the per-engine task list during `/speckit-tasks`.

---

## R7. UI density strategy: expand-row vs detail drawer

**Decision**: Use **both**, layered by intent.

- **Primary table** (always visible): rank, ticker (+ company), market, signal badge, combined score, volatility-regime badge, "expand" toggle. Fits a 1280px viewport without horizontal scroll.
- **Expand-row** (one click on the row): existing secondary metrics (MC probability, expected return, momentum ROC, individual engine score chips, "why" reason). Stays inline; the trader can compare two picks side-by-side without losing context.
- **Detail drawer** (click a "Details" link inside expanded row, or click ticker): full per-pick view with all 10 engines listed, weight contributions to the combined score, full rationale text, links to the per-engine education popover.

**Rationale**:
- Three tiers of progressive disclosure cover all spec acceptance scenarios:
  - Story 1 (clean table) — primary table is intentionally sparse.
  - Story 2 (inline education) — popover triggered from any engine chip in the expanded row or drawer.
  - Story 5 (transparency drill-down) — drawer.
- AntD `Table` already supports `expandable` natively, and `Drawer` / `Popover` are first-class components — no new component library required.

**Alternatives considered**:
- **Single drawer, no expand-row** — rejected; the trader loses the ability to scan multiple picks' detail simultaneously.
- **Always-expanded rows (no toggle)** — rejected; defeats the goal of a clean primary table.
- **Modal instead of drawer** — rejected; a modal blocks the underlying table, which makes "compare to next pick" impossible without re-navigating.

---

## Summary of decisions

| Question | Decision |
|----------|----------|
| RSI parameters / mapping | RSI(14) Wilder; oversold→bullish piecewise-linear map |
| MACD parameters / mapping | MACD(12,26,9); 50/50 state + histogram-strength score; fresh-crossover ±5 |
| Volatility regime classification | 30-bar realized vol; per-market percentile thresholds (4 tags) |
| Dampening curve | Linear pull toward 50 with α ∈ {0, 0.15, 0.30}; never inverts |
| Reweighting | MC 40 / News 30 / Tech-avg-of-8 30 (no-news: 55/45) |
| Engine education location | Frontend i18n (`locales/{en,ar}/engines.json`) |
| UI density | Primary table + expand-row + detail drawer |

All `NEEDS CLARIFICATION` items from the Technical Context are resolved. Ready for Phase 1.
