import type { CSSProperties } from 'react';
import type { MarketPerformance, HorizonPerformance } from '../../types';

interface MarketPerfProps {
  byMarket: Record<string, MarketPerformance>;
  byHorizon: Record<string, HorizonPerformance>;
}

const containerStyle: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: '1fr 1fr',
  gap: 16,
};

const cardStyle: CSSProperties = {
  background: 'var(--surface2)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-lg)',
  padding: 20,
};

const titleStyle: CSSProperties = {
  fontSize: 14,
  fontWeight: 600,
  color: 'var(--text)',
  marginBottom: 16,
};

const rowStyle: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  marginBottom: 12,
};

const nameStyle: CSSProperties = {
  fontSize: 13,
  fontWeight: 500,
  color: 'var(--text2)',
  minWidth: 80,
};

const barOuterStyle: CSSProperties = {
  flex: 1,
  height: 8,
  background: 'var(--border)',
  borderRadius: 4,
  margin: '0 12px',
  overflow: 'hidden',
};

const barInnerStyle = (pct: number): CSSProperties => ({
  height: '100%',
  width: `${Math.min(pct, 100)}%`,
  background: 'var(--green)',
  borderRadius: 4,
  transition: 'width 0.4s ease',
});

const pctStyle: CSSProperties = {
  fontSize: 13,
  fontWeight: 600,
  color: 'var(--text)',
  minWidth: 48,
  textAlign: 'right',
};

function formatLabel(key: string): string {
  return key
    .replace(/-/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function MarketPerf({ byMarket, byHorizon }: MarketPerfProps) {
  const marketEntries = Object.entries(byMarket);
  const horizonEntries = Object.entries(byHorizon);

  const hasData = marketEntries.length > 0 || horizonEntries.length > 0;

  if (!hasData) {
    return null;
  }

  return (
    <div style={containerStyle}>
      <div style={cardStyle}>
        <div style={titleStyle}>By Market</div>
        {marketEntries.length === 0 && (
          <div style={{ fontSize: 13, color: 'var(--text3)' }}>No data yet</div>
        )}
        {marketEntries.map(([key, data]) => (
          <div key={key} style={rowStyle}>
            <span style={nameStyle}>{formatLabel(key)}</span>
            <div style={barOuterStyle}>
              <div style={barInnerStyle(data.win_rate)} />
            </div>
            <span style={pctStyle}>{data.win_rate}%</span>
          </div>
        ))}
      </div>

      <div style={cardStyle}>
        <div style={titleStyle}>By Horizon</div>
        {horizonEntries.length === 0 && (
          <div style={{ fontSize: 13, color: 'var(--text3)' }}>No data yet</div>
        )}
        {horizonEntries.map(([key, data]) => (
          <div key={key} style={rowStyle}>
            <span style={nameStyle}>{formatLabel(key)}</span>
            <div style={barOuterStyle}>
              <div style={barInnerStyle(data.win_rate)} />
            </div>
            <span style={pctStyle}>{data.win_rate}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
