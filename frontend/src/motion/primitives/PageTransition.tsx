import { motion } from 'motion/react';
import type { ReactNode } from 'react';
import { useMotionTokens } from '../reducedMotion';
import { useDirection } from '../direction';

interface PageTransitionProps {
  children: ReactNode;
}

/**
 * Wraps a route component. Mount inside <AnimatePresence mode="wait"> in App.tsx
 * with a key bound to useLocation().pathname so this primitive's enter/exit
 * tokens drive the page-to-page transition.
 */
export function PageTransition({ children }: PageTransitionProps) {
  const tokens = useMotionTokens();
  const { dirSign } = useDirection();
  const enter = tokens.page.enter;
  const exit = tokens.page.exit;

  return (
    <motion.div
      initial={{ opacity: 0, x: enter.x * dirSign }}
      animate={{ opacity: 1, x: 0 }}
      exit={{
        opacity: 0,
        transition: { duration: exit.duration / 1000, ease: exit.easing },
      }}
      transition={{ duration: enter.duration / 1000, ease: enter.easing }}
      style={{ width: '100%', height: '100%' }}
    >
      {children}
    </motion.div>
  );
}
