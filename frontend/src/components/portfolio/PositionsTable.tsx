import { useState } from 'react';
import type { CSSProperties } from 'react';
import { closePosition } from '../../services/api';
import type { PositionResponse } from '../../types';
import { ValueFlash } from '../../motion';

interface PositionsTableProps {
  positions: PositionResponse[];
  onRefresh: () => void;
}

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

const closeBtnStyle: CSSProperties = {
  padding: '5px 12px',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid var(--border)',
  background: 'transparent',
  color: 'var(--text2)',
  fontSize: 12,
  cursor: 'pointer',
  fontWeight: 500,
};

const confirmRow: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 8,
  fontSize: 12,
};

const confirmBtnStyle: CSSProperties = {
  padding: '4px 10px',
  borderRadius: 'var(--radius-sm)',
  border: 'none',
  background: '#ef4444',
  color: '#fff',
  fontSize: 11,
  fontWeight: 600,
  cursor: 'pointer',
};

const cancelBtnStyle: CSSProperties = {
  padding: '4px 10px',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid var(--border)',
  background: 'transparent',
  color: 'var(--text3)',
  fontSize: 11,
  cursor: 'pointer',
};

const toastStyle: CSSProperties = {
  position: 'fixed',
  bottom: 24,
  right: 24,
  padding: '12px 20px',
  background: 'rgba(34,197,94,0.15)',
  border: '1px solid rgba(34,197,94,0.3)',
  borderRadius: 'var(--radius-sm)',
  color: '#22c55e',
  fontSize: 13,
  fontWeight: 600,
  zIndex: 2000,
};

export default function PositionsTable({ positions, onRefresh }: PositionsTableProps) {
  const [closingId, setClosingId] = useState<string | null>(null);
  const [loadingClose, setLoadingClose] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [closeError, setCloseError] = useState<string | null>(null);

  async function handleClose(id: string) {
    setLoadingClose(true);
    setCloseError(null);
    try {
      const res = await closePosition(id);
      const sign = res.realized_pnl >= 0 ? '+' : '';
      setToast(`Closed ${res.ticker}: ${sign}$${res.realized_pnl.toFixed(2)} (${sign}${res.realized_pnl_pct.toFixed(2)}%)`);
      setClosingId(null);
      onRefresh();
      setTimeout(() => setToast(null), 3000);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to close position';
      setCloseError(message);
    } finally {
      setLoadingClose(false);
    }
  }

  if (positions.length === 0) {
    return (
      <div style={emptyStyle}>
        <div style={{ fontSize: 32, marginBottom: 12 }}>📭</div>
        <div>No open positions. Run an analysis and execute a trade!</div>
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
            <th style={thStyle}>Current</th>
            <th style={thStyle}>P&L</th>
            <th style={thStyle}>P&L%</th>
            <th style={thStyle}>Days</th>
            <th style={thStyle}>Rec.</th>
            <th style={thStyle}>Action</th>
          </tr>
        </thead>
        <tbody>
          {positions.map((pos) => (
            <tr key={pos.id} className="hover-row">
              <td style={{ ...tdStyle, fontWeight: 700, color: 'var(--text)' }}>{pos.ticker}</td>
              <td style={tdStyle}><span style={marketTag}>{pos.market_id}</span></td>
              <td style={tdStyle}><span style={dirBadge(pos.direction)}>{pos.direction.toUpperCase()}</span></td>
              <td style={tdStyle}>{pos.quantity}</td>
              <td style={tdStyle}>${pos.entry_price.toFixed(2)}</td>
              <td style={tdStyle}>$<ValueFlash value={pos.current_price} decimals={2} /></td>
              <td style={{ ...tdStyle, color: pnlColor(pos.unrealized_pnl), fontWeight: 600 }}>
                {pos.unrealized_pnl >= 0 ? '+' : ''}$<ValueFlash value={pos.unrealized_pnl} decimals={2} />
              </td>
              <td style={{ ...tdStyle, color: pnlColor(pos.unrealized_pnl_pct), fontWeight: 700 }}>
                {pos.unrealized_pnl_pct >= 0 ? '+' : ''}{pos.unrealized_pnl_pct.toFixed(2)}%
              </td>
              <td style={tdStyle}>{pos.days_held}</td>
              <td style={tdStyle}>
                {pos.recommendation && <span style={recBadge(pos.recommendation)}>{pos.recommendation}</span>}
              </td>
              <td style={tdStyle}>
                {closingId === pos.id ? (
                  <div style={confirmRow}>
                    <span style={{ color: 'var(--text3)' }}>
                      Close at ${pos.current_price.toFixed(2)}? P&L: <span style={{ color: pnlColor(pos.unrealized_pnl) }}>
                        {pos.unrealized_pnl >= 0 ? '+' : ''}${pos.unrealized_pnl.toFixed(2)}
                      </span>
                    </span>
                    <button
                      style={confirmBtnStyle}
                      onClick={() => handleClose(pos.id)}
                      disabled={loadingClose}
                    >
                      {loadingClose ? '...' : 'Confirm'}
                    </button>
                    <button style={cancelBtnStyle} onClick={() => { setClosingId(null); setCloseError(null); }}>
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button style={closeBtnStyle} onClick={() => setClosingId(pos.id)}>
                    Close
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {closeError && (
        <div style={{ padding: 10, color: '#ef4444', fontSize: 12, textAlign: 'center', marginTop: 8 }}>
          {closeError}
        </div>
      )}

      {toast && <div style={toastStyle}>{toast}</div>}
    </div>
  );
}
