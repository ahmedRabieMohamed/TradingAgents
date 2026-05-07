import { motion } from 'motion/react';
import type { ReactNode, CSSProperties } from 'react';
import { Children, isValidElement, cloneElement } from 'react';
import { useMotionTokens } from '../reducedMotion';

interface EnterStaggerProps {
  children: ReactNode;
  className?: string;
  style?: CSSProperties;
}

/**
 * Coordinated entrance for a small grid of cards. Each direct child is wrapped
 * in a motion.div with a delay = min(index, maxItems) * delayStep. Beyond
 * maxItems items render with no extra delay so long lists do not stagger
 * forever (Edge Case "Long lists" in spec.md).
 */
export function EnterStagger({ children, className, style }: EnterStaggerProps) {
  const tokens = useMotionTokens();
  const { delayStep, maxItems } = tokens.stagger.card;
  const enterDur = tokens.page.enter.duration / 1000;

  const items = Children.toArray(children).filter(isValidElement);

  return (
    <div className={className} style={style}>
      {items.map((child, idx) => {
        const delay = Math.min(idx, maxItems) * (delayStep / 1000);
        return (
          <motion.div
            key={(child as { key?: string | number | null }).key ?? idx}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: enterDur, delay, ease: [0.22, 1, 0.36, 1] }}
          >
            {cloneElement(child)}
          </motion.div>
        );
      })}
    </div>
  );
}
