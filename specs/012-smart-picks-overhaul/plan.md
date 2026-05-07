# Implementation Plan: Smart Picks Overhaul

**Branch**: `012-smart-picks-overhaul` | **Date**: 2026-05-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/012-smart-picks-overhaul/spec.md`

## Summary

Three changes that ship together on one branch but are layered so the P1 slice is shippable on its own:

1. **Redesign the Smart Picks page** so primary columns fit a 1280-px viewport in both LTR and RTL, secondary metrics move into expand-rows / a detail drawer, and a per-engine inline explanation lives one click/hover away from every score.
2. **Add three new engines** — RSI (oscillator), MACD (trend-following crossover), Volatility Regime (regime classifier + score dampener) — each following the existing engine module shape.
3. **Reweight and integrate** the new engines into the combined score, with the volatility-regime engine acting as a dampener that pulls the score toward NEUTRAL during extreme regimes (without inverting the signal direction).

Approach: backend stays close to today's structure (drop three new modules into `backend/app/services/engines/` and extend the orchestrator); UI is reworked in `frontend/src/pages/SmartPicks.tsx` plus a new `frontend/src/components/smart-picks/` directory; engine education content lives in the existing `frontend/src/locales/` i18n files (EN + AR), keyed by engine name.

## Technical Context

**Language/Version**: Python 3.10+ (backend), TypeScript 5.9 (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy, NumPy (backend — all already present); React 19, AntD 6, react-i18next 17, `motion` v11+, Recharts (frontend — all from prior branches)
**Storage**: No schema changes. Smart Picks is computed in-memory on demand; results are not persisted.
**Testing**: Manual verification per `quickstart.md` plus existing lint (`ruff check .`) and frontend `tsc --noEmit` / `eslint`. Unit tests for each new engine (focused on signal direction at known input shapes) since financial-correctness is non-negotiable per constitution principle II.
**Target Platform**: Modern desktop browsers; backend on macOS/Linux.
**Project Type**: Web application (frontend + backend repo). This feature touches both sides.
**Performance Goals**: Smart Picks page first-meaningful-render no slower than baseline (SC-008). Engine pipeline runs the same 50 tickers in roughly the same wall-clock time as today (target: ≤ 10% slowdown after adding 3 engines).
**Constraints**: No breaking API changes (consumers without new-engine awareness still get a usable response). Score determinism preserved — same input → identical output (FR-013/SC-009). Volatility-regime dampening MUST NOT invert signal direction (FR-008). All engine education must exist in EN + AR (FR-004/SC-010).
**Scale/Scope**: 7 → 10 engines. 1 page redesigned. ~10 new functional components. 0 new persistent entities. ~20 new i18n keys (engine name + 3 explanation fields × 10 engines, half of those already exist as labels).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Simplicity First | ✅ Pass | Three new engines follow the existing module shape — no new abstraction. Education text reuses existing i18n. UI redesign keeps the same data flow; only layout changes. |
| II. Correctness Over Speed | ✅ Pass | Each new engine gets focused unit tests. Determinism (FR-013) and the no-invert rule (FR-008) are explicit success criteria. Score arithmetic uses the same int-rounded 0–100 range as today. |
| III. Separation of Concerns | ✅ Pass | Backend computes; frontend renders. Engine education lives in `frontend/src/locales/` i18n (UI concern, never read by backend). API contract is extended, not redesigned. |
| IV. Incremental Delivery | ✅ Pass | 5 stories prioritized; P1 (US1 + US2) is shippable without any new engine. Each engine is independently testable. |
| V. Data Integrity | ✅ Pass | No DB schema changes. No engine modifies persisted state. Existing analysis history is untouched. |

**Gate result**: PASS. No violations to track in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/012-smart-picks-overhaul/
├── plan.md                  # This file
├── research.md              # Phase 0 — engine parameter + dampening + reweight decisions
├── data-model.md            # Phase 1 — Engine Result, Engine Reference, Volatility Regime Tag shapes
├── quickstart.md            # Phase 1 — run + verify (per-story acceptance walkthrough)
├── contracts/
│   ├── engines-api.md       # Phase 1 — extended /api/engines/score and /smart-picks responses
│   └── engine-reference.md  # Phase 1 — i18n key shape for engine education content
└── checklists/
    └── requirements.md      # Spec quality checklist (already created)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── services/
│   │   └── engines/
│   │       ├── __init__.py              # EDIT — add new engines to run_all + extend _compute_combined_score
│   │       ├── rsi.py                   # NEW — RSI(14) Wilder oscillator engine
│   │       ├── macd.py                  # NEW — MACD(12,26,9) crossover engine
│   │       └── volatility_regime.py     # NEW — rolling-stddev regime classifier + dampener
│   └── routers/
│       └── engines.py                   # EDIT (likely no-op — engines dict is open-ended)
└── tests/
    └── services/
        └── engines/
            ├── test_rsi.py              # NEW — known-input cases (oversold, overbought, neutral)
            ├── test_macd.py             # NEW — bullish crossover, bearish crossover, no-cross cases
            ├── test_volatility_regime.py# NEW — calm, normal, elevated, extreme regimes
            └── test_combined_score.py   # NEW — reweighting, dampening, no-invert rule

frontend/
├── src/
│   ├── pages/
│   │   └── SmartPicks.tsx               # EDIT — major rework: column priority, expand-row, drawer mount
│   ├── components/
│   │   └── smart-picks/                 # NEW directory
│   │       ├── PickRow.tsx
│   │       ├── PickRowExpanded.tsx
│   │       ├── EngineCell.tsx
│   │       ├── EngineEducationPopover.tsx
│   │       ├── PickDetailDrawer.tsx
│   │       └── VolatilityBadge.tsx
│   ├── locales/
│   │   ├── en/engines.json              # NEW — engine education content (EN)
│   │   └── ar/engines.json              # NEW — engine education content (AR)
│   └── types/                           # EDIT — extend SmartPick / EngineResult types
└── tsconfig.app.json                    # UNCHANGED
```

**Structure Decision**: Web-application layout. Backend gets three new engines + tests. Frontend gets a new `components/smart-picks/` directory and i18n content. No DB schema changes; no new top-level routes; existing API endpoints get richer payloads.

## Phase 0 — Research

Open questions to resolve in `research.md`:

1. **RSI parameters** — period (14 standard?), smoothing method (Wilder's vs SMA), and how the 0–100 RSI value maps to the engine's 0–100 score (oversold-as-bullish vs RSI-as-momentum).
2. **MACD parameters** — fast/slow/signal periods (12/26/9 standard?), what "score" means for MACD (line vs histogram, crossover proximity), and how to handle insufficient history.
3. **Volatility regime classification** — window (e.g., 30-bar realized vol), thresholds for calm/normal/elevated/extreme, and whether to use percentiles vs absolute thresholds.
4. **Dampening curve** — exact rule that turns a regime tag into a score adjustment that satisfies "moves toward NEUTRAL but never inverts" (FR-008). Linear pull factor? Cap?
5. **Reweighting** — does Monte Carlo stay at 40%, or does the new ensemble distribute differently (e.g., MC 35%, News 25%, Tech-9 40%)?
6. **Engine education location** — frontend i18n vs backend metadata. (Default decision: frontend i18n — keeps backend purely computational and lets translators work in one place; revisit during research.)
7. **UI density strategy** — expand-row vs drawer vs both. (Default decision: expand-row for quick peek + drawer for full detail; reuses existing AntD `Table` capabilities.)

## Phase 1 — Design & Contracts

**Prerequisites**: `research.md` complete.

1. **Entities → `data-model.md`**: Document the four spec entities — Engine Result, Engine Reference, Smart Pick, Volatility Regime Tag — including the new fields the three engines add. Show how Engine Reference is keyed (engine name) and where it lives (frontend i18n).
2. **Contracts**:
   - `contracts/engines-api.md` — extended `GET /api/engines/score/{ticker}` and `GET /api/engines/smart-picks` payload shapes; document that the `engines` dict gains `rsi`, `macd`, `volatility_regime` keys, and the new `combined_score` rules. Backwards compatibility: existing consumers ignore new keys without breakage.
   - `contracts/engine-reference.md` — the i18n key shape for engine education content (`engines.{name}.label`, `engines.{name}.measures`, `engines.{name}.scoreRange`, `engines.{name}.whyMatters`), and the rules for adding a new engine to the catalog.
3. **Quickstart → `quickstart.md`** — step-by-step verification for each user story, including viewport-fit checks, RTL walkthrough, deterministic-score check (run pipeline twice and diff), and the no-invert rule (force extreme regime, confirm score moves toward 50 but stays on the same side).
4. **Agent context update** — run `.specify/scripts/bash/update-agent-context.sh claude` after the artifacts above exist so `CLAUDE.md` records that this branch adds RSI/MACD/Volatility-Regime engines and Smart Picks education content.

**Output**: `research.md`, `data-model.md`, `contracts/engines-api.md`, `contracts/engine-reference.md`, `quickstart.md`, plus regenerated `CLAUDE.md`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. Section intentionally empty.
