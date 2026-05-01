import { useReducedMotion } from 'motion/react';
import { defaultTokens, reducedTokens, type MotionTokens } from './tokens';

/**
 * Single source of truth for which motion-token profile is active.
 * Components must consume this hook instead of reading tokens or
 * `useReducedMotion()` directly.
 */
export function useMotionTokens(): MotionTokens {
  const reduce = useReducedMotion();
  return reduce ? reducedTokens : defaultTokens;
}
