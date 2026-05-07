import type { CSSProperties } from 'react';
import type { PortfolioResponse } from '../../types';
import { ValueFlash } from '../../motion';

interface PortfolioSummaryProps {
  portfolio: PortfolioResponse;
}

function pnlColor(value: number): string {
  if (value > 0) return '#22c55e';
  if (value < 0) return '#ef4444';
  return 'var(--text2)';
}

function pnlGradient(value: number): string {
  if (value > 0)
    return 'linear-gradient(135deg, rgba(34,197,94,0.12) 0%, rgba(34,197,94,0.03) 100%)';
  if (value < 0)
    return 'linear-gradient(135deg, rgba(239,68,68,0.12) 0%, rgba(239,68,68,0.03) 100%)';
  return 'linear-gradient(135deg, var(--surface2) 0%, var(--surface) 100%)';
}

function formatMoney(v: number): string {
  return v.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export default function PortfolioSummary({ portfolio }: PortfolioSummaryProps) {
  const isPositive = portfolio.total_pnl >= 0;

  const containerStyle: CSSProperties = {
    background: pnlGradient(portfolio.total_pnl),
    border: `1.5px solid ${pnlColor(portfolio.total_pnl)}33`,
    borderRadius: 'var(--radius-lg)',
    padding: '28px 24px',
    boxShadow: 'var(--shadow-sm)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 16,
    marginBottom: 24,
  };

  const currentValueStyle: CSSProperties = {
    fontSize: 36,
    fontWeight: 800,
    color: 'var(--text)',
    letterSpacing: '-0.5px',
  };

  const pnlStyle: CSSProperties = {
    fontSize: 18,
    fontWeight: 700,
    color: pnlColor(portfolio.total_pnl),
  };

  const statsRow: CSSProperties = {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 16,
    justifyContent: 'center',
  };

  const statChip: CSSProperties = {
    padding: '6px 14px',
    background: 'var(--surface2)',
    borderRadius: 'var(--radius-sm)',
    border: '1px solid var(--border)',
    fontSize: 13,
    color: 'var(--text2)',
    textAlign: 'center',
  };

  const statLabel: CSSProperties = {
    fontSize: 10,
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    color: 'var(--text3)',
    marginBottom: 2,
  };

  const statValue: CSSProperties = {
    fontSize: 14,
    fontWeight: 700,
    color: 'var(--text)',
  };

  return (
    <div style={containerStyle}>
      <div style={{ fontSize: 12, color: 'var(--text3)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
        Portfolio Value
      </div>
      <div style={currentValueStyle}>
        $<ValueFlash value={portfolio.total_value} format={formatMoney} />
      </div>
      <div style={pnlStyle}>
        {isPositive ? '+' : ''}$
        <ValueFlash value={portfolio.total_pnl} format={formatMoney} />{' '}
        <span style={{ fontSize: 14 }}>
          ({isPositive ? '+' : ''}
          <ValueFlash value={portfolio.total_pnl_pct} decimals={2} />%)
        </span>
      </div>

      <div style={statsRow}>
        <div style={statChip}>
          <div style={statLabel}>Starting Balance</div>
          <div style={statValue}>${formatMoney(portfolio.starting_balance)}</div>
        </div>
        <div style={statChip}>
          <div style={statLabel}>Cash Remaining</div>
          <div style={statValue}>${formatMoney(portfolio.cash_balance)}</div>
        </div>
        <div style={statChip}>
          <div style={statLabel}>Open Positions</div>
          <div style={statValue}>{portfolio.open_positions_count}</div>
        </div>
      </div>
    </div>
  );
}
