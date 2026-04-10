import { useState, useEffect } from 'react';
import type { CSSProperties } from 'react';
import { getPortfolio, executeTrade } from '../../services/api';
import type { TradeRequest } from '../../types';

interface TradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  ticker: string;
  marketId: string;
  direction: 'long' | 'short';
  recommendation: string;
  confidence: number | null;
  currentPrice: number;
  analysisSessionId: string | null;
  onSuccess: () => void;
}

const overlayStyle: CSSProperties = {
  position: 'fixed',
  inset: 0,
  background: 'rgba(0, 0, 0, 0.6)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 1000,
};

const cardStyle: CSSProperties = {
  background: 'var(--surface)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-lg)',
  padding: 28,
  width: '100%',
  maxWidth: 440,
  display: 'flex',
  flexDirection: 'column',
  gap: 16,
  boxShadow: 'var(--shadow-md)',
};

const headerStyle: CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
};

const titleStyle: CSSProperties = {
  fontSize: 18,
  fontWeight: 700,
  color: 'var(--text)',
};

const closeBtnStyle: CSSProperties = {
  background: 'none',
  border: 'none',
  fontSize: 20,
  color: 'var(--text3)',
  cursor: 'pointer',
  padding: 4,
};

const rowStyle: CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  fontSize: 13,
  color: 'var(--text2)',
};

const labelStyle: CSSProperties = {
  fontSize: 12,
  fontWeight: 600,
  color: 'var(--text3)',
  marginBottom: 4,
};

const inputStyle: CSSProperties = {
  width: '100%',
  padding: '10px 12px',
  background: 'var(--surface2)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  color: 'var(--text)',
  fontSize: 14,
  outline: 'none',
  boxSizing: 'border-box',
};

const badgeStyle = (color: string): CSSProperties => ({
  display: 'inline-block',
  padding: '3px 10px',
  borderRadius: 'var(--radius-sm)',
  fontSize: 12,
  fontWeight: 700,
  color: '#fff',
  background: color,
});

const directionBadge = (dir: 'long' | 'short'): CSSProperties => ({
  display: 'inline-block',
  padding: '3px 10px',
  borderRadius: 'var(--radius-sm)',
  fontSize: 12,
  fontWeight: 600,
  color: dir === 'long' ? '#22c55e' : '#ef4444',
  background: dir === 'long' ? 'rgba(34,197,94,0.12)' : 'rgba(239,68,68,0.12)',
});

const warningBox: CSSProperties = {
  padding: 10,
  background: 'rgba(234,179,8,0.1)',
  border: '1px solid rgba(234,179,8,0.3)',
  borderRadius: 'var(--radius-sm)',
  color: '#eab308',
  fontSize: 12,
  textAlign: 'center',
};

const successBox: CSSProperties = {
  padding: 12,
  background: 'rgba(34,197,94,0.1)',
  border: '1px solid rgba(34,197,94,0.3)',
  borderRadius: 'var(--radius-sm)',
  color: '#22c55e',
  fontSize: 13,
  textAlign: 'center',
};

const errorBoxStyle: CSSProperties = {
  padding: 12,
  background: 'rgba(239,68,68,0.1)',
  border: '1px solid rgba(239,68,68,0.3)',
  borderRadius: 'var(--radius-sm)',
  color: '#ef4444',
  fontSize: 13,
  textAlign: 'center',
};

const confirmBtnStyle = (disabled: boolean): CSSProperties => ({
  width: '100%',
  padding: '12px 0',
  borderRadius: 'var(--radius-sm)',
  border: 'none',
  background: disabled ? 'var(--surface2)' : '#22c55e',
  color: disabled ? 'var(--text3)' : '#fff',
  fontSize: 14,
  fontWeight: 700,
  cursor: disabled ? 'not-allowed' : 'pointer',
  opacity: disabled ? 0.6 : 1,
});

const dividerStyle: CSSProperties = {
  height: 1,
  background: 'var(--border)',
  margin: '4px 0',
};

export default function TradeModal({
  isOpen,
  onClose,
  ticker,
  marketId,
  direction,
  recommendation,
  confidence,
  currentPrice,
  analysisSessionId,
  onSuccess,
}: TradeModalProps) {
  const [quantity, setQuantity] = useState<string>('1');
  const [availableCash, setAvailableCash] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [fetchingCash, setFetchingCash] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<{ entryPrice: number; totalCost: number } | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    // Reset state on open
    setQuantity('1');
    setError(null);
    setSuccess(null);
    setLoading(false);

    // Fetch available cash
    setFetchingCash(true);
    getPortfolio()
      .then((p) => setAvailableCash(p.cash_balance))
      .catch(() => setAvailableCash(null))
      .finally(() => setFetchingCash(false));
  }, [isOpen]);

  if (!isOpen) return null;

  const qty = Math.max(0, parseInt(quantity, 10) || 0);
  const totalCost = qty * currentPrice;
  const insufficientCash = availableCash !== null && totalCost > availableCash;
  const canConfirm = qty >= 1 && !insufficientCash && !loading && !success;

  const recColor = recommendation.toUpperCase() === 'BUY' ? '#22c55e' : '#ef4444';

  async function handleConfirm() {
    setLoading(true);
    setError(null);
    try {
      const req: TradeRequest = {
        ticker,
        market_id: marketId,
        direction,
        quantity: qty,
      };
      if (analysisSessionId) {
        req.analysis_session_id = analysisSessionId;
      }
      const res = await executeTrade(req);
      setSuccess({ entryPrice: res.entry_price, totalCost: res.total_cost });
      setTimeout(() => {
        onSuccess();
        onClose();
      }, 1500);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Trade execution failed';
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={overlayStyle} onClick={onClose}>
      <div style={cardStyle} onClick={(e) => e.stopPropagation()}>
        <div style={headerStyle}>
          <span style={titleStyle}>Execute Trade</span>
          <button style={closeBtnStyle} onClick={onClose}>&times;</button>
        </div>

        <div style={dividerStyle} />

        {/* Ticker + recommendation */}
        <div style={rowStyle}>
          <span style={{ fontSize: 16, fontWeight: 700, color: 'var(--text)' }}>{ticker}</span>
          <span style={badgeStyle(recColor)}>{recommendation.toUpperCase()}</span>
        </div>

        {/* Direction + price */}
        <div style={rowStyle}>
          <span>Direction: <span style={directionBadge(direction)}>{direction.toUpperCase()}</span></span>
          <span>Price: <strong style={{ color: 'var(--text)' }}>${currentPrice.toFixed(2)}</strong></span>
        </div>

        {confidence !== null && (
          <div style={{ fontSize: 12, color: 'var(--text3)' }}>
            AI Confidence: <strong style={{ color: recColor }}>{Math.round(confidence)}%</strong>
          </div>
        )}

        <div style={dividerStyle} />

        {/* Quantity input */}
        <div>
          <div style={labelStyle}>Quantity</div>
          <input
            type="number"
            min={1}
            step={1}
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            style={inputStyle}
            placeholder="Enter quantity"
          />
        </div>

        {/* Position size calculator */}
        {availableCash !== null && currentPrice > 0 && (
          <div style={{ background: 'var(--surface2)', borderRadius: 'var(--radius-sm)', padding: 12, fontSize: 12 }}>
            <div style={{ fontWeight: 600, color: 'var(--text3)', marginBottom: 8, fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Position Size Guide
            </div>
            {[1, 2, 5, 10].map((riskPct) => {
              const riskAmount = availableCash * (riskPct / 100);
              const suggestedQty = Math.floor(riskAmount / currentPrice);
              return suggestedQty > 0 ? (
                <div key={riskPct} style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text2)', padding: '3px 0' }}>
                  <span>{riskPct}% risk (${riskAmount.toFixed(0)})</span>
                  <button
                    style={{ background: 'none', border: 'none', color: 'var(--accent)', cursor: 'pointer', fontSize: 12, fontWeight: 600 }}
                    onClick={() => setQuantity(String(suggestedQty))}
                  >
                    {suggestedQty} shares
                  </button>
                </div>
              ) : null;
            })}
          </div>
        )}

        {/* Total cost */}
        <div style={rowStyle}>
          <span>Total Cost</span>
          <span style={{ fontSize: 16, fontWeight: 700, color: 'var(--text)' }}>
            ${totalCost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
        </div>

        {/* Available cash */}
        <div style={rowStyle}>
          <span>Available Cash</span>
          <span style={{ fontWeight: 600, color: 'var(--text)' }}>
            {fetchingCash
              ? '...'
              : availableCash !== null
                ? `$${availableCash.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                : 'N/A'}
          </span>
        </div>

        {/* Warning */}
        {insufficientCash && (
          <div style={warningBox}>
            Insufficient cash. Reduce quantity or close existing positions.
          </div>
        )}

        {/* Success message */}
        {success && (
          <div style={successBox}>
            Trade executed! Entry: ${success.entryPrice.toFixed(2)} | Total: ${success.totalCost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
        )}

        {/* Error message */}
        {error && <div style={errorBoxStyle}>{error}</div>}

        {/* Confirm button */}
        <button
          style={confirmBtnStyle(!canConfirm)}
          disabled={!canConfirm}
          onClick={handleConfirm}
        >
          {loading ? 'Executing...' : success ? 'Trade Confirmed' : 'Confirm Trade'}
        </button>
      </div>
    </div>
  );
}
