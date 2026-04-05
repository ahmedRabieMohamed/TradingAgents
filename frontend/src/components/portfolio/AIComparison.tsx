import { useState, useEffect, CSSProperties } from 'react';
import { getAIComparison } from '../../services/api';
import type { AIComparisonResponse } from '../../types';

const wrapperStyle: CSSProperties = {
  marginTop: 24,
};

const titleStyle: CSSProperties = {
  fontSize: 14,
  fontWeight: 600,
  color: 'var(--text)',
  marginBottom: 14,
};

const cardsRow: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: '1fr 1fr',
  gap: 14,
  marginBottom: 14,
};

function sideCard(variant: 'followed' | 'ignored'): CSSProperties {
  const isFollowed = variant === 'followed';
  const accent = isFollowed ? '#22c55e' : '#f59e0b';
  return {
    background: `linear-gradient(135deg, ${accent}0D 0%, ${accent}03 100%)`,
    border: `1px solid ${accent}33`,
    borderRadius: 'var(--radius-lg)',
    padding: '20px 18px',
  };
}

const sideLabel: CSSProperties = {
  fontSize: 11,
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.06em',
  marginBottom: 14,
};

const metricRow: CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '6px 0',
  borderBottom: '1px solid var(--border)',
};

const metricLabel: CSSProperties = {
  fontSize: 12,
  color: 'var(--text3)',
};

const metricValue: CSSProperties = {
  fontSize: 14,
  fontWeight: 700,
  color: 'var(--text)',
};

function bannerStyle(isPositive: boolean): CSSProperties {
  const clr = isPositive ? '#22c55e' : '#ef4444';
  return {
    background: `${clr}11`,
    border: `1px solid ${clr}33`,
    borderRadius: 'var(--radius-lg)',
    padding: '14px 20px',
    textAlign: 'center',
    fontSize: 14,
    fontWeight: 600,
    color: clr,
  };
}

const loadingStyle: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: 32,
  gap: 10,
  color: 'var(--text3)',
  fontSize: 13,
};

const emptyStyle: CSSProperties = {
  textAlign: 'center',
  padding: 32,
  color: 'var(--text3)',
  fontSize: 13,
};

function formatMoney(v: number): string {
  const sign = v >= 0 ? '+' : '';
  return sign + '$' + Math.abs(v).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function renderMetrics(side: { count: number; win_rate: number; avg_return_pct: number; total_pnl: number }) {
  return (
    <>
      <div style={metricRow}>
        <span style={metricLabel}>Trades</span>
        <span style={metricValue}>{side.count}</span>
      </div>
      <div style={metricRow}>
        <span style={metricLabel}>Win Rate</span>
        <span style={{ ...metricValue, color: side.win_rate >= 50 ? '#22c55e' : '#ef4444' }}>
          {side.win_rate.toFixed(1)}%
        </span>
      </div>
      <div style={metricRow}>
        <span style={metricLabel}>Avg Return</span>
        <span style={{ ...metricValue, color: side.avg_return_pct >= 0 ? '#22c55e' : '#ef4444' }}>
          {side.avg_return_pct >= 0 ? '+' : ''}{side.avg_return_pct.toFixed(2)}%
        </span>
      </div>
      <div style={{ ...metricRow, borderBottom: 'none' }}>
        <span style={metricLabel}>Total P&L</span>
        <span style={{ ...metricValue, color: side.total_pnl >= 0 ? '#22c55e' : '#ef4444' }}>
          {formatMoney(side.total_pnl)}
        </span>
      </div>
    </>
  );
}

export default function AIComparison() {
  const [data, setData] = useState<AIComparisonResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAIComparison()
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load AI comparison'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div style={loadingStyle}>
        <span className="spinner" />
        Loading AI comparison...
      </div>
    );
  }

  if (error) {
    return <div style={{ ...emptyStyle, color: '#ef4444' }}>{error}</div>;
  }

  if (!data || (data.followed.count === 0 && data.ignored.count === 0)) {
    return (
      <div style={emptyStyle}>
        <div style={{ fontSize: 28, marginBottom: 8 }}>🤖</div>
        <div style={{ fontWeight: 600, color: 'var(--text)', marginBottom: 4 }}>
          Not Enough Data
        </div>
        <div>Complete trades linked to AI analyses to see the comparison.</div>
      </div>
    );
  }

  const aiOutperforms = data.difference.return_advantage_pct >= 0;

  return (
    <div style={wrapperStyle} className="fade-in">
      <div style={titleStyle}>AI Recommendation Comparison</div>

      <div style={cardsRow}>
        {/* Followed AI */}
        <div style={sideCard('followed')}>
          <div style={{ ...sideLabel, color: '#22c55e' }}>Followed AI</div>
          {renderMetrics(data.followed)}
        </div>

        {/* Ignored AI */}
        <div style={sideCard('ignored')}>
          <div style={{ ...sideLabel, color: '#f59e0b' }}>Ignored AI</div>
          {renderMetrics(data.ignored)}
        </div>
      </div>

      {/* Difference banner */}
      <div style={bannerStyle(aiOutperforms)}>
        {data.difference.message}
      </div>
    </div>
  );
}
