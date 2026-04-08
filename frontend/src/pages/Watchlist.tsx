import { useEffect, useState, CSSProperties } from 'react';
import { useNavigate } from 'react-router-dom';
import Topbar from '../components/layout/Topbar';
import { getWatchlist, addToWatchlist, removeFromWatchlist, validateStock } from '../services/api';
import type { WatchlistItem } from '../types';

const pageStyle: CSSProperties = { padding: 24, maxWidth: 900 };

const cardStyle: CSSProperties = {
  background: 'var(--surface)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-md)',
  overflow: 'hidden',
  boxShadow: 'var(--shadow-sm)',
};

const tableStyle: CSSProperties = {
  width: '100%',
  borderCollapse: 'collapse',
  fontSize: 13,
};

const thStyle: CSSProperties = {
  textAlign: 'left',
  padding: '10px 14px',
  borderBottom: '1px solid var(--border)',
  color: 'var(--text3)',
  fontSize: 11,
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.04em',
};

const tdStyle: CSSProperties = {
  padding: '12px 14px',
  borderBottom: '1px solid var(--border)',
  color: 'var(--text)',
};

const addBarStyle: CSSProperties = {
  display: 'flex',
  gap: 8,
  marginBottom: 20,
  alignItems: 'center',
};

const inputStyle: CSSProperties = {
  padding: '8px 12px',
  background: 'var(--surface)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  color: 'var(--text)',
  fontSize: 13,
  outline: 'none',
};

const btnStyle: CSSProperties = {
  padding: '8px 16px',
  borderRadius: 'var(--radius-sm)',
  border: 'none',
  background: 'var(--accent)',
  color: '#fff',
  fontSize: 13,
  fontWeight: 600,
  cursor: 'pointer',
};

const removeBtnStyle: CSSProperties = {
  padding: '4px 10px',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid var(--border)',
  background: 'transparent',
  color: 'var(--text3)',
  fontSize: 11,
  cursor: 'pointer',
};

const selectStyle: CSSProperties = {
  ...inputStyle,
  cursor: 'pointer',
};

const pnlColor = (v: number | null) =>
  v == null ? 'var(--text3)' : v >= 0 ? 'var(--green)' : 'var(--red)';

export default function WatchlistPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [ticker, setTicker] = useState('');
  const [market, setMarket] = useState('us');
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function fetchItems() {
    getWatchlist()
      .then((res) => setItems(res.items))
      .catch(() => {})
      .finally(() => setLoading(false));
  }

  useEffect(() => { fetchItems(); }, []);

  async function handleAdd() {
    if (!ticker.trim()) return;
    setAdding(true);
    setError(null);

    try {
      // Validate ticker first
      const validated = await validateStock(ticker.trim(), market);
      await addToWatchlist(validated.ticker, market, validated.name);
      setTicker('');
      fetchItems();
    } catch (err: any) {
      const msg = err?.message || 'Failed to add ticker';
      setError(msg.includes('409') ? 'Already in watchlist' : msg.includes('404') ? 'Invalid ticker' : msg);
    } finally {
      setAdding(false);
    }
  }

  async function handleRemove(id: string) {
    await removeFromWatchlist(id).catch(() => {});
    setItems((prev) => prev.filter((i) => i.id !== id));
  }

  if (loading) {
    return (
      <>
        <Topbar title="Watchlist" />
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', gap: 8, color: 'var(--text3)' }}>
          <span className="spinner" />
          Loading watchlist...
        </div>
      </>
    );
  }

  return (
    <>
      <Topbar title="Watchlist" />
      <div style={pageStyle}>
        {/* Add bar */}
        <div style={addBarStyle}>
          <select style={selectStyle} value={market} onChange={(e) => setMarket(e.target.value)}>
            <option value="us">US</option>
            <option value="egypt">Egypt</option>
          </select>
          <input
            style={{ ...inputStyle, flex: 1 }}
            placeholder="Enter ticker symbol (e.g. AAPL, COMI)"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
          />
          <button style={btnStyle} onClick={handleAdd} disabled={adding}>
            {adding ? 'Adding...' : '+ Add'}
          </button>
        </div>

        {error && (
          <div style={{ padding: 10, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 'var(--radius-sm)', color: '#ef4444', fontSize: 12, marginBottom: 16 }}>
            {error}
          </div>
        )}

        {items.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 60, color: 'var(--text3)' }}>
            <div style={{ fontSize: 36, marginBottom: 12 }}>⭐</div>
            <div style={{ fontSize: 14, color: 'var(--text2)' }}>Your watchlist is empty</div>
            <div style={{ fontSize: 12, marginTop: 4 }}>Add tickers above to track them.</div>
          </div>
        ) : (
          <div style={cardStyle}>
            <table style={tableStyle}>
              <thead>
                <tr>
                  <th style={thStyle}>Ticker</th>
                  <th style={thStyle}>Name</th>
                  <th style={thStyle}>Market</th>
                  <th style={thStyle}>Price</th>
                  <th style={thStyle}>Change</th>
                  <th style={thStyle}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id} className="hover-row">
                    <td style={{ ...tdStyle, fontWeight: 700 }}>{item.ticker}</td>
                    <td style={{ ...tdStyle, color: 'var(--text2)' }}>{item.name || '—'}</td>
                    <td style={tdStyle}>{item.market_id === 'egypt' ? 'EGX' : 'US'}</td>
                    <td style={tdStyle}>
                      {item.price != null
                        ? `${item.currency === 'EGP' ? 'E£' : '$'}${item.price.toFixed(2)}`
                        : '—'}
                    </td>
                    <td style={{ ...tdStyle, color: pnlColor(item.change_pct), fontWeight: 600 }}>
                      {item.change_pct != null
                        ? `${item.change_pct >= 0 ? '+' : ''}${item.change_pct.toFixed(2)}%`
                        : '—'}
                    </td>
                    <td style={tdStyle}>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button
                          style={{ ...removeBtnStyle, color: 'var(--accent)' }}
                          onClick={() => navigate(`/analysis?ticker=${item.ticker}&market=${item.market_id}`)}
                        >
                          Analyze
                        </button>
                        <button style={removeBtnStyle} onClick={() => handleRemove(item.id)}>
                          Remove
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}
