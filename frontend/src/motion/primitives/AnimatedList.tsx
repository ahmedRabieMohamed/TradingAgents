import { AnimatePresence, motion } from 'motion/react';
import type { ReactNode, CSSProperties } from 'react';
import { useMotionTokens } from '../reducedMotion';
import { useDirection } from '../direction';

export interface AnimatedListItem {
  key: string | number;
  content: ReactNode;
}

interface AnimatedListProps {
  items: AnimatedListItem[];
  as?: 'ul' | 'ol' | 'div';
  className?: string;
  style?: CSSProperties;
  itemClassName?: string;
  itemStyle?: CSSProperties;
}

/**
 * Renders a list whose items animate on enter and exit. Items are keyed by
 * `item.key`; only newly added or removed items animate, so re-orderings and
 * long lists do not re-stagger every render.
 *
 * Use cases: Watchlist rows, history rows, portfolio positions, smart-picks
 * results, analysis log entries.
 */
export function AnimatedList({
  items,
  as = 'div',
  className,
  style,
  itemClassName,
  itemStyle,
}: AnimatedListProps) {
  const tokens = useMotionTokens();
  const { dirSign } = useDirection();
  const enter = tokens.list.item.enter;
  const exit = tokens.list.item.exit;

  const Container = as as 'div';

  return (
    <Container className={className} style={style}>
      <AnimatePresence initial={false}>
        {items.map(item => (
          <motion.div
            key={item.key}
            className={itemClassName}
            style={itemStyle}
            initial={{ opacity: 0, x: enter.x * dirSign }}
            animate={{ opacity: 1, x: 0 }}
            exit={{
              opacity: exit.opacity,
              transition: { duration: exit.duration / 1000 },
            }}
            transition={{ duration: enter.duration / 1000 }}
            layout
          >
            {item.content}
          </motion.div>
        ))}
      </AnimatePresence>
    </Container>
  );
}
