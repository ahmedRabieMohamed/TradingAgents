import { useTranslation } from 'react-i18next';

export type Direction = 'ltr' | 'rtl';

export interface DirectionInfo {
  dir: Direction;
  dirSign: 1 | -1;
}

/**
 * Reads the active i18n language direction. Multiplies any directional
 * (`*.x`) motion-token by `dirSign` so slides naturally mirror in RTL.
 */
export function useDirection(): DirectionInfo {
  const { i18n } = useTranslation();
  const dir: Direction = i18n.dir() === 'rtl' ? 'rtl' : 'ltr';
  return { dir, dirSign: dir === 'rtl' ? -1 : 1 };
}
