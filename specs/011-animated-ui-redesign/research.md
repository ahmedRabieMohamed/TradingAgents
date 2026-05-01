# Phase 0 — Research

**Feature**: Animated & Motion-Driven Frontend UI (`011-animated-ui-redesign`)
**Date**: 2026-04-30

This document resolves the open technical questions identified in `plan.md` so Phase 1 (data model + contracts) can proceed without `NEEDS CLARIFICATION` markers.

---

## R1. Animation library choice

**Decision**: Adopt **`motion`** (the published successor to Framer Motion, package name `motion`, v11+) as the single animation library.

**Rationale**:
- React 19 compatible. The team has already moved to React 19 and AntD 6, so a library that lags behind is a non-starter.
- Native primitives for everything the spec asks for: route transitions (`AnimatePresence`), list enter/exit (`AnimatePresence` + `layout`), gesture/press feedback (`whileTap`, `whileHover`), reduced-motion (`useReducedMotion`), layout animations (`layoutId`), and direction-aware variants.
- A single dependency satisfies all five user stories — keeps Constitution principle I (Simplicity First).
- Tree-shakable; production bundle cost is bounded (~12–18 kB gzipped for the surface we'll use).

**Alternatives considered**:
- **`@react-spring/web`** — physics-based, powerful, but the API is heavier for simple enter/exit and orchestration; would require more bespoke wrappers. Rejected on simplicity.
- **CSS-only** (`@keyframes` + `transition`) — sufficient for entrance, page fades, and reduced-motion. Insufficient for clean exit animations on React unmount and for AnimatePresence-style list reflow. Rejected because the spec requires item exit animations (FR-005).
- **`motion` Mini / `motion-vanilla`** — smaller, but less ergonomic for React-tree orchestration. Rejected.
- **AntD 6 native motion** — useful for component-level micro-animations (already implicit). We will keep it; it is complementary, not a substitute, for page/list orchestration.

**Risks & mitigations**:
- Bundle size — acceptable for a desktop-first trading app; monitored via existing Vite build output.
- Library lock-in — mitigated by funneling all usage through the `frontend/src/motion/primitives/*` layer; swapping libraries later means rewriting that one folder.

---

## R2. Page-transition strategy under React Router 7

**Decision**: Wrap `<Routes>` in `<AnimatePresence mode="wait">` and key the active route container by `useLocation().pathname`. Use a single `<PageTransition>` primitive that applies the `page.enter` and `page.exit` motion tokens.

**Rationale**:
- React Router 7's `useLocation` is stable; pairing it with `AnimatePresence mode="wait"` produces clean, non-overlapping page transitions and lets each page's exit animation finish before the next page's enter begins. This satisfies the "no visible flash or layout jump" requirement (Story 1, AC-2).
- `mode="wait"` avoids the rapid-navigation orphan problem (Edge Case: Rapid navigation) — `AnimatePresence` handles cancellation deterministically.
- Single wrapper — every page benefits without per-page edits beyond the wrap call.

**Alternatives considered**:
- **Per-route loader-driven transitions** — overkill for presentational motion; couples motion to data fetching unnecessarily. Rejected.
- **No `mode="wait"`** (overlapping transitions) — looks busier and risks doubled scrollbars / layout fights on overlapping pages. Rejected.

---

## R3. Chart animation strategy

**Decision**: Use library-native animation for each chart library, with motion tokens applied where the library exposes duration/easing knobs.

**Per library**:
- **`recharts`** — keep `isAnimationActive` enabled; pass `animationDuration` and `animationEasing` from the `chart.enter` token. This satisfies "series draw or grow into place" (Story 3, AC-1) for equity curves, performance bars, and smart-picks visuals.
- **`lightweight-charts`** — has no built-in animation API for series draw. We will animate the **container** (fade + subtle scale-in via `motion`) on first mount and on data-source change, not the series themselves. On data updates the library already eases via its built-in render path. Acceptable per Story 3, AC-2 ("eases between old and new state instead of jumping") since the library's internal renderer covers update easing.

**Rationale**:
- Avoids re-implementing chart engines or forcing a heavyweight wrapper.
- Recharts already has good motion ergonomics — wasting effort to replace it would violate Simplicity First.
- Lightweight-charts' container-level animation is a well-known pattern and visually satisfies the spec's user-perception goal.

**Alternatives considered**:
- **Custom `motion`-driven SVG redraw on top of lightweight-charts** — high effort, high risk, no user-visible benefit beyond what container fades already provide. Rejected.
- **Disable Recharts animation, drive it with `motion`** — duplicates work and produces less consistent results than the built-in. Rejected.

---

## R4. Reduced-motion fallback strategy

**Decision**: Implement one `useMotionTokens()` hook that returns either the **default** or the **reduced** token set based on `motion`'s `useReducedMotion()`. All motion primitives consume this hook; raw token values are not imported directly into components.

**Rationale**:
- Single source of truth for the reduced-motion decision — components never branch on `prefers-reduced-motion` themselves.
- Keeps the reduced-motion **profile**, not just durations, swappable: distances collapse to 0, easings collapse to linear, decorative entrances collapse to short fades, value flashes collapse to color-only emphasis (no count-up). This satisfies FR-009 and Edge Case "Reduced motion + value updates".
- Layered with a CSS fallback in `globals.css` (`@media (prefers-reduced-motion: reduce)`) so any animation that escapes the JS layer (CSS-only effects in AntD or custom CSS) is also tamed.

**Alternatives considered**:
- **Per-component `useReducedMotion` checks** — duplication, easy to miss. Rejected.
- **CSS-only suppression** — works for CSS animations but `motion` JS animations would still run. Rejected as insufficient.

---

## R5. RTL / Arabic mirroring

**Decision**: A `useDirection()` hook reads the active i18n language (existing `react-i18next` infrastructure) and returns a `dirSign` of `+1` (LTR) or `-1` (RTL). Directional motion tokens (e.g., `page.enter.x`, `list.item.enter.x`) are multiplied by `dirSign` inside primitives. Non-directional motion (fade, scale, opacity) is unaffected.

**Rationale**:
- Existing app already toggles `<html dir>` based on locale, so the source of truth exists.
- Centralizing the sign flip inside primitives means each component author writes "slide in from the start of the line" once; the primitive interprets "start" correctly per direction. Satisfies FR-011 and Story 5.

**Alternatives considered**:
- **Per-component direction handling** — error-prone, will drift. Rejected.
- **Two parallel token sets (LTR / RTL)** — doubles the token surface for no benefit over a sign multiplier. Rejected.

---

## Summary of decisions

| Question | Decision |
|----------|----------|
| Animation library | `motion` v11+ (Framer Motion successor) |
| Page transitions | `<AnimatePresence mode="wait">` keyed on `pathname` |
| Recharts animation | Library-native, driven by `chart.enter` tokens |
| `lightweight-charts` animation | Container-level fade/scale on mount + data-source change |
| Reduced-motion control point | `useMotionTokens()` hook returning default/reduced profile |
| RTL handling | `useDirection()` hook → `dirSign` multiplier inside primitives |

All `NEEDS CLARIFICATION` items from the Technical Context are resolved. Ready for Phase 1.
