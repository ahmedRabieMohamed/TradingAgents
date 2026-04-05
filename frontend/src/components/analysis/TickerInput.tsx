import { useState, CSSProperties, KeyboardEvent } from 'react';
import { validateStock } from '../../services/api';
import type { StockValidation } from '../../types';

interface TickerInputProps {
  marketId: string;
  onValidated: (stock: StockValidation) => void;
}

const PLACEHOLDER_MAP: Record<string, string> = {
  us: 'AAPL',
  egx: 'COMI',
};

const wrapperStyle: CSSProperties = {
  maxWidth: 480,
  display: 'flex',
  flexDirection: 'column',
  gap: 16,
};

const inputRow: CSSProperties = {
  display: 'flex',
  gap: 10,
};

const inputStyle: CSSProperties = {
  flex: 1,
  padding: '10px 14px',
  background: 'var(--surface2)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  color: 'var(--text)',
  fontSize: 14,
  outline: 'none',
  fontFamily: 'var(--font-mono, monospace)',
  textTransform: 'uppercase',
};

const btnStyle: CSSProperties = {
  padding: '10px 20px',
  background: 'var(--accent)',
  color: '#fff',
  border: 'none',
  borderRadius: 'var(--radius-sm)',
  fontSize: 13,
  fontWeight: 600,
  cursor: 'pointer',
  whiteSpace: 'nowrap',
};

const btnDisabled: CSSProperties = {
  ...btnStyle,
  opacity: 0.5,
  cursor: 'not-allowed',
};

const errorMsg: CSSProperties = {
  color: 'var(--red)',
  fontSize: 13,
};

const stockCard: CSSProperties = {
  background: 'var(--surface)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-lg)',
  padding: 20,
  display: 'flex',
  flexDirection: 'column',
  gap: 8,
};

const stockName: CSSProperties = {
  fontSize: 15,
  fontWeight: 600,
  color: 'var(--text)',
};

const stockTicker: CSSProperties = {
  fontSize: 12,
  color: 'var(--text3)',
  fontFamily: 'var(--font-mono, monospace)',
};

const priceRow: CSSProperties = {
  display: 'flex',
  alignItems: 'baseline',
  gap: 10,
  marginTop: 4,
};

const priceStyle: CSSProperties = {
  fontSize: 22,
  fontWeight: 700,
  color: 'var(--text)',
};

const continueBtn: CSSProperties = {
  ...btnStyle,
  alignSelf: 'flex-start',
  marginTop: 8,
};

export default function TickerInput({ marketId, onValidated }: TickerInputProps) {
  const [ticker, setTicker] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stock, setStock] = useState<StockValidation | null>(null);

  async function handleValidate() {
    const trimmed = ticker.trim().toUpperCase();
    if (!trimmed) return;

    setLoading(true);
    setError(null);
    setStock(null);

    try {
      const result = await validateStock(trimmed, marketId);
      if (result.valid) {
        setStock(result);
      } else {
        setError('Stock not found or invalid for this market.');
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Validation failed';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') handleValidate();
  }

  const placeholder = PLACEHOLDER_MAP[marketId] ?? 'TICKER';
  const changePct = stock?.change_pct ?? 0;
  const changeColor = changePct >= 0 ? 'var(--green)' : 'var(--red)';
  const changeSign = changePct >= 0 ? '+' : '';

  return (
    <div style={wrapperStyle}>
      <div style={inputRow}>
        <input
          style={inputStyle}
          type="text"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`e.g. ${placeholder}`}
          disabled={loading}
        />
        <button
          style={loading || !ticker.trim() ? btnDisabled : btnStyle}
          onClick={handleValidate}
          disabled={loading || !ticker.trim()}
        >
          {loading ? 'Validating...' : 'Validate'}
        </button>
      </div>

      {error && <div style={errorMsg}>{error}</div>}

      {stock && (
        <div style={stockCard}>
          <span style={stockName}>{stock.name}</span>
          <span style={stockTicker}>{stock.ticker} · {stock.currency}</span>
          <div style={priceRow}>
            <span style={priceStyle}>
              {stock.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            <span style={{ fontSize: 14, fontWeight: 600, color: changeColor }}>
              {changeSign}{changePct.toFixed(2)}%
            </span>
          </div>
          <button style={continueBtn} onClick={() => onValidated(stock)}>
            Continue →
          </button>
        </div>
      )}
    </div>
  );
}
