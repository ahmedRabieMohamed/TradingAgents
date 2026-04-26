import type { CSSProperties } from 'react';
import type { StatsData } from '../../stores/analysisStore';

interface StatsBarProps {
  stats: StatsData | null;
}

const barStyle: CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: 8,
};

const chipStyle: CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 6,
  padding: '6px 12px',
  background: 'var(--surface2)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  fontSize: 12,
  color: 'var(--text2)',
};

const valueStyle: CSSProperties = {
  color: 'var(--accent)',
  fontWeight: 700,
};

function formatTokens(tokensIn: number, tokensOut: number): string {
  const total = tokensIn + tokensOut;
  if (total >= 1000) {
    return `${(total / 1000).toFixed(1)}k`;
  }
  return total.toLocaleString();
}

function formatElapsed(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)}s`;
  const m = Math.floor(seconds / 60);
  const s = Math.round(seconds % 60);
  return `${m}m ${s}s`;
}

export default function StatsBar({ stats }: StatsBarProps) {
  if (!stats) {
    return (
      <div style={barStyle}>
        <div style={chipStyle}>
          <span>Agents:</span>
          <span style={valueStyle}>0/0</span>
        </div>
      </div>
    );
  }

  const chips = [
    { label: 'Agents', value: `${stats.agents_completed}/${stats.agents_total}` },
    { label: 'LLM Calls', value: stats.llm_calls.toLocaleString() },
    { label: 'Tools', value: stats.tool_calls.toLocaleString() },
    { label: 'Tokens', value: formatTokens(stats.tokens_in, stats.tokens_out) },
    { label: 'Reports', value: stats.reports_generated.toLocaleString() },
    { label: 'Elapsed', value: formatElapsed(stats.elapsed_seconds) },
  ];

  return (
    <div style={barStyle}>
      {chips.map((chip) => (
        <div key={chip.label} style={chipStyle}>
          <span>{chip.label}:</span>
          <span style={valueStyle}>{chip.value}</span>
        </div>
      ))}
    </div>
  );
}
