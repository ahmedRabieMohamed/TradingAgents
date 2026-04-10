import { useState, useEffect, useCallback } from 'react';
import type { CSSProperties } from 'react';
import { fetchMarketNews } from '../../services/api';
import type { NewsArticle } from '../../types';

interface TickerNewsProps {
  ticker: string;
  marketId: string;
  onClose: () => void;
}

const backdropStyle: CSSProperties = {
  position: 'fixed',
  inset: 0,
  background: 'rgba(0, 0, 0, 0.6)',
  zIndex: 1000,
  display: 'flex',
  justifyContent: 'flex-end',
};

const panelStyle: CSSProperties = {
  width: '100%',
  maxWidth: 480,
  height: '100%',
  background: 'var(--surface)',
  borderLeft: '1px solid var(--border)',
  display: 'flex',
  flexDirection: 'column',
  animation: 'slideInRight 0.2s ease-out',
};

const headerStyle: CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '16px 20px',
  borderBottom: '1px solid var(--border)',
  flexShrink: 0,
};

const headerTitleStyle: CSSProperties = {
  fontSize: 16,
  fontWeight: 700,
  color: 'var(--text)',
};

const closeBtnStyle: CSSProperties = {
  background: 'transparent',
  border: 'none',
  color: 'var(--text3)',
  fontSize: 20,
  cursor: 'pointer',
  padding: '4px 8px',
  borderRadius: 'var(--radius-sm)',
  lineHeight: 1,
};

const bodyStyle: CSSProperties = {
  flex: 1,
  overflowY: 'auto',
  padding: '16px 20px',
  display: 'flex',
  flexDirection: 'column',
  gap: 12,
};

const cardStyle: CSSProperties = {
  padding: '14px 16px',
  background: 'var(--surface2)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  cursor: 'pointer',
  transition: 'background 0.15s',
};

const titleStyle: CSSProperties = {
  fontSize: 14,
  fontWeight: 700,
  color: 'var(--text)',
  marginBottom: 4,
  lineHeight: 1.4,
};

const metaRowStyle: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 8,
  marginBottom: 6,
  flexWrap: 'wrap',
};

const sourceStyle: CSSProperties = {
  fontSize: 12,
  color: 'var(--accent)',
  fontWeight: 600,
};

const timeStyle: CSSProperties = {
  fontSize: 11,
  color: 'var(--text3)',
};

const snippetStyle: CSSProperties = {
  fontSize: 13,
  color: 'var(--text2)',
  lineHeight: 1.5,
};

const spinnerWrapStyle: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: 40,
  color: 'var(--text3)',
  fontSize: 14,
  gap: 10,
};

const emptyStyle: CSSProperties = {
  padding: 32,
  textAlign: 'center',
  color: 'var(--text3)',
  fontSize: 14,
};

const errorStyle: CSSProperties = {
  padding: 16,
  background: 'rgba(239, 68, 68, 0.1)',
  border: '1px solid rgba(239, 68, 68, 0.3)',
  borderRadius: 'var(--radius-sm)',
  color: '#ef4444',
  fontSize: 13,
  textAlign: 'center',
};

function hotBadgeStyle(): CSSProperties {
  return {
    display: 'inline-block',
    padding: '1px 6px',
    borderRadius: 8,
    fontSize: 10,
    fontWeight: 700,
    color: '#fff',
    background: 'var(--red)',
    letterSpacing: '0.5px',
  };
}

function formatRelativeTime(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diffMs = now - then;

  if (isNaN(then)) return '';

  const minutes = Math.floor(diffMs / 60000);
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;

  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;

  return new Date(dateStr).toLocaleDateString();
}

export default function TickerNews({ ticker, marketId, onClose }: TickerNewsProps) {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  const loadNews = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchMarketNews(marketId, ticker, 10);
      setArticles(response.articles);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load news';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [marketId, ticker]);

  useEffect(() => {
    loadNews();
  }, [loadNews]);

  return (
    <div style={backdropStyle} onClick={onClose}>
      <div style={panelStyle} onClick={(e) => e.stopPropagation()}>
        <div style={headerStyle}>
          <span style={headerTitleStyle}>News: {ticker}</span>
          <button style={closeBtnStyle} onClick={onClose} title="Close">
            &times;
          </button>
        </div>

        <div style={bodyStyle}>
          {loading && (
            <div style={spinnerWrapStyle}>
              <span className="spinner" />
              <span>Loading news...</span>
            </div>
          )}

          {error && (
            <div style={errorStyle}>
              {error}
              <br />
              <button
                style={{
                  padding: '6px 14px',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border)',
                  background: 'transparent',
                  color: 'var(--text2)',
                  fontSize: 12,
                  cursor: 'pointer',
                  marginTop: 10,
                }}
                onClick={loadNews}
              >
                Retry
              </button>
            </div>
          )}

          {!loading && !error && articles.length === 0 && (
            <div style={emptyStyle}>No recent news found for {ticker}</div>
          )}

          {!loading &&
            !error &&
            articles.map((article, idx) => (
              <div
                key={`${article.url}-${idx}`}
                style={{
                  ...cardStyle,
                  background: hoveredIdx === idx ? 'var(--surface)' : 'var(--surface2)',
                }}
                onMouseEnter={() => setHoveredIdx(idx)}
                onMouseLeave={() => setHoveredIdx(null)}
                onClick={() => window.open(article.url, '_blank')}
              >
                <div style={titleStyle}>{article.title}</div>
                <div style={metaRowStyle}>
                  <span style={sourceStyle}>{article.source}</span>
                  <span style={timeStyle}>{formatRelativeTime(article.published_at)}</span>
                  {article.is_hot && <span style={hotBadgeStyle()}>HOT</span>}
                </div>
                {article.snippet && <div style={snippetStyle}>{article.snippet}</div>}
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}
