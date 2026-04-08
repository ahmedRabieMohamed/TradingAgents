import { CSSProperties } from 'react';

interface ResultHeroProps {
  recommendation: string;
  confidence: number;
  ticker: string;
  market: string;
  horizon: string;
  date: string;
}

function recColor(rec: string): string {
  const upper = rec.toUpperCase();
  if (upper === 'BUY') return '#22c55e';
  if (upper === 'SELL') return '#ef4444';
  return '#eab308'; // HOLD / yellow
}

function recGradient(rec: string): string {
  const upper = rec.toUpperCase();
  if (upper === 'BUY')
    return 'linear-gradient(135deg, rgba(34,197,94,0.12) 0%, rgba(34,197,94,0.03) 100%)';
  if (upper === 'SELL')
    return 'linear-gradient(135deg, rgba(239,68,68,0.12) 0%, rgba(239,68,68,0.03) 100%)';
  return 'linear-gradient(135deg, rgba(234,179,8,0.12) 0%, rgba(234,179,8,0.03) 100%)';
}

export default function ResultHero({
  recommendation,
  confidence,
  ticker,
  market,
  horizon,
  date,
}: ResultHeroProps) {
  const color = recColor(recommendation);

  const containerStyle: CSSProperties = {
    background: recGradient(recommendation),
    border: `1.5px solid ${color}33`,
    borderRadius: 'var(--radius-lg)',
    padding: '40px 24px',
    boxShadow: 'var(--shadow-sm)',
    textAlign: 'center',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 12,
  };

  const recStyle: CSSProperties = {
    fontSize: 48,
    fontWeight: 800,
    color,
    letterSpacing: '2px',
    textTransform: 'uppercase',
  };

  const confStyle: CSSProperties = {
    fontSize: 20,
    fontWeight: 600,
    color: 'var(--text)',
  };

  const confValue: CSSProperties = {
    color,
    fontWeight: 800,
  };

  const infoLine: CSSProperties = {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 16,
    justifyContent: 'center',
    fontSize: 13,
    color: 'var(--text3)',
    marginTop: 8,
  };

  const infoChip: CSSProperties = {
    padding: '4px 10px',
    background: 'var(--surface2)',
    borderRadius: 'var(--radius-sm)',
    border: '1px solid var(--border)',
  };

  return (
    <div style={containerStyle}>
      <div style={recStyle}>{recommendation}</div>
      <div style={confStyle}>
        Confidence: <span style={confValue}>{Math.round(confidence)}%</span>
      </div>
      <div style={infoLine}>
        <span style={infoChip}>{ticker}</span>
        <span style={infoChip}>{market.toUpperCase()}</span>
        <span style={infoChip}>{horizon}</span>
        <span style={infoChip}>{date}</span>
      </div>
    </div>
  );
}
