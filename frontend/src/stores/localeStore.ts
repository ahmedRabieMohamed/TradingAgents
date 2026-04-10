import { create } from 'zustand';
import i18n from '../i18n';

type Locale = 'en' | 'ar';

interface LocaleState {
  locale: Locale;
  direction: 'ltr' | 'rtl';
  setLocale: (locale: Locale) => void;
}

function applyDirection(locale: Locale) {
  const dir = locale === 'ar' ? 'rtl' : 'ltr';
  document.documentElement.dir = dir;
  document.documentElement.lang = locale;
  return dir;
}

const savedLocale = (localStorage.getItem('locale') as Locale) || 'en';
applyDirection(savedLocale);

export const useLocaleStore = create<LocaleState>((set) => ({
  locale: savedLocale,
  direction: savedLocale === 'ar' ? 'rtl' : 'ltr',
  setLocale: (locale: Locale) => {
    const direction = applyDirection(locale);
    localStorage.setItem('locale', locale);
    i18n.changeLanguage(locale);
    set({ locale, direction });
  },
}));
