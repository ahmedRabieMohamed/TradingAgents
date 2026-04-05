import { CSSProperties } from 'react';

export interface HistoryFilters {
  market?: string;
  recommendation?: string;
}

interface FilterBarProps {
  filters: HistoryFilters;
  onChange: (filters: HistoryFilters) => void;
}

interface Pill {
  label: string;
  key: keyof HistoryFilters;
  value: string | undefined;
}

const pills: Pill[] = [
  { label: 'All Markets', key: 'market', value: undefined },
  { label: '\u{1F1FA}\u{1F1F8} US', key: 'market', value: 'us' },
  { label: '\u{1F1EA}\u{1F1EC} EGX', key: 'market', value: 'egypt' },
  { label: 'Buy Only', key: 'recommendation', value: 'BUY' },
  { label: 'Sell Only', key: 'recommendation', value: 'SELL' },
  { label: 'Hold Only', key: 'recommendation', value: 'HOLD' },
];

const barStyle: CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: 8,
  padding: '12px 0',
};

function pillStyle(active: boolean): CSSProperties {
  return {
    padding: '6px 14px',
    borderRadius: 20,
    fontSize: 13,
    fontWeight: 500,
    cursor: 'pointer',
    border: active ? '1px solid var(--accent)' : '1px solid var(--border)',
    background: active ? 'rgba(59, 130, 246, 0.12)' : 'var(--surface2)',
    color: active ? 'var(--accent)' : 'var(--text2)',
    transition: 'all 0.15s ease',
    userSelect: 'none' as const,
  };
}

export default function FilterBar({ filters, onChange }: FilterBarProps) {
  function handleClick(pill: Pill) {
    const next = { ...filters };

    if (pill.key === 'market') {
      // "All Markets" clears market filter; specific market sets it
      next.market = pill.value;
    } else if (pill.key === 'recommendation') {
      // Toggle: clicking active recommendation clears it
      next.recommendation = filters.recommendation === pill.value ? undefined : pill.value;
    }

    onChange(next);
  }

  function isActive(pill: Pill): boolean {
    if (pill.key === 'market') {
      if (pill.value === undefined) return !filters.market;
      return filters.market === pill.value;
    }
    return filters.recommendation === pill.value;
  }

  return (
    <div style={barStyle}>
      {pills.map((pill) => (
        <button
          key={pill.label}
          style={pillStyle(isActive(pill))}
          onClick={() => handleClick(pill)}
        >
          {pill.label}
        </button>
      ))}
    </div>
  );
}
