import { animate, motion, useMotionValue, useTransform } from 'motion/react';
import { useEffect, useRef } from 'react';
import type { CSSProperties, ReactNode } from 'react';
import { useMotionTokens } from '../reducedMotion';

interface ValueFlashProps {
  value: number;
  /** Optional formatter (e.g., currency, percent). */
  format?: (n: number) => string;
  /** Decimal places when no `format` provided. */
  decimals?: number;
  /** Optional prefix/suffix rendered alongside the number. */
  children?: ReactNode;
  className?: string;
  style?: CSSProperties;
}

/**
 * Animated transition for a live numeric value: count-up tween into the new
 * value, plus a brief background-color flash signaling direction.
 *
 * Under reduced motion (countUp.duration === 0), the value snaps but the
 * directional color flash still fires — users still perceive the change.
 */
export function ValueFlash({
  value,
  format,
  decimals = 2,
  children,
  className,
  style,
}: ValueFlashProps) {
  const tokens = useMotionTokens();
  const flash = tokens.value.flash;
  const countUpMs = tokens.value.countUp.duration;

  const mv = useMotionValue(value);
  const display = useTransform(mv, latest =>
    format ? format(latest) : latest.toFixed(decimals),
  );

  const prevValue = useRef(value);
  const flashRef = useRef<HTMLSpanElement | null>(null);

  useEffect(() => {
    const prev = prevValue.current;
    if (prev === value) return;

    // 1. Count-up tween (snaps when countUpMs === 0).
    let stop: (() => void) | undefined;
    if (countUpMs > 0) {
      const controls = animate(mv, value, {
        duration: countUpMs / 1000,
        ease: 'easeOut',
      });
      stop = () => controls.stop();
    } else {
      mv.set(value);
    }

    // 2. Direction flash (always fires).
    const direction = value > prev ? 'up' : value < prev ? 'down' : null;
    if (direction && flashRef.current) {
      const color = direction === 'up' ? flash.upColor : flash.downColor;
      flashRef.current.animate(
        [{ backgroundColor: color }, { backgroundColor: 'transparent' }],
        { duration: flash.duration, easing: 'ease-out' },
      );
    }

    prevValue.current = value;
    return stop;
  }, [value, mv, flash, countUpMs]);

  return (
    <span ref={flashRef} className={className} style={{ borderRadius: 4, ...style }}>
      <motion.span>{display}</motion.span>
      {children}
    </span>
  );
}
