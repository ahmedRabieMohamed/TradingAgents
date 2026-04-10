import { useState, useEffect } from 'react';
import type { CSSProperties } from 'react';
import { getTradeHistory } from '../../services/api';
import type { TradeHistoryItem } from '../../types';

const tableContainer: CSSProperties = {
  overflowX: 'auto',
};

const tableStyle: CSSProperties = {
  width: '100%',
  borderCollapse: 'collapse',
  fontSize: 13,
};

const thStyle: CSSProperties = {
  textAlign: 'left',
  padding: '10px 12px',
  fontSize: 11,
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  color: 'var(--text3)',
  borderBottom: '1px solid var(--border)',
  whiteSpace: 'nowrap',
};

const tdStyle: CSSProperties = {
  padding: '10px 12px',
  borderBottom: '1px solid var(--border)',
  color: 'var(--text2)',
  whiteSpace: 'nowrap',
};

const emptyStyle: CSSProperties = {
  textAlign: 'center',
  padding: 48,
  color: 'var(--text3)',
  fontSize: 14,
};

const loadingStyle: CSSProperties = {
  textAlign: 'center',
  padding: 48,
  color: 'var(--text3)',
  fontSize: 14,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 8,
};

function pnlColor(v: number): string {
  if (v > 0) return '#22c55e';
  if (v < 0) return '#ef4444';
  return 'var(--text2)';
}

const dirBadge = (dir: string): CSSProperties => ({
  display: 'inline-block',
  padding: '2px 8px',
  borderRadius: 'var(--radius-sm)',
  fontSize: 11,
  fontWeight: 600,
  color: dir === 'long' ? '#22c55e' : '#ef4444',
  background: dir === 'long' ? 'rgba(34,197,94,0.12)' : 'rgba(239,68,68,0.12)',
});

const recBadge = (rec: string | null): CSSProperties => {
  if (!rec) return { display: 'none' };
  const upper = rec.toUpperCase();
  const color = upper === 'BUY' ? '#22c55e' : upper === 'SELL' ? '#ef4444' : '#eab308';
  return {
    display: 'inline-block',
    padding: '2px 8px',
    borderRadius: 'var(--radius-sm)',
    fontSize: 11,
    fontWeight: 600,
    color: '#fff',
    background: color,
  };
};

const marketTag: CSSProperties = {
  display: 'inline-block',
  padding: '2px 6px',
  borderRadius: 'var(--radius-sm)',
  fontSize: 10,
  fontWeight: 600,
  color: 'var(--text3)',
  background: 'var(--surface2)',
  border: '1px solid var(--border)',
  textTransform: 'uppercase',
};

export default function TradeHistory() {
  const [trades, setTrades] = useState<TradeHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getTradeHistory()
      .then((res) => setTrades(res.trades))
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : 'Failed to load trade history';
        setError(message);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div style={loadingStyle}>
        <span className="spinner" />
        Loading trade history...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ ...emptyStyle, color: '#ef4444' }}>
        {error}
      </div>
    );
  }

  if (trades.length === 0) {
    return (
      <div style={emptyStyle}>
        <div style={{ fontSize: 32, marginBottom: 12 }}>📊</div>
        <div>No closed trades yet. Close a position to see it here.</div>
      </div>
    );
  }

  return (
    <div style={tableContainer}>
      <table style={tableStyle}>
        <thead>
          <tr>
            <th style={thStyle}>Ticker</th>
            <th style={thStyle}>Market</th>
            <th style={thStyle}>Direction</th>
            <th style={thStyle}>Qty</th>
            <th style={thStyle}>Entry</th>
            <th style={thStyle}>Exit</th>
            <th style={thStyle}>P&L</th>
            <th style={thStyle}>Return%</th>
            <th style={thStyle}>Hold Days</th>
            <th style={thStyle}>AI Rec.</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade) => (
            <tr key={trade.id}>
              <td style={{ ...tdStyle, fontWeight: 700, color: 'var(--text)' }}>{trade.ticker}</td>
              <td style={tdStyle}><span style={marketTag}>{trade.market_id}</span></td>
              <td style={tdStyle}><span style={dirBadge(trade.direction)}>{trade.direction.toUpperCase()}</span></td>
              <td style={tdStyle}>{trade.quantity}</td>
              <td style={tdStyle}>${trade.entry_price.toFixed(2)}</td>
              <td style={tdStyle}>${trade.exit_price.toFixed(2)}</td>
              <td style={{ ...tdStyle, color: pnlColor(trade.realized_pnl), fontWeight: 600 }}>
                {trade.realized_pnl >= 0 ? '+' : ''}${trade.realized_pnl.toFixed(2)}
              </td>
              <td style={{ ...tdStyle, color: pnlColor(trade.realized_pnl_pct), fontWeight: 700 }}>
                {trade.realized_pnl_pct >= 0 ? '+' : ''}{trade.realized_pnl_pct.toFixed(2)}%
              </td>
              <td style={tdStyle}>{trade.hold_days}</td>
              <td style={tdStyle}>
                {trade.recommendation && <span style={recBadge(trade.recommendation)}>{trade.recommendation}</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
