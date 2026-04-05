import { useState, useEffect, useCallback, CSSProperties } from 'react';
import { fetchMarketNews } from '../../services/api';
import type { NewsArticle } from '../../types';

interface NewsSectionProps {
  marketId: string;
}

const containerStyle: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 12,
};

const headerRowStyle: CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: 4,
};

const refreshBtnStyle: CSSProperties = {
  padding: '6px 14px',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid var(--border)',
  background: 'transparent',
  color: 'var(--text2)',
  fontSize: 12,
  cursor: 'pointer',
};

const cardStyle: CSSProperties = {
  padding: '14px 16px',
  background: 'var(--surface)',
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

function hotBadge(): CSSProperties {
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

function newBadge(): CSSProperties {
  return {
    display: 'inline-block',
    padding: '1px 6px',
    borderRadius: 8,
    fontSize: 10,
    fontWeight: 700,
    color: '#fff',
    background: 'var(--accent)',
    letterSpacing: '0.5px',
  };
}

const spinnerWrapStyle: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: 40,
  color: 'var(--text3)',
  fontSize: 14,
  gap: 10,
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

const emptyStyle: CSSProperties = {
  padding: 32,
  textAlign: 'center',
  color: 'var(--text3)',
  fontSize: 14,
};

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

export default function NewsSection({ marketId }: NewsSectionProps) {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  const loadNews = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchMarketNews(marketId);
      setArticles(response.articles);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load news';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [marketId]);

  useEffect(() => {
    loadNews();
  }, [loadNews]);

  if (loading) {
    return (
      <div style={spinnerWrapStyle}>
        <span className="spinner" />
        <span>Loading news...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div style={containerStyle}>
        <div style={errorStyle}>
          {error}
          <br />
          <button
            style={{ ...refreshBtnStyle, marginTop: 10 }}
            onClick={loadNews}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      <div style={headerRowStyle}>
        <span style={{ fontSize: 13, color: 'var(--text3)' }}>
          {articles.length} article{articles.length !== 1 ? 's' : ''}
        </span>
        <button style={refreshBtnStyle} onClick={loadNews}>
          Refresh
        </button>
      </div>

      {articles.length === 0 ? (
        <div style={emptyStyle}>No news articles available.</div>
      ) : (
        articles.map((article, idx) => (
          <div
            key={`${article.url}-${idx}`}
            style={{
              ...cardStyle,
              background: hoveredIdx === idx ? 'var(--surface2)' : 'var(--surface)',
            }}
            onMouseEnter={() => setHoveredIdx(idx)}
            onMouseLeave={() => setHoveredIdx(null)}
            onClick={() => window.open(article.url, '_blank')}
          >
            <div style={titleStyle}>{article.title}</div>
            <div style={metaRowStyle}>
              <span style={sourceStyle}>{article.source}</span>
              <span style={timeStyle}>{formatRelativeTime(article.published_at)}</span>
              {article.is_hot && <span style={hotBadge()}>HOT</span>}
              {idx < 3 && !article.is_hot && <span style={newBadge()}>NEW</span>}
            </div>
            {article.snippet && <div style={snippetStyle}>{article.snippet}</div>}
          </div>
        ))
      )}
    </div>
  );
}
