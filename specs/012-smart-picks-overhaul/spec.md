# Feature Specification: Smart Picks Overhaul — More Engines, Better UX, Explainable Scoring

**Feature Branch**: `012-smart-picks-overhaul`
**Created**: 2026-05-01
**Status**: Draft
**Input**: User description: "we need to add more engines, and enhance smart Pick page (poor UX and UI). User must know the differences between each engine and what it exactly does, and why it's important. The new engines should be integrated with the others and the scoring system."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Redesigned Smart Picks Page (Priority: P1)

A trader opens the Smart Picks page and sees a clean, scannable layout. The most important columns (rank, ticker, signal, score) are visible without horizontal scrolling on a typical desktop screen; secondary metrics are accessible through column reveal, expand-row, or detail drill-down. The page conveys what's actually picked and why at a glance, instead of an overwhelming wall of numbers.

**Why this priority**: This is the user's primary complaint ("it's poor UX and UI") and it's the only path to making the rest of Smart Picks usable. Even a perfect engine can't help a trader who can't read the screen. Independent of any new engine work.

**Independent Test**: Open the Smart Picks page on a 1280×800 viewport in both LTR (English) and RTL (Arabic). Confirm: (a) primary columns fit without horizontal scrollbars on the page itself, (b) every existing pick still appears with all current data accessible (via columns, hover, or expand), (c) the layout feels finished rather than cramped or overflowing.

**Acceptance Scenarios**:

1. **Given** the Smart Picks page on a 1280×800 desktop viewport in LTR, **When** the page loads, **Then** the rank, ticker, company, signal, and combined score are visible without page-level horizontal scroll, and the sidebar remains visible.
2. **Given** the Smart Picks page in RTL (Arabic), **When** the page loads, **Then** the layout mirrors correctly without overflow, and all data still renders.
3. **Given** the Smart Picks page with the current set of picks, **When** the trader inspects each row, **Then** every metric available pre-redesign is still reachable (visible directly, behind a tooltip/expand, or in a detail panel) — no data is lost.

---

### User Story 2 - Per-Engine Education Inline ("What does this engine do, and why does it matter?") (Priority: P1)

When a trader sees a score from a specific engine — for example "Momentum 72" or "Mean Reversion 41" — they can instantly find out what that engine measures, what a high vs low score means, and why the engine matters for a trading decision. The information is one click/hover away from where the score appears, in plain language, without leaving the Smart Picks page.

**Why this priority**: Without this, the engines are a black box and the trader can't trust the combined score. The user explicitly asked for it. Reaching this is what turns the score into something actionable rather than mysterious.

**Independent Test**: Hover/click on each engine name or its score in the picks table; confirm a short explanation appears with: (a) what the engine measures, (b) score interpretation (e.g., "0–30 oversold, 70–100 overbought"), (c) why it matters / when this signal is most useful.

**Acceptance Scenarios**:

1. **Given** the trader is looking at a pick with engine scores, **When** they hover or tap on an engine label or score, **Then** a short explanation appears within 200 ms describing what it measures, score-range meaning, and why it matters.
2. **Given** the trader wants more detail, **When** they click "Learn more" in the inline explanation, **Then** they reach a fuller per-engine reference (a side panel, modal, or dedicated section) with examples but stay in the Smart Picks context.
3. **Given** the trader has Arabic selected, **When** they trigger the same explanation, **Then** the content is shown in Arabic.

---

### User Story 3 - Add New Quantitative Engines (Priority: P2)

Three additional engines are added to the Smart Picks ensemble so the score reflects more independent signals: an oscillator-based engine (RSI), a trend-following crossover engine (MACD), and a volatility-regime engine that flags how reliable the other engines should be considered in the current market state.

**Why this priority**: More independent signals reduce false positives and surface different kinds of opportunities. Independent of UX work, but the UX must already be in place to display them. P2 because the existing 7 engines plus news already give a usable score; this raises quality further.

**Independent Test**: For any ticker that the existing pipeline returns, verify three new engine results (RSI, MACD, Volatility Regime) appear with score, signal, and a 1-line rationale. Verify each new engine produces consistent results when run twice on the same data.

**Acceptance Scenarios**:

1. **Given** the Smart Picks pipeline runs on a market, **When** picks are returned, **Then** each pick includes RSI, MACD, and Volatility Regime engine outputs in addition to the existing engines.
2. **Given** a stock with known oversold conditions (RSI in the 0–30 range based on recent prices), **When** the RSI engine runs, **Then** it returns a low score (≤ 30) with an "oversold" rationale.
3. **Given** a stock whose short-term moving average crosses above its long-term moving average on the most recent bars, **When** the MACD engine runs, **Then** it returns a bullish score (≥ 60) with a "bullish crossover" rationale.
4. **Given** market data with elevated recent volatility, **When** the Volatility Regime engine runs, **Then** it reports a high-volatility regime which is visible in the pick row.

---

### User Story 4 - New Engines Integrated into the Combined Score (Priority: P2)

The new engines aren't displayed in isolation — they participate in the combined score and the BUY/HOLD/NEUTRAL/SELL signal the trader actually uses. The trader can see the new engines' contribution clearly, including how the volatility regime tempers (or amplifies) the final score in extreme conditions.

**Why this priority**: An engine that doesn't influence the final pick adds visual clutter without decision value. P2 because it depends on Story 3.

**Independent Test**: For a fixed ticker, compare the combined score before and after the new engines are integrated. Confirm the score moves in the expected direction when one of the new engines fires strongly. Confirm the volatility regime adjusts the score (e.g., dampens) in extreme regimes.

**Acceptance Scenarios**:

1. **Given** a ticker where the existing engines produce a combined score X, **When** the new engines fire bullishly, **Then** the new combined score is ≥ X (or unchanged if the new engines are neutral), and the change is explainable from the per-engine breakdown.
2. **Given** the volatility-regime engine reports an extreme regime (very high or very low volatility), **When** the combined score is computed, **Then** the score is moderated toward NEUTRAL relative to what it would be in a calm regime — preventing over-confidence in unstable markets.
3. **Given** the trader looks at a pick's score breakdown, **When** they expand the engine list, **Then** they see how much each engine (existing + new) contributed to the combined score.

---

### User Story 5 - Score Transparency Drill-Down (Priority: P3)

A trader who clicks on a pick gets a per-pick detail view that shows every engine's score, the engine's contribution to the combined score, and the rationale text from each engine — turning the combined number into a story the trader can audit.

**Why this priority**: This is what makes the score persuasive rather than just present. P3 because the inline education from Story 2 already covers the common case.

**Independent Test**: Click any pick row; confirm a detail view shows all engine scores, weights, contribution to the combined score, and a one-line "why" per engine.

**Acceptance Scenarios**:

1. **Given** a pick in the table, **When** the trader opens the detail view, **Then** every engine that contributed to the score is listed with its score, weight, and one-line rationale.
2. **Given** the detail view is open, **When** the trader closes it, **Then** they return to the Smart Picks list with their previous filters/sort intact.

---

### Edge Cases

- **Insufficient price history** for a new engine (e.g., RSI typically needs ~14+ bars; MACD needs ~26+): the engine reports "insufficient data" and is excluded from the combined score for that ticker, not silently treated as neutral. The pick row indicates the engine is unavailable so the user isn't confused.
- **Volatility regime extreme**: the dampening must not flip the signal direction — it can only move the score toward NEUTRAL, never invert BUY into SELL or vice versa.
- **Conflicting engines**: when one engine says strong BUY and another says strong SELL on the same ticker, the combined score reflects the disagreement (lands closer to NEUTRAL) and the detail view makes the disagreement visible.
- **Engine outage**: if any single engine fails for a given ticker, the pick still appears with the remaining engines; the failed engine is shown with an error indicator and its weight is redistributed across the remaining engines so the score remains comparable.
- **Long lists** (50+ picks): the redesign must not introduce render slowdowns; tooltips/hover-cards should not block scrolling.
- **Engine education in RTL**: explanation tooltips/panels must mirror correctly and use Arabic translations when the locale is Arabic.
- **Score reproducibility**: with the same input prices and timestamps, running the engine pipeline twice must produce identical scores so the trader can trust what they see.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST present the Smart Picks page in a layout that fits primary columns (rank, ticker, signal, score) without page-level horizontal scrolling on a 1280-pixel-wide desktop viewport in both LTR and RTL.
- **FR-002**: System MUST preserve every existing data point currently shown on the Smart Picks page — none of the current information may be removed by the redesign; data may be reorganized into expand-rows, tooltips, or a detail view.
- **FR-003**: System MUST display, for each engine result on the page, a per-engine inline explanation accessible via hover or click, containing (a) what the engine measures, (b) score-range interpretation, and (c) why this engine matters.
- **FR-004**: System MUST translate engine explanations and labels to Arabic when the active locale is Arabic.
- **FR-005**: System MUST add three new engines to the Smart Picks ensemble: an RSI-based engine, a MACD-based engine, and a volatility-regime engine.
- **FR-006**: System MUST produce a 0–100 score and a one-line rationale string for each new engine, using the same shape as the existing engines so that downstream consumers (UI, scoring, history) treat them uniformly.
- **FR-007**: System MUST integrate the three new engines into the combined Smart Picks score so they influence the final BUY/HOLD/NEUTRAL/SELL signal.
- **FR-008**: System MUST allow the volatility-regime engine to dampen the combined score toward NEUTRAL during extreme volatility regimes, but MUST NOT let it invert the signal direction.
- **FR-009**: System MUST omit any engine that has insufficient input data for a given ticker from that ticker's combined score and clearly mark the engine as unavailable in the UI, rather than substituting a neutral value silently.
- **FR-010**: System MUST redistribute engine weights when an engine is unavailable so that the combined score remains comparable across tickers.
- **FR-011**: System MUST provide a per-pick detail view that lists every engine's score, weight, contribution to the combined score, and one-line rationale.
- **FR-012**: System MUST maintain feature parity with the existing Smart Picks behavior: refresh action, sort, filter, manual scoring of an arbitrary ticker, market selection, and pagination must all keep working.
- **FR-013**: System MUST keep score computation deterministic — the same prices, timestamps, and parameters MUST produce identical scores across runs.
- **FR-014**: System MUST keep all engine education content in plain language understandable by a trader who is not a quantitative analyst.

### Key Entities

- **Engine Result**: Per ticker per engine. Carries (engine name, score 0–100, signal label, one-line rationale, "data sufficient?" flag, weight in the combined score). Same shape for existing and new engines.
- **Engine Reference**: Static, per-engine metadata used by the inline education UI. Carries (engine name, category, what-it-measures text, score-range interpretation, why-it-matters text). Available in English and Arabic.
- **Smart Pick**: A ticker plus its combined score, combined signal, list of Engine Results, and headline metrics already present today (MC probability, expected return, etc.).
- **Volatility Regime Tag**: A coarse label per ticker (e.g., calm / normal / elevated / extreme) emitted by the new volatility-regime engine and used both as a display badge and as the input that allows score dampening.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a 1280×800 desktop viewport in both LTR and RTL, 100% of primary columns (rank, ticker, signal, combined score) are visible without page-level horizontal scrolling on the Smart Picks page.
- **SC-002**: Every existing data point shown on the current Smart Picks page is reachable in the redesigned page (visible, expandable, or in detail view) — verified by a feature-parity walkthrough; zero items lost.
- **SC-003**: A trader unfamiliar with the engines can answer "what does Engine X measure and why does it matter?" within 10 seconds for any of the engines without leaving the Smart Picks page.
- **SC-004**: Three new engines (RSI, MACD, Volatility Regime) appear on every pick that has sufficient input data, with score, signal, and rationale.
- **SC-005**: For 90%+ of tickers in a representative sample, the new combined score (with all engines) differs by no more than ±10 points from the score the existing 7-engine ensemble would have produced — confirming that adding engines refines rather than destabilizes scores.
- **SC-006**: When the volatility-regime engine reports an extreme regime, the combined score moves toward NEUTRAL by a measurable amount (e.g., score absolute distance from 50 reduced) compared with the same engines under a calm regime — verified on a controlled test set.
- **SC-007**: When any single engine fails or has insufficient data, the pick still renders with the remaining engines and the failed engine is clearly marked unavailable; no pick is dropped solely because one engine failed.
- **SC-008**: Smart Picks page first-meaningful-render is no slower than today's baseline after the redesign — measured on the same hardware and input set.
- **SC-009**: Score determinism: running the pipeline twice with the same inputs produces byte-identical engine scores in 100% of cases.
- **SC-010**: All engine explanations are present in both English and Arabic; switching language flips the explanation text along with the rest of the page.

## Assumptions

- The redesign lands on its own feature branch (`012-smart-picks-overhaul`) and replaces the current Smart Picks page once accepted; this is not a side-by-side toggle.
- Existing Smart Picks API contracts may be extended (new fields per pick) but not broken — i.e., consumers that don't know about the new engines still get a usable response.
- Inline engine education is shown via hover/click (tooltip + drill-down), not by routing the user away to a documentation page; users stay in Smart Picks context.
- The three new engines (RSI, MACD, Volatility Regime) are the right set for this iteration; further engines (sentiment beyond news, fundamentals, sector rotation, etc.) are out of scope for this branch and tracked separately.
- The existing scoring weights stay reasonable when extended; weights are redistributed proportionally so the new engines participate without dwarfing or being dwarfed by the existing ones.
- Arabic translations of engine education content are produced as part of this branch; if professional translation is unavailable, working draft translations are acceptable for v1 and refined later.
- Existing motion/animation infrastructure from `011-animated-ui-redesign` is reused — the redesigned page benefits from `useMotionTokens()` and existing primitives (e.g., `<AnimatedList>`, `<ValueFlash>`, `<PageTransition>`).
- The redesign targets desktop and laptop screens primarily; mobile-specific layouts are improved opportunistically but not the goal of this branch.
