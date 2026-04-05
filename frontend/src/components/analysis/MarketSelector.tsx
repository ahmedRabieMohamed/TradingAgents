import { useState, useEffect, CSSProperties } from 'react';
import { fetchMarkets } from '../../services/api';
import { useMarketStore } from '../../stores/marketStore';
import type { Market } from '../../types';

interface MarketSelectorProps {
  onSelect: (marketId: string) => void;
}

const FLAG_MAP: Record<string, string> = {
  us: '\u{1F1FA}\u{1F1F8}',
  egypt: '\u{1F1EA}\u{1F1EC}',
};

const gridStyle: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(2, 1fr)',
  gap: 16,
  maxWidth: 640,
};

const cardBase: CSSProperties = {
  background: 'var(--surface)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-lg)',
  padding: 24,
  cursor: 'pointer',
  transition: 'border-color 0.15s, transform 0.15s, background 0.15s',
  display: 'flex',
  flexDirection: 'column',
  gap: 10,
};

const flagStyle: CSSProperties = {
  fontSize: 36,
};

const nameStyle: CSSProperties = {
  fontSize: 16,
  fontWeight: 600,
  color: 'var(--text)',
};

const exchangeStyle: CSSProperties = {
  fontSize: 13,
  color: 'var(--text2)',
};

const metaRow: CSSProperties = {
  display: 'flex',
  gap: 12,
  fontSize: 12,
  color: 'var(--text3)',
  marginTop: 4,
};

const tagContainer: CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: 6,
  marginTop: 6,
};

const tagStyle: CSSProperties = {
  padding: '3px 8px',
  background: 'var(--surface2)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  fontSize: 11,
  color: 'var(--text2)',
  fontFamily: 'var(--font-mono, monospace)',
};

const loadingStyle: CSSProperties = {
  color: 'var(--text3)',
  fontSize: 14,
  padding: 24,
};

const errorStyle: CSSProperties = {
  color: 'var(--red)',
  fontSize: 13,
  padding: 24,
};

export default function MarketSelector({ onSelect }: MarketSelectorProps) {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hovered, setHovered] = useState<string | null>(null);

  useEffect(() => {
    fetchMarkets()
      .then((res) => setMarkets(res.markets))
      .catch((err) => setError(err.message || 'Failed to load markets'))
      .finally(() => setLoading(false));
  }, []);

  const setMarket = useMarketStore((s) => s.setMarket);

  function handleSelect(market: Market) {
    setSelected(market.id);
    const flag = FLAG_MAP[market.id] ?? '';
    setMarket(market.id, `${flag} ${market.name} (${market.exchange})`);
    onSelect(market.id);
  }

  if (loading) return <div style={loadingStyle}>Loading markets...</div>;
  if (error) return <div style={errorStyle}>{error}</div>;

  return (
    <div style={gridStyle}>
      {markets.map((market) => {
        const isSelected = selected === market.id;
        const isHovered = hovered === market.id;
        const cardStyle: CSSProperties = {
          ...cardBase,
          borderColor: isSelected
            ? 'var(--accent)'
            : isHovered
              ? 'var(--accent)'
              : 'var(--border)',
          background: isSelected
            ? 'rgba(59, 130, 246, 0.06)'
            : 'var(--surface)',
          transform: isHovered ? 'translateY(-2px)' : 'none',
        };

        return (
          <div
            key={market.id}
            style={cardStyle}
            onClick={() => handleSelect(market)}
            onMouseEnter={() => setHovered(market.id)}
            onMouseLeave={() => setHovered(null)}
          >
            <span style={flagStyle}>{FLAG_MAP[market.id] ?? '🏳️'}</span>
            <span style={nameStyle}>{market.name}</span>
            <span style={exchangeStyle}>{market.exchange}</span>
            <div style={metaRow}>
              <span>{market.currency}</span>
              <span>·</span>
              <span>{market.trading_days.join(', ')}</span>
            </div>
            <div style={tagContainer}>
              {market.example_tickers.map((t) => (
                <span key={t} style={tagStyle}>{t}</span>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
