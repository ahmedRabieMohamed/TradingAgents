import { motion } from 'motion/react';
import type { ReactNode, CSSProperties } from 'react';
import { useMotionTokens } from '../reducedMotion';

interface PressFeedbackProps {
  children: ReactNode;
  className?: string;
  style?: CSSProperties;
  disabled?: boolean;
}

/**
 * Wraps an element (button, card, list row) and applies a brief scale + opacity
 * response on press. Under reduced motion, scale collapses to 1.0 and only a
 * faint opacity nudge remains.
 */
export function PressFeedback({ children, className, style, disabled }: PressFeedbackProps) {
  const tokens = useMotionTokens();
  const { scale, duration } = tokens.press;

  return (
    <motion.div
      className={className}
      style={{ display: 'inline-block', ...style }}
      whileTap={disabled ? undefined : { scale, opacity: 0.85 }}
      transition={{ duration: duration / 1000 }}
    >
      {children}
    </motion.div>
  );
}
