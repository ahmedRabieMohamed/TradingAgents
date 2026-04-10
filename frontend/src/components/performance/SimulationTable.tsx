import type { CSSProperties } from 'react';

export interface SimulationRow {
  id: string;
  ticker: string;
  stock_name: string;
  market_id: string;
  recommendation: string | null;
  entry_price: number;
  exit_price: number;
  return_pct: number;
  is_win: boolean;
}

interface SimulationTableProps {
  rows: SimulationRow[];
}

const wrapperStyle: CSSProperties = {
  background: 'var(--surface2)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-lg)',
  overflow: 'hidden',
};

const headerStyle: CSSProperties = {
  padding: '16px 20px',
  fontSize: 14,
  fontWeight: 600,
  color: 'var(--text)',
  borderBottom: '1px solid var(--border)',
};

const tableStyle: CSSProperties = {
  width: '100%',
  borderCollapse: 'collapse',
  fontSize: 13,
};

const thStyle: CSSProperties = {
  textAlign: 'left',
  padding: '10px 16px',
  fontSize: 11,
  fontWeight: 600,
  color: 'var(--text3)',
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
  borderBottom: '1px solid var(--border)',
};

const tdStyle: CSSProperties = {
  padding: '10px 16px',
  color: 'var(--text2)',
  borderBottom: '1px solid var(--border)',
};

const returnStyle = (pct: number): CSSProperties => ({
  ...tdStyle,
  fontWeight: 600,
  color: pct > 0 ? 'var(--green)' : pct < 0 ? 'var(--red)' : 'var(--text2)',
});

const tagStyle = (rec: string | null): CSSProperties => {
  const r = (rec || '').toUpperCase();
  let bg = 'rgba(245, 158, 11, 0.12)';
  let color = 'var(--yellow)';
  if (r === 'BUY') { bg = 'rgba(16, 185, 129, 0.12)'; color = 'var(--green)'; }
  if (r === 'SELL') { bg = 'rgba(239, 68, 68, 0.12)'; color = 'var(--red)'; }
  return {
    display: 'inline-block',
    padding: '2px 10px',
    borderRadius: 12,
    fontSize: 12,
    fontWeight: 500,
    background: bg,
    color,
  };
};

const correctStyle = (win: boolean): CSSProperties => ({
  ...tdStyle,
  fontWeight: 600,
  color: win ? 'var(--green)' : 'var(--red)',
});

export default function SimulationTable({ rows }: SimulationTableProps) {
  if (rows.length === 0) {
    return null;
  }

  return (
    <div style={wrapperStyle}>
      <div style={headerStyle}>Simulation Results</div>
      <div style={{ overflowX: 'auto' }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>Stock</th>
              <th style={thStyle}>Market</th>
              <th style={thStyle}>Signal</th>
              <th style={{ ...thStyle, textAlign: 'right' }}>Entry</th>
              <th style={{ ...thStyle, textAlign: 'right' }}>Exit</th>
              <th style={{ ...thStyle, textAlign: 'right' }}>Return %</th>
              <th style={{ ...thStyle, textAlign: 'center' }}>Correct</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id}>
                <td style={tdStyle}>
                  <span style={{ fontWeight: 600, color: 'var(--text)' }}>{row.ticker}</span>
                  {row.stock_name && (
                    <span style={{ marginLeft: 6, color: 'var(--text3)', fontSize: 12 }}>
                      {row.stock_name}
                    </span>
                  )}
                </td>
                <td style={tdStyle}>
                  <span style={{ textTransform: 'uppercase', fontSize: 12 }}>{row.market_id}</span>
                </td>
                <td style={tdStyle}>
                  <span style={tagStyle(row.recommendation)}>{row.recommendation || '-'}</span>
                </td>
                <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'monospace' }}>
                  {row.entry_price.toFixed(2)}
                </td>
                <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'monospace' }}>
                  {row.exit_price.toFixed(2)}
                </td>
                <td style={{ ...returnStyle(row.return_pct), textAlign: 'right', fontFamily: 'monospace' }}>
                  {row.return_pct > 0 ? '+' : ''}{row.return_pct.toFixed(2)}%
                </td>
                <td style={{ ...correctStyle(row.is_win), textAlign: 'center' }}>
                  {row.is_win ? 'Yes' : 'No'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
