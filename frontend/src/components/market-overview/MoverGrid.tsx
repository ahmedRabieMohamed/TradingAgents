import { useState, CSSProperties } from 'react';
import type { StockSnapshot } from '../../types';

interface MoverGridProps {
  gainers: StockSnapshot[];
  losers: StockSnapshot[];
  onSelectStock: (ticker: string, name: string) => void;
}

const gridStyle: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: '1fr 1fr',
  gap: 16,
};

const cardStyle: CSSProperties = {
  background: 'var(--surface)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  overflow: 'hidden',
};

function headerStyle(color: string): CSSProperties {
  return {
    padding: '10px 14px',
    fontSize: 14,
    fontWeight: 700,
    color: '#fff',
    background: color,
  };
}

const rowBaseStyle: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 10,
  padding: '8px 14px',
  cursor: 'pointer',
  transition: 'background 0.15s',
  borderBottom: '1px solid var(--border)',
};

const tickerStyle: CSSProperties = {
  fontWeight: 700,
  fontSize: 13,
  color: 'var(--text)',
  minWidth: 60,
};

const nameStyle: CSSProperties = {
  fontSize: 12,
  color: 'var(--text2)',
  flex: 1,
  overflow: 'hidden',
  textOverflow: 'ellipsis',
  whiteSpace: 'nowrap',
};

const priceStyle: CSSProperties = {
  fontSize: 12,
  color: 'var(--text)',
  fontVariantNumeric: 'tabular-nums',
  marginRight: 8,
};

function badgeStyle(isGainer: boolean): CSSProperties {
  return {
    padding: '2px 8px',
    borderRadius: 10,
    fontSize: 11,
    fontWeight: 700,
    color: '#fff',
    background: isGainer ? 'var(--green)' : 'var(--red)',
    whiteSpace: 'nowrap',
    fontVariantNumeric: 'tabular-nums',
  };
}

const emptyRowStyle: CSSProperties = {
  padding: '20px 14px',
  textAlign: 'center',
  color: 'var(--text3)',
  fontSize: 13,
};

function MoverCard({
  title,
  stocks,
  color,
  isGainer,
  onSelectStock,
}: {
  title: string;
  stocks: StockSnapshot[];
  color: string;
  isGainer: boolean;
  onSelectStock: (ticker: string, name: string) => void;
}) {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);
  const display = stocks.slice(0, 7);

  return (
    <div style={cardStyle}>
      <div style={headerStyle(color)}>{title}</div>
      {display.length === 0 ? (
        <div style={emptyRowStyle}>No data available</div>
      ) : (
        display.map((stock, idx) => (
          <div
            key={stock.ticker}
            style={{
              ...rowBaseStyle,
              background: hoveredIdx === idx ? 'var(--surface2)' : 'transparent',
            }}
            onMouseEnter={() => setHoveredIdx(idx)}
            onMouseLeave={() => setHoveredIdx(null)}
            onClick={() => onSelectStock(stock.ticker, stock.name)}
          >
            <span style={tickerStyle}>{stock.ticker}</span>
            <span style={nameStyle}>{stock.name}</span>
            <span style={priceStyle}>{stock.price.toFixed(2)}</span>
            <span style={badgeStyle(isGainer)}>
              {stock.change_pct > 0 ? '+' : ''}
              {stock.change_pct.toFixed(2)}%
            </span>
          </div>
        ))
      )}
    </div>
  );
}

export default function MoverGrid({ gainers, losers, onSelectStock }: MoverGridProps) {
  return (
    <div style={gridStyle}>
      <MoverCard
        title="Top Gainers"
        stocks={gainers}
        color="var(--green)"
        isGainer={true}
        onSelectStock={onSelectStock}
      />
      <MoverCard
        title="Top Losers"
        stocks={losers}
        color="var(--red)"
        isGainer={false}
        onSelectStock={onSelectStock}
      />
    </div>
  );
}
