import { CSSProperties } from 'react';
import { useMarketStore } from '../../stores/marketStore';

interface TopbarProps {
  title: string;
}

const topbarStyle: CSSProperties = {
  height: 'var(--topbar-height)',
  position: 'sticky',
  top: 0,
  background: 'var(--surface)',
  borderBottom: '1px solid var(--border)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: '0 24px',
  zIndex: 50,
};

const titleStyle: CSSProperties = {
  fontSize: 16,
  fontWeight: 600,
  color: 'var(--text)',
};

const rightSection: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 10,
};

const badgeBase: CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 5,
  padding: '4px 10px',
  borderRadius: 'var(--radius-sm)',
  fontSize: 11,
  fontWeight: 500,
};

const marketBadge: CSSProperties = {
  ...badgeBase,
  background: 'rgba(59, 130, 246, 0.10)',
  color: 'var(--accent)',
};

const versionBadge: CSSProperties = {
  ...badgeBase,
  background: 'rgba(139, 92, 246, 0.10)',
  color: 'var(--accent2)',
};

export default function Topbar({ title }: TopbarProps) {
  const marketLabel = useMarketStore((s) => s.marketLabel);

  return (
    <header style={topbarStyle}>
      <h1 style={titleStyle}>{title}</h1>
      <div style={rightSection}>
        <span style={marketBadge}>{marketLabel}</span>
        <span style={versionBadge}>v0.1.0</span>
      </div>
    </header>
  );
}
