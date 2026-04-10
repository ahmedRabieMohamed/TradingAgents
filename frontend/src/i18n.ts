import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import English translations
import commonEn from './locales/en/common.json';
import dashboardEn from './locales/en/dashboard.json';
import analysisEn from './locales/en/analysis.json';
import historyEn from './locales/en/history.json';
import portfolioEn from './locales/en/portfolio.json';
import watchlistEn from './locales/en/watchlist.json';
import performanceEn from './locales/en/performance.json';
import settingsEn from './locales/en/settings.json';

// Import Arabic translations
import commonAr from './locales/ar/common.json';
import dashboardAr from './locales/ar/dashboard.json';
import analysisAr from './locales/ar/analysis.json';
import historyAr from './locales/ar/history.json';
import portfolioAr from './locales/ar/portfolio.json';
import watchlistAr from './locales/ar/watchlist.json';
import performanceAr from './locales/ar/performance.json';
import settingsAr from './locales/ar/settings.json';

const savedLocale = localStorage.getItem('locale') || 'en';

i18n.use(initReactI18next).init({
  resources: {
    en: {
      common: commonEn,
      dashboard: dashboardEn,
      analysis: analysisEn,
      history: historyEn,
      portfolio: portfolioEn,
      watchlist: watchlistEn,
      performance: performanceEn,
      settings: settingsEn,
    },
    ar: {
      common: commonAr,
      dashboard: dashboardAr,
      analysis: analysisAr,
      history: historyAr,
      portfolio: portfolioAr,
      watchlist: watchlistAr,
      performance: performanceAr,
      settings: settingsAr,
    },
  },
  lng: savedLocale,
  fallbackLng: 'en',
  defaultNS: 'common',
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
