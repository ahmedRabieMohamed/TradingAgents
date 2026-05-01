/**
 * Motion token catalog. See specs/011-animated-ui-redesign/data-model.md for
 * the canonical values; this file is the typed source for code.
 *
 * Components MUST consume tokens via useMotionTokens(), never import
 * defaultTokens / reducedTokens directly. See contracts/motion-tokens.md.
 */

export type Easing = [number, number, number, number];

export interface MotionTokens {
  page: {
    enter: { duration: number; easing: Easing; x: number };
    exit: { duration: number; easing: Easing };
  };
  stagger: {
    card: { delayStep: number; maxItems: number };
  };
  list: {
    item: {
      enter: { duration: number; x: number };
      exit: { duration: number; opacity: number };
    };
  };
  press: { scale: number; duration: number };
  value: {
    flash: { duration: number; upColor: string; downColor: string };
    countUp: { duration: number };
  };
  chart: {
    enter: { duration: number; easing: string };
    container: { enter: { duration: number } };
  };
  modal: {
    enter: { duration: number };
    exit: { duration: number };
    backdrop: { opacity: number };
  };
  skeleton: { shimmer: { duration: number; angle: number } };
}

const easeOutQuint: Easing = [0.22, 1, 0.36, 1];
const easeIn: Easing = [0.4, 0, 1, 1];

export const defaultTokens: MotionTokens = {
  page: {
    enter: { duration: 350, easing: easeOutQuint, x: 16 },
    exit: { duration: 200, easing: easeIn },
  },
  stagger: {
    card: { delayStep: 40, maxItems: 12 },
  },
  list: {
    item: {
      enter: { duration: 220, x: 12 },
      exit: { duration: 180, opacity: 0 },
    },
  },
  press: { scale: 0.97, duration: 90 },
  value: {
    flash: {
      duration: 600,
      upColor: 'var(--color-success-flash, rgba(34, 197, 94, 0.18))',
      downColor: 'var(--color-danger-flash, rgba(239, 68, 68, 0.18))',
    },
    countUp: { duration: 500 },
  },
  chart: {
    enter: { duration: 600, easing: 'ease-out' },
    container: { enter: { duration: 300 } },
  },
  modal: {
    enter: { duration: 220 },
    exit: { duration: 160 },
    backdrop: { opacity: 0.5 },
  },
  skeleton: { shimmer: { duration: 1400, angle: 100 } },
};

export const reducedTokens: MotionTokens = {
  page: {
    enter: { duration: 120, easing: easeOutQuint, x: 0 },
    exit: { duration: 80, easing: easeIn },
  },
  stagger: {
    card: { delayStep: 0, maxItems: 0 },
  },
  list: {
    item: {
      enter: { duration: 100, x: 0 },
      exit: { duration: 80, opacity: 0 },
    },
  },
  press: { scale: 1.0, duration: 60 },
  value: {
    flash: {
      duration: 250,
      upColor: defaultTokens.value.flash.upColor,
      downColor: defaultTokens.value.flash.downColor,
    },
    countUp: { duration: 0 },
  },
  chart: {
    enter: { duration: 0, easing: 'linear' },
    container: { enter: { duration: 100 } },
  },
  modal: {
    enter: { duration: 100 },
    exit: { duration: 80 },
    backdrop: { opacity: 0.5 },
  },
  skeleton: { shimmer: { duration: 0, angle: 100 } },
};
