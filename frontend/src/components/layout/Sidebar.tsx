import { NavLink } from 'react-router-dom';
import { useState, useEffect, CSSProperties } from 'react';
import { useMarketStore } from '../../stores/marketStore';
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
  padding: '16px 20px',
  borderTop: '1px solid var(--border)',
  fontSize: 12,
  color: 'var(--text3)',
  display: 'flex',
  alignItems: 'center',
  gap: 8,
};

const marketDot: CSSProperties = {
  width: 8,
  height: 8,
  borderRadius: '50%',
  background: 'var(--green)',
};

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
  const marketLabel = useMarketStore((s) => s.marketLabel);
  const [openPositions, setOpenPositions] = useState<number>(0);

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
        <span style={marketDot} />
        {marketLabel}
      </div>
    </aside>
  );
}
