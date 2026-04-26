import type { CSSProperties } from 'react';

interface PerfCardProps {
  value: string;
  label: string;
  color?: string;
}

const cardStyle: CSSProperties = {
  background: 'var(--surface2)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-lg)',
  padding: '24px 20px',
  boxShadow: 'var(--shadow-sm)',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: 6,
};

const valueStyle = (color?: string): CSSProperties => ({
  fontSize: 32,
  fontWeight: 700,
  color: color || 'var(--text)',
  lineHeight: 1.1,
});

const labelStyle: CSSProperties = {
  fontSize: 13,
  fontWeight: 500,
  color: 'var(--text3)',
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
};

export default function PerfCard({ value, label, color }: PerfCardProps) {
  return (
    <div style={cardStyle}>
      <span style={valueStyle(color)}>{value}</span>
      <span style={labelStyle}>{label}</span>
    </div>
  );
}
