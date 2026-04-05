import { CSSProperties } from 'react';
import type { MarketSummaryData } from '../../types';

interface MarketSummaryBarProps {
  summary: MarketSummaryData;
}

const rowStyle: CSSProperties = {
  display: 'flex',
  gap: 10,
  marginBottom: 16,
  flexWrap: 'wrap',
};

function chipStyle(color?: string): CSSProperties {
  return {
    padding: '5px 12px',
    background: 'var(--surface2)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-sm)',
    fontSize: 12,
    fontWeight: 600,
    color: color || 'var(--text2)',
    fontVariantNumeric: 'tabular-nums',
    whiteSpace: 'nowrap',
  };
}

export default function MarketSummaryBar({ summary }: MarketSummaryBarProps) {
  return (
    <div style={rowStyle}>
      <span style={chipStyle()}>Stocks: {summary.total_stocks}</span>
      <span style={chipStyle('var(--green)')}>Gainers: {summary.gainers_count}</span>
      <span style={chipStyle('var(--red)')}>Losers: {summary.losers_count}</span>
      <span style={chipStyle()}>Breadth: {summary.breadth_pct.toFixed(1)}%</span>
    </div>
  );
}
