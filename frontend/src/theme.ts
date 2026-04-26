import { theme } from 'antd';
import type { ThemeConfig } from 'antd';

const appTheme: ThemeConfig = {
  algorithm: theme.darkAlgorithm,
  token: {
    // Primary
    colorPrimary: '#3b82f6',
    colorInfo: '#3b82f6',

    // Backgrounds
    colorBgLayout: '#0a0e17',
    colorBgContainer: '#111827',
    colorBgElevated: '#1a2236',
    colorBgSpotlight: '#1a2236',

    // Borders
    colorBorder: '#1e2a3a',
    colorBorderSecondary: '#1e2a3a',

    // Text
    colorText: '#e2e8f0',
    colorTextSecondary: '#94a3b8',
    colorTextTertiary: '#64748b',
    colorTextQuaternary: '#475569',

    // Semantic
    colorSuccess: '#10b981',
    colorError: '#ef4444',
    colorWarning: '#f59e0b',

    // Shape
    borderRadius: 8,
    borderRadiusSM: 6,
    borderRadiusLG: 12,

    // Typography
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    fontSize: 14,
  },
  components: {
    Layout: {
      siderBg: '#0d1321',
      headerBg: '#111827',
      bodyBg: '#0a0e17',
    },
    Menu: {
      darkItemBg: 'transparent',
      darkItemColor: '#94a3b8',
      darkItemHoverColor: '#e2e8f0',
      darkItemHoverBg: 'rgba(59, 130, 246, 0.08)',
      darkItemSelectedBg: 'rgba(59, 130, 246, 0.12)',
      darkItemSelectedColor: '#3b82f6',
    },
    Table: {
      headerBg: '#1a2236',
      headerColor: '#94a3b8',
      rowHoverBg: 'rgba(59, 130, 246, 0.05)',
      borderColor: '#1e2a3a',
    },
    Card: {
      colorBgContainer: '#111827',
      colorBorderSecondary: '#1e2a3a',
    },
    Modal: {
      contentBg: '#111827',
      headerBg: '#111827',
    },
    Input: {
      colorBgContainer: '#1a2236',
      colorBorder: '#1e2a3a',
    },
    Select: {
      colorBgContainer: '#1a2236',
      colorBorder: '#1e2a3a',
    },
    Button: {
      borderRadius: 6,
    },
    Tag: {
      borderRadiusSM: 12,
    },
  },
};

export default appTheme;
