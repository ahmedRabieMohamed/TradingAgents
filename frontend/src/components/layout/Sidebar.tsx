import { useNavigate, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Layout, Menu, Badge, Typography, Space } from 'antd';
import {
  DashboardOutlined,
  LineChartOutlined,
  HistoryOutlined,
  StarOutlined,
  FundOutlined,
  WalletOutlined,
  SettingOutlined,
  RiseOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { getPortfolio } from '../../services/api';

const { Sider } = Layout;
const { Text } = Typography;

interface MarketSchedule {
  label: string;
  weekendDays: number[];
  openHour: number;
  closeHour: number;
  timezone: string;
}

const MARKETS: Record<string, MarketSchedule> = {
  us: {
    label: 'US (NYSE/NASDAQ)',
    weekendDays: [0, 6],
    openHour: 9,
    closeHour: 16,
    timezone: 'America/New_York',
  },
  egypt: {
    label: 'Egypt (EGX)',
    weekendDays: [5, 6],
    openHour: 10,
    closeHour: 15,
    timezone: 'Africa/Cairo',
  },
};

function isMarketOpen(schedule: MarketSchedule): boolean {
  const now = new Date();
  const formatter = new Intl.DateTimeFormat('en-US', {
    timeZone: schedule.timezone,
    hour: 'numeric',
    hour12: false,
    weekday: 'short',
  });
  const parts = formatter.formatToParts(now);
  const hour = parseInt(parts.find((p) => p.type === 'hour')?.value || '0', 10);
  const weekday = parts.find((p) => p.type === 'weekday')?.value || '';
  const dayMap: Record<string, number> = {
    Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6,
  };
  const dayNum = dayMap[weekday] ?? now.getDay();
  if (schedule.weekendDays.includes(dayNum)) return false;
  return hour >= schedule.openHour && hour < schedule.closeHour;
}

export default function Sidebar() {
  const { t } = useTranslation('common');
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [openPositions, setOpenPositions] = useState(0);
  const [marketStatus, setMarketStatus] = useState<Record<string, boolean>>({});

  useEffect(() => {
    let cancelled = false;
    function fetchCount() {
      getPortfolio()
        .then((p) => { if (!cancelled) setOpenPositions(p.open_positions_count); })
        .catch(() => {});
    }
    fetchCount();
    const interval = setInterval(fetchCount, 60000);
    return () => { cancelled = true; clearInterval(interval); };
  }, []);

  useEffect(() => {
    function updateStatus() {
      const status: Record<string, boolean> = {};
      for (const [id, schedule] of Object.entries(MARKETS)) {
        status[id] = isMarketOpen(schedule);
      }
      setMarketStatus(status);
    }
    updateStatus();
    const interval = setInterval(updateStatus, 60000);
    return () => clearInterval(interval);
  }, []);

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: t('nav.dashboard'),
    },
    {
      key: '/analysis',
      icon: <LineChartOutlined />,
      label: t('nav.newAnalysis'),
    },
    {
      key: '/smart-picks',
      icon: <ThunderboltOutlined />,
      label: t('nav.smartPicks') || 'Smart Picks',
    },
    { type: 'divider' as const },
    {
      key: '/watchlist',
      icon: <StarOutlined />,
      label: t('nav.watchlist'),
    },
    {
      key: '/history',
      icon: <HistoryOutlined />,
      label: t('nav.history'),
    },
    {
      key: '/portfolio',
      icon: <WalletOutlined />,
      label: (
        <Space>
          {t('nav.portfolio')}
          {openPositions > 0 && <Badge count={openPositions} size="small" />}
        </Space>
      ),
    },
    {
      key: '/performance',
      icon: <FundOutlined />,
      label: t('nav.performance'),
    },
    { type: 'divider' as const },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: t('nav.settings'),
    },
  ];

  return (
    <Sider
      width={260}
      collapsedWidth={64}
      collapsible
      collapsed={collapsed}
      onCollapse={setCollapsed}
      breakpoint="lg"
      onBreakpoint={(broken) => setCollapsed(broken)}
      style={{
        height: '100vh',
        position: 'fixed',
        insetInlineStart: 0,
        top: 0,
        zIndex: 100,
        borderInlineEnd: '1px solid var(--border)',
        overflow: 'auto',
        background: '#0d1321',
      }}
      theme="dark"
    >
      {/* Logo */}
      <div style={{ padding: collapsed ? '20px 0 16px' : '20px 20px 16px', borderBottom: '1px solid var(--border)', textAlign: collapsed ? 'center' : undefined }}>
        {collapsed ? (
          <RiseOutlined style={{ fontSize: 22, color: 'var(--accent)' }} />
        ) : (
          <>
            <Space align="center" size={8}>
              <RiseOutlined style={{ fontSize: 20, color: 'var(--accent)' }} />
              <Text strong style={{ fontSize: 16, color: 'var(--text)' }}>
                {t('app.title')}
              </Text>
            </Space>
            <div style={{ fontSize: 11, color: 'var(--text3)', marginTop: 2, paddingInlineStart: 28 }}>
              {t('app.subtitle')}
            </div>
          </>
        )}
      </div>

      {/* Navigation */}
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={({ key }) => navigate(key)}
        style={{ background: 'transparent', borderInlineEnd: 'none' }}
      />

      {/* Market Status — above the collapse trigger (48px) */}
      {!collapsed && (
        <div style={{
          position: 'absolute',
          bottom: 48,
          insetInlineStart: 0,
          insetInlineEnd: 0,
          padding: '12px 20px',
          borderTop: '1px solid var(--border)',
          background: '#0d1321',
        }}>
          {Object.entries(MARKETS).map(([id, schedule]) => (
            <div
              key={id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                fontSize: 11,
                color: 'var(--text3)',
                marginBottom: 6,
              }}
            >
              <span
                style={{
                  width: 7,
                  height: 7,
                  borderRadius: '50%',
                  background: marketStatus[id] ? 'var(--green)' : 'var(--red)',
                  flexShrink: 0,
                }}
              />
              <span>{schedule.label}</span>
              <span style={{ marginInlineStart: 'auto', fontSize: 10, opacity: 0.7 }}>
                {marketStatus[id] ? t('market.open') : t('market.closed')}
              </span>
            </div>
          ))}
        </div>
      )}
    </Sider>
  );
}
