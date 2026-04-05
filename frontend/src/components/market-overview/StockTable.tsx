import { useState, useMemo, CSSProperties } from 'react';
import type { StockSnapshot } from '../../types';

interface StockTableProps {
  stocks: StockSnapshot[];
  onSelectStock: (ticker: string, name: string) => void;
  onViewNews?: (ticker: string) => void;
}

const containerStyle: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 12,
};

const searchInputStyle: CSSProperties = {
  padding: '10px 14px',
  background: 'var(--surface2)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  color: 'var(--text)',
  fontSize: 14,
  outline: 'none',
  width: '100%',
  boxSizing: 'border-box',
};

const tableWrapStyle: CSSProperties = {
  overflowX: 'auto',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid var(--border)',
};

const tableStyle: CSSProperties = {
  width: '100%',
  borderCollapse: 'collapse',
  fontSize: 13,
};

const thStyle: CSSProperties = {
  padding: '10px 12px',
  textAlign: 'left',
  fontWeight: 600,
  fontSize: 11,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
  color: 'var(--text3)',
  background: 'var(--surface2)',
  borderBottom: '1px solid var(--border)',
  whiteSpace: 'nowrap',
};

const tdStyle: CSSProperties = {
  padding: '10px 12px',
  borderBottom: '1px solid var(--border)',
  color: 'var(--text)',
  verticalAlign: 'middle',
};

const analyzeBtnStyle: CSSProperties = {
  padding: '4px 12px',
  borderRadius: 'var(--radius-sm)',
  border: 'none',
  background: 'var(--accent)',
  color: '#fff',
  fontSize: 12,
  fontWeight: 600,
  cursor: 'pointer',
  whiteSpace: 'nowrap',
};

const newsBtnStyle: CSSProperties = {
  padding: '4px 8px',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid var(--border)',
  background: 'transparent',
  color: 'var(--text2)',
  fontSize: 14,
  cursor: 'pointer',
  whiteSpace: 'nowrap',
  lineHeight: 1,
  marginRight: 6,
};

const emptyStyle: CSSProperties = {
  padding: 32,
  textAlign: 'center',
  color: 'var(--text3)',
  fontSize: 14,
};

export default function StockTable({ stocks, onSelectStock, onViewNews }: StockTableProps) {
  const [search, setSearch] = useState('');
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  const filtered = useMemo(() => {
    const q = search.toLowerCase().trim();
    const list = q
      ? stocks.filter(
          (s) =>
            s.ticker.toLowerCase().includes(q) ||
            s.name.toLowerCase().includes(q) ||
            (s.name_ar && s.name_ar.includes(q))
        )
      : [...stocks];

    // Sort by change_pct descending
    list.sort((a, b) => b.change_pct - a.change_pct);
    return list;
  }, [stocks, search]);

  function changeColor(val: number): string {
    if (val > 0) return 'var(--green)';
    if (val < 0) return 'var(--red)';
    return 'var(--text3)';
  }

  function formatChange(val: number): string {
    const sign = val > 0 ? '+' : '';
    return `${sign}${val.toFixed(2)}`;
  }

  function formatChangePct(val: number): string {
    const sign = val > 0 ? '+' : '';
    return `${sign}${val.toFixed(2)}%`;
  }

  return (
    <div style={containerStyle}>
      <input
        style={searchInputStyle}
        type="text"
        placeholder="Search by ticker or name..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      <div style={tableWrapStyle}>
        {filtered.length === 0 ? (
          <div style={emptyStyle}>
            {search ? 'No stocks match your search.' : 'No stocks available.'}
          </div>
        ) : (
          <table style={tableStyle}>
            <thead>
              <tr>
                <th style={thStyle}>Ticker</th>
                <th style={thStyle}>Name</th>
                <th style={{ ...thStyle, textAlign: 'right' }}>Price</th>
                <th style={{ ...thStyle, textAlign: 'right' }}>Change</th>
                <th style={{ ...thStyle, textAlign: 'right' }}>Change%</th>
                <th style={thStyle}>Sector</th>
                <th style={{ ...thStyle, textAlign: 'center' }}></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((stock, idx) => (
                <tr
                  key={stock.ticker}
                  style={{
                    cursor: 'pointer',
                    background: hoveredIdx === idx ? 'var(--surface2)' : 'transparent',
                    transition: 'background 0.15s',
                  }}
                  onMouseEnter={() => setHoveredIdx(idx)}
                  onMouseLeave={() => setHoveredIdx(null)}
                  onClick={() => onSelectStock(stock.ticker, stock.name)}
                >
                  <td style={{ ...tdStyle, fontWeight: 700 }}>{stock.ticker}</td>
                  <td style={tdStyle}>
                    <div>{stock.name}</div>
                    {stock.name_ar && (
                      <div style={{ fontSize: 11, color: 'var(--text3)', marginTop: 2 }}>
                        {stock.name_ar}
                      </div>
                    )}
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>
                    {stock.price.toFixed(2)} {stock.currency}
                  </td>
                  <td
                    style={{
                      ...tdStyle,
                      textAlign: 'right',
                      color: changeColor(stock.change),
                      fontVariantNumeric: 'tabular-nums',
                    }}
                  >
                    {formatChange(stock.change)}
                  </td>
                  <td
                    style={{
                      ...tdStyle,
                      textAlign: 'right',
                      color: changeColor(stock.change_pct),
                      fontWeight: 700,
                      fontVariantNumeric: 'tabular-nums',
                    }}
                  >
                    {formatChangePct(stock.change_pct)}
                  </td>
                  <td style={{ ...tdStyle, fontSize: 12, color: 'var(--text2)' }}>
                    {stock.sector}
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'center', whiteSpace: 'nowrap' }}>
                    {onViewNews && (
                      <button
                        style={newsBtnStyle}
                        title={`News for ${stock.ticker}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          onViewNews(stock.ticker);
                        }}
                      >
                        📰
                      </button>
                    )}
                    <button
                      style={analyzeBtnStyle}
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectStock(stock.ticker, stock.name);
                      }}
                    >
                      Analyze
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
