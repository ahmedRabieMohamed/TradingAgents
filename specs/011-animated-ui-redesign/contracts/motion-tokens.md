# Contract — Motion Token API

**Feature**: Animated & Motion-Driven Frontend UI (`011-animated-ui-redesign`)
**Audience**: Any component author in `frontend/src/`
**Stability**: Public-internal — additions are non-breaking; renaming/removing a token is a breaking change.

This contract defines the **only** way components in this codebase consume motion. Hard-coded durations, easings, and distances scattered across components are explicitly out of bounds.

---

## Public surface

### Hook: `useMotionTokens()`

```ts
import { useMotionTokens } from "@/motion";

function MyComponent() {
  const tokens = useMotionTokens();
  // tokens.page.enter.duration, tokens.list.item.enter.x, …
}
```

**Returns**: a frozen `MotionTokens` object. Either the default profile or the reduced-motion profile, selected at hook-call time based on `prefers-reduced-motion`.

**Type** (informal):

```ts
type MotionTokens = {
  page:    { enter: { duration: number; easing: number[]; x: number };
             exit:  { duration: number; easing: number[] } };
  stagger: { card:  { delayStep: number; maxItems: number } };
  list:    { item:  { enter: { duration: number; x: number };
                      exit:  { duration: number; opacity: number } } };
  press:   { scale: number; duration: number };
  value:   { flash: { duration: number; upColor: string; downColor: string };
             countUp: { duration: number } };
  chart:   { enter: { duration: number; easing: string };
             container: { enter: { duration: number } } };
  modal:   { enter: { duration: number };
             exit:  { duration: number };
             backdrop: { opacity: number } };
  skeleton:{ shimmer: { duration: number; angle: number } };
};
```

The exhaustive token list and default values live in [`../data-model.md`](../data-model.md). The TypeScript declaration is the single source of truth for shape; the data-model document is the single source of truth for values.

### Hook: `useDirection()`

```ts
import { useDirection } from "@/motion";

const { dir, dirSign } = useDirection(); // dir: "ltr" | "rtl"; dirSign: 1 | -1
```

**Returns**: the active layout direction and a sign multiplier. Use `dirSign` to mirror any `*.x` token. Never read `document.dir` directly inside a component.

### Primitives (consumers should prefer these over raw `motion` elements)

| Primitive | Wraps | Use it for |
|-----------|-------|------------|
| `<PageTransition>` | `<AnimatePresence mode="wait">` + page wrapper | Top-level route transitions (mounted once in `App.tsx`) |
| `<EnterStagger>` | `motion.div` + variants | Coordinated entrance for grids of cards (Dashboard panels, market overview tiles) |
| `<AnimatedList>` | `<AnimatePresence>` + `motion.li` | Lists where items add/remove (watchlist, history, positions, smart-picks) |
| `<ValueFlash>` | `motion.span` + count-up | Live numeric values (prices, P&L, totals, scores) |
| `<PressFeedback>` | `motion.button` (or wraps existing button) | Primary buttons that need press response |
| `<SkeletonShimmer>` | CSS gradient animation gated by tokens | Loading placeholders for any operation > 200 ms |

---

## Rules

1. **Components MUST NOT import token values directly.** Always go through `useMotionTokens()`.
2. **Components MUST NOT call `useReducedMotion()` from `motion`.** The token hook already accounts for it.
3. **Directional motion (`*.x`) MUST be multiplied by `dirSign` from `useDirection()`** — done by primitives; component authors do not touch this when using primitives.
4. **Adding a new token** requires:
   - Updating `data-model.md` (default + reduced override).
   - Updating `frontend/src/motion/tokens.ts`.
   - Justifying why an existing token cannot serve the same purpose.
5. **Changing or removing a token** is breaking. Search the codebase for usages and update them in the same change.
6. **Tokens are not theme variables.** Theme (color, spacing) lives in AntD theme + `globals.css`. Tokens here are duration/easing/distance only — except `value.flash.*Color`, which intentionally points at theme CSS custom properties so the flash respects light/dark mode.

---

## Verification

For each acceptance scenario in `spec.md`:

- The corresponding token is sourced via `useMotionTokens()` and the duration falls within the budget the spec defines (SC-002 through SC-006).
- With OS `prefers-reduced-motion: reduce`, no token-driven duration exceeds 150 ms (SC-006).
- For directional motion, switching the app to Arabic flips the visible direction with no code change in consuming components.

These verifications are documented as steps in [`../quickstart.md`](../quickstart.md).
