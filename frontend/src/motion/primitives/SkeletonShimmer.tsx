import type { CSSProperties } from 'react';
import { useMotionTokens } from '../reducedMotion';

interface SkeletonShimmerProps {
  width?: string | number;
  height?: string | number;
  borderRadius?: string | number;
  className?: string;
  style?: CSSProperties;
}

/**
 * Animated loading placeholder. A diagonal gradient sweep cycles across the
 * surface; under reduced motion (shimmer.duration === 0) the gradient is
 * static so users still see the placeholder.
 */
export function SkeletonShimmer({
  width = '100%',
  height = 16,
  borderRadius = 4,
  className,
  style,
}: SkeletonShimmerProps) {
  const tokens = useMotionTokens();
  const { duration, angle } = tokens.skeleton.shimmer;
  const animated = duration > 0;

  return (
    <span
      className={className}
      style={{
        display: 'inline-block',
        width,
        height,
        borderRadius,
        background: animated
          ? `linear-gradient(${angle}deg, var(--surface2) 25%, var(--surface) 50%, var(--surface2) 75%)`
          : 'var(--surface2)',
        backgroundSize: animated ? '200% 100%' : undefined,
        animation: animated ? `skeleton-shimmer ${duration}ms linear infinite` : undefined,
        ...style,
      }}
    />
  );
}
