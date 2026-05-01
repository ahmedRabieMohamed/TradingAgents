# Phase 1 — Data Model (UX Entities)

**Feature**: Animated & Motion-Driven Frontend UI (`011-animated-ui-redesign`)
**Date**: 2026-04-30

This feature introduces no persistent data entities. The "data model" here is the
**UX-level vocabulary** that the redesign ships with — the motion-token catalog
and its reduced-motion profile. Components in the rest of the codebase consume
these tokens via the `useMotionTokens()` hook; they do not hard-code values.

---

## Entity 1 — Motion Token Set (default profile)

A named catalog of motion parameters (durations, easings, distances) used
across the app.

### Token groups

| Group | Token | Type | Default | Purpose |
|-------|-------|------|---------|---------|
| `page` | `enter.duration` | ms | 350 | Page entrance fade/slide |
| `page` | `enter.easing` | cubic-bezier | `[0.22, 1, 0.36, 1]` (ease-out-quint) | Page entrance |
| `page` | `enter.x` | px | 16 (× `dirSign`) | Horizontal travel on enter |
| `page` | `exit.duration` | ms | 200 | Page exit |
| `page` | `exit.easing` | cubic-bezier | `[0.4, 0, 1, 1]` (ease-in) | Page exit |
| `stagger` | `card.delayStep` | ms | 40 | Per-card delay in entrance grids |
| `stagger` | `card.maxItems` | int | 12 | Stagger only the first N items |
| `list` | `item.enter.duration` | ms | 220 | New list-item appears |
| `list` | `item.enter.x` | px | 12 (× `dirSign`) | Horizontal slide for incoming item |
| `list` | `item.exit.duration` | ms | 180 | Removed list-item disappears |
| `list` | `item.exit.opacity` | number | 0 | Fade-out target |
| `press` | `scale` | number | 0.97 | Press feedback scale on primary buttons |
| `press` | `duration` | ms | 90 | Press feedback duration |
| `value` | `flash.duration` | ms | 600 | Numeric-value flash |
| `value` | `flash.upColor` | css color | `--color-success-flash` | Up-direction flash |
| `value` | `flash.downColor` | css color | `--color-danger-flash` | Down-direction flash |
| `value` | `countUp.duration` | ms | 500 | Count-up tween for big numbers |
| `chart` | `enter.duration` | ms | 600 | Chart series draw-in (Recharts) |
| `chart` | `enter.easing` | string | `ease-out` | Recharts `animationEasing` |
| `chart` | `container.enter.duration` | ms | 300 | Lightweight-charts container fade/scale |
| `modal` | `enter.duration` | ms | 220 | Modal/drawer open |
| `modal` | `exit.duration` | ms | 160 | Modal/drawer close |
| `modal` | `backdrop.opacity` | number | 0.5 | Final backdrop opacity |
| `skeleton` | `shimmer.duration` | ms | 1400 | Loading shimmer cycle |
| `skeleton` | `shimmer.angle` | deg | 100 | Shimmer gradient angle |

### Validation rules

- All `duration` values **must be > 0** and **≤ 800 ms** (matches SC-003).
- `enter.x` values are **scalars only**; the primitive multiplies by `dirSign`
  from `useDirection()` to mirror RTL.
- `flash.upColor` / `flash.downColor` reference CSS custom properties so theme
  changes (light/dark) automatically take effect.
- New tokens **must be added to this catalog and to `frontend/src/motion/tokens.ts`
  in the same change** — components must not introduce ad-hoc values.

### State / lifecycle

The token set has no runtime state. It is a frozen object selected at
component mount time by `useMotionTokens()`.

---

## Entity 2 — Reduced-Motion Profile

The variant of the token set that activates when the user's OS reports
`prefers-reduced-motion: reduce`. Same token names, simpler/shorter values.

### Overrides applied to the default profile

| Token | Default | Reduced |
|-------|---------|---------|
| `page.enter.duration` | 350 ms | 120 ms |
| `page.enter.x` | 16 px | 0 (no slide) |
| `page.exit.duration` | 200 ms | 80 ms |
| `stagger.card.delayStep` | 40 ms | 0 ms (no stagger) |
| `list.item.enter.duration` | 220 ms | 100 ms |
| `list.item.enter.x` | 12 px | 0 |
| `list.item.exit.duration` | 180 ms | 80 ms |
| `press.scale` | 0.97 | 1.0 (no scale; opacity tap only) |
| `press.duration` | 90 ms | 60 ms |
| `value.countUp.duration` | 500 ms | 0 ms (set value directly; keep color flash) |
| `value.flash.duration` | 600 ms | 250 ms |
| `chart.enter.duration` | 600 ms | 0 ms (Recharts `isAnimationActive=false`) |
| `chart.container.enter.duration` | 300 ms | 100 ms |
| `modal.enter.duration` | 220 ms | 100 ms |
| `skeleton.shimmer.duration` | 1400 ms | 0 ms (static skeleton, no shimmer) |

All durations under reduced-motion are capped at **150 ms** per SC-006, except
`skeleton.shimmer.duration = 0` (animation removed entirely).

### Critical preservations under reduced motion

The following are **never** removed, even with reduced motion enabled — they
are the spec's "functional" motion (Edge Case: Reduced motion + value updates):

- `value.flash.upColor` / `flash.downColor` — colors still apply (no count-up,
  but the flash signals the change).
- Loading state visibility — skeletons still render; only the shimmer animation
  is suppressed.
- Modal open/close — short fade (≤ 100 ms) preserved so users can perceive the
  state change.

---

## Relationships

```text
useMotionTokens()
   │
   ├── if useReducedMotion() === true  → Reduced-Motion Profile
   └── otherwise                       → Default Motion Token Set
   │
   ├── consumed by → motion/primitives/PageTransition.tsx
   ├── consumed by → motion/primitives/AnimatedList.tsx
   ├── consumed by → motion/primitives/ValueFlash.tsx
   ├── consumed by → motion/primitives/PressFeedback.tsx
   ├── consumed by → motion/primitives/SkeletonShimmer.tsx
   └── consumed by → chart adapters in components/{performance,portfolio,analysis}/
```

The `useDirection()` hook is orthogonal: it returns `dirSign ∈ {+1, -1}`,
multiplied into directional tokens (`*.x` fields) by primitives, never by
component authors directly.
