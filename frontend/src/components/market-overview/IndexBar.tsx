import { CSSProperties } from 'react';
import type { IndexData } from '../../types';

interface IndexBarProps {
  indices: IndexData[];
}

const gridStyle: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
  gap: 12,
  marginBottom: 16,
};

const cardStyle: CSSProperties = {
  padding: '14px 16px',
  background: 'var(--surface2)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
};

const nameStyle: CSSProperties = {
  fontSize: 11,
  color: 'var(--text3)',
  fontWeight: 500,
  textTransform: 'uppercase',
  letterSpacing: '0.3px',
  marginBottom: 4,
};

const valueStyle: CSSProperties = {
  fontSize: 20,
  fontWeight: 700,
  color: 'var(--text)',
  fontVariantNumeric: 'tabular-nums',
  marginBottom: 4,
};

function changeRowStyle(positive: boolean): CSSProperties {
  return {
    fontSize: 13,
    fontWeight: 600,
    color: positive ? 'var(--green)' : 'var(--red)',
    fontVariantNumeric: 'tabular-nums',
  };
}

function formatValue(val: number): string {
  return val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatChange(val: number): string {
  const sign = val >= 0 ? '+' : '';
  return `${sign}${val.toFixed(2)}`;
}

function formatChangePct(val: number): string {
  const sign = val >= 0 ? '+' : '';
  return `(${sign}${val.toFixed(2)}%)`;
}

export default function IndexBar({ indices }: IndexBarProps) {
  if (!indices || indices.length === 0) return null;

  return (
    <div style={gridStyle}>
      {indices.map((idx) => {
        const positive = idx.change >= 0;
        return (
          <div key={idx.symbol} style={cardStyle}>
            <div style={nameStyle}>{idx.name}</div>
            <div style={valueStyle}>{formatValue(idx.value)}</div>
            <div style={changeRowStyle(positive)}>
              {formatChange(idx.change)} {formatChangePct(idx.change_pct)}
            </div>
          </div>
        );
      })}
    </div>
  );
}
