import { NavLink } from 'react-router-dom';
import { useState, useEffect, CSSProperties } from 'react';
import { getPortfolio } from '../../services/api';

const sidebarStyle: CSSProperties = {
  width: 'var(--sidebar-width)',
  height: '100vh',
  position: 'fixed',
  top: 0,
  left: 0,
  background: 'var(--surface)',
  borderRight: '1px solid var(--border)',
  display: 'flex',
  flexDirection: 'column',
  zIndex: 100,
  overflow: 'hidden',
};

const logoSection: CSSProperties = {
  padding: '20px 20px 16px',
  borderBottom: '1px solid var(--border)',
};

const logoTitle: CSSProperties = {
  fontSize: 16,
  fontWeight: 700,
  color: 'var(--text)',
  display: 'flex',
  alignItems: 'center',
  gap: 8,
};

const logoSub: CSSProperties = {
  fontSize: 11,
  color: 'var(--text3)',
  marginTop: 2,
  paddingLeft: 26,
};

const navSection: CSSProperties = {
  flex: 1,
  overflowY: 'auto',
  padding: '12px 0',
};

const sectionLabel: CSSProperties = {
  fontSize: 10,
  fontWeight: 600,
  textTransform: 'uppercase' as const,
  letterSpacing: '0.08em',
  color: 'var(--text3)',
  padding: '16px 20px 6px',
};

const navItemBase: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 10,
  padding: '9px 20px',
  fontSize: 13,
  fontWeight: 500,
  color: 'var(--text2)',
  textDecoration: 'none',
  borderRadius: 0,
  transition: 'background 0.15s, color 0.15s',
};

const navItemActive: CSSProperties = {
  ...navItemBase,
  color: 'var(--accent)',
  background: 'rgba(59, 130, 246, 0.08)',
  borderRight: '2px solid var(--accent)',
};

const bottomSection: CSSProperties = {
  padding: '12px 20px',
  borderTop: '1px solid var(--border)',
  display: 'flex',
  flexDirection: 'column',
  gap: 8,
};

const marketRowStyle: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 8,
  fontSize: 11,
  color: 'var(--text3)',
};

function statusDot(isOpen: boolean): CSSProperties {
  return {
    width: 7,
    height: 7,
    borderRadius: '50%',
    background: isOpen ? 'var(--green)' : 'var(--red)',
    flexShrink: 0,
  };
}

interface NavItem {
  to: string;
  icon: string;
  label: string;
}

const marketItems: NavItem[] = [
  { to: '/', icon: '📊', label: 'New Analysis' },
];

const analysisItems: NavItem[] = [
  { to: '/history', icon: '📋', label: 'History' },
  { to: '/portfolio', icon: '💰', label: 'Portfolio' },
  { to: '/performance', icon: '📈', label: 'Performance' },
];

const settingsItems: NavItem[] = [
  { to: '/settings', icon: '⚙️', label: 'Settings' },
];

const badgeStyle: CSSProperties = {
  minWidth: 18,
  height: 18,
  borderRadius: 9,
  background: 'var(--accent)',
  color: '#fff',
  fontSize: 10,
  fontWeight: 700,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: '0 5px',
  marginLeft: 'auto',
};

// Market schedule definitions (mirrors backend MARKET_REGIONS)
interface MarketSchedule {
  label: string;
  weekendDays: number[]; // JS: 0=Sun, 1=Mon, ..., 6=Sat
  openHour: number;
  closeHour: number;
  timezone: string; // IANA timezone for correct local time
}

const MARKETS: Record<string, MarketSchedule> = {
  us: {
    label: 'US (NYSE/NASDAQ)',
    weekendDays: [0, 6], // Sun, Sat (JS convention)
    openHour: 9,
    closeHour: 16,
    timezone: 'America/New_York',
  },
  egypt: {
    label: 'Egypt (EGX)',
    weekendDays: [5, 6], // Fri, Sat (JS convention)
    openHour: 10,
    closeHour: 15,
    timezone: 'Africa/Cairo',
  },
};

function isMarketOpen(schedule: MarketSchedule): boolean {
  // Get current time in the market's timezone
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

  // Map weekday string to number (JS convention: 0=Sun)
  const dayMap: Record<string, number> = {
    Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6,
  };
  const dayNum = dayMap[weekday] ?? now.getDay();

  if (schedule.weekendDays.includes(dayNum)) return false;
  return hour >= schedule.openHour && hour < schedule.closeHour;
}

function renderNavItem(item: NavItem, badge?: number) {
  return (
    <NavLink
      key={item.to}
      to={item.to}
      end={item.to === '/'}
      style={({ isActive }) => (isActive ? navItemActive : navItemBase)}
    >
      <span style={{ fontSize: 16, width: 20, textAlign: 'center' }}>{item.icon}</span>
      {item.label}
      {badge != null && badge > 0 && <span style={badgeStyle}>{badge}</span>}
    </NavLink>
  );
}

export default function Sidebar() {
  const [openPositions, setOpenPositions] = useState<number>(0);
  const [marketStatus, setMarketStatus] = useState<Record<string, boolean>>({});

  useEffect(() => {
    let cancelled = false;
    function fetchCount() {
      getPortfolio()
        .then((p) => {
          if (!cancelled) setOpenPositions(p.open_positions_count);
        })
        .catch(() => {
          /* ignore */
        });
    }
    fetchCount();
    const interval = setInterval(fetchCount, 60000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  // Update market status every minute
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

  return (
    <aside style={sidebarStyle}>
      <div style={logoSection}>
        <div style={logoTitle}>
          <span style={{ fontSize: 20 }}>📈</span>
          TradingAgents
        </div>
        <div style={logoSub}>AI Analysis Platform</div>
      </div>

      <nav style={navSection}>
        <div style={sectionLabel}>Markets</div>
        {marketItems.map(renderNavItem)}

        <div style={sectionLabel}>Analysis</div>
        {analysisItems.map((item) =>
          renderNavItem(item, item.to === '/portfolio' ? openPositions : undefined)
        )}

        <div style={sectionLabel}>System</div>
        {settingsItems.map(renderNavItem)}
      </nav>

      <div style={bottomSection}>
        {Object.entries(MARKETS).map(([id, schedule]) => (
          <div key={id} style={marketRowStyle}>
            <span style={statusDot(marketStatus[id] ?? false)} />
            <span>{schedule.label}</span>
            <span style={{ marginLeft: 'auto', fontSize: 10, opacity: 0.7 }}>
              {marketStatus[id] ? 'Open' : 'Closed'}
            </span>
          </div>
        ))}
      </div>
    </aside>
  );
}
