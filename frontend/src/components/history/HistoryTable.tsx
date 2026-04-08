import { CSSProperties, useState } from 'react';
import type { AnalysisListItem } from '../../types';
import { simulateAnalysis } from '../../services/api';

interface HistoryTableProps {
  items: AnalysisListItem[];
  onView: (id: string) => void;
  onRefresh: () => void;
  selectedIds: string[];
  onToggleSelect: (id: string) => void;
}

const tableStyle: CSSProperties = {
  width: '100%',
  borderCollapse: 'collapse',
  fontSize: 13,
};

const thStyle: CSSProperties = {
  textAlign: 'left',
  padding: '10px 12px',
  color: 'var(--text3)',
  fontWeight: 500,
  fontSize: 11,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
  borderBottom: '1px solid var(--border)',
  whiteSpace: 'nowrap',
};

function tdStyle(isHovered: boolean): CSSProperties {
  return {
    padding: '10px 12px',
    borderBottom: '1px solid var(--border)',
    color: 'var(--text)',
    background: isHovered ? 'rgba(255,255,255,0.03)' : 'transparent',
    transition: 'background 0.12s ease',
  };
}

function marketTag(marketId: string): CSSProperties {
  const isUS = marketId === 'us';
  return {
    display: 'inline-block',
    padding: '2px 8px',
    borderRadius: 4,
    fontSize: 11,
    fontWeight: 600,
    background: isUS ? 'rgba(59, 130, 246, 0.12)' : 'rgba(16, 185, 129, 0.12)',
    color: isUS ? 'var(--accent)' : '#10b981',
  };
}

function recTag(rec: string | null): CSSProperties {
  if (!rec) return { color: 'var(--text3)' };
  const colors: Record<string, { bg: string; fg: string }> = {
    BUY: { bg: 'rgba(16, 185, 129, 0.12)', fg: '#10b981' },
    SELL: { bg: 'rgba(239, 68, 68, 0.12)', fg: '#ef4444' },
    HOLD: { bg: 'rgba(234, 179, 8, 0.12)', fg: '#eab308' },
  };
  const c = colors[rec] || { bg: 'var(--surface2)', fg: 'var(--text2)' };
  return {
    display: 'inline-block',
    padding: '2px 8px',
    borderRadius: 4,
    fontSize: 11,
    fontWeight: 600,
    background: c.bg,
    color: c.fg,
  };
}

const viewBtn: CSSProperties = {
  padding: '4px 12px',
  borderRadius: 6,
  fontSize: 12,
  fontWeight: 500,
  border: '1px solid var(--border)',
  background: 'var(--surface2)',
  color: 'var(--text2)',
  cursor: 'pointer',
  transition: 'all 0.12s ease',
};

const checkboxStyle: CSSProperties = {
  width: 16,
  height: 16,
  accentColor: 'var(--accent)',
  cursor: 'pointer',
};

const emptyStyle: CSSProperties = {
  textAlign: 'center',
  padding: 40,
  color: 'var(--text3)',
  fontSize: 14,
};

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatConfidence(conf: number | null): string {
  if (conf === null || conf === undefined) return '--';
  return `${Math.round(conf)}%`;
}

const simBtn: CSSProperties = {
  padding: '4px 12px',
  borderRadius: 6,
  fontSize: 12,
  fontWeight: 500,
  border: '1px solid rgba(139, 92, 246, 0.3)',
  background: 'rgba(139, 92, 246, 0.1)',
  color: 'var(--accent2)',
  cursor: 'pointer',
  transition: 'all 0.12s ease',
  marginLeft: 4,
};

function HoverRow({
  item,
  onView,
  onRefresh,
  selected,
  onToggleSelect,
}: {
  item: AnalysisListItem;
  onView: (id: string) => void;
  onRefresh: () => void;
  selected: boolean;
  onToggleSelect: (id: string) => void;
}) {
  const [hovered, setHovered] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const td = tdStyle(hovered);

  const returnPct = item.simulation?.return_pct;
  const hasReturn = returnPct !== undefined && returnPct !== null;
  const canSimulate = item.status === 'completed' && !item.simulation && item.recommendation;

  async function handleSimulate() {
    setSimulating(true);
    try {
      await simulateAnalysis(item.id);
      onRefresh();
    } catch {
      // Silently fail — likely horizon hasn't elapsed yet
    } finally {
      setSimulating(false);
    }
  }

  return (
    <tr
      className="hover-row"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{ cursor: 'pointer' }}
    >
      <td style={td}>
        <input
          type="checkbox"
          style={checkboxStyle}
          checked={selected}
          onChange={() => onToggleSelect(item.id)}
        />
      </td>
      <td style={td}>{formatDate(item.analysis_date)}</td>
      <td style={{ ...td, fontWeight: 600 }}>{item.ticker}</td>
      <td style={td}>
        <span style={marketTag(item.market_id)}>
          {item.market_id === 'us' ? 'US' : 'EGX'}
        </span>
      </td>
      <td style={td}>{item.trade_horizon}</td>
      <td style={td}>
        <span style={recTag(item.recommendation)}>
          {item.recommendation || '--'}
        </span>
      </td>
      <td style={td}>{formatConfidence(item.confidence)}</td>
      <td style={td}>
        {hasReturn ? (
          <span style={{ color: returnPct >= 0 ? '#10b981' : '#ef4444', fontWeight: 600 }}>
            {returnPct >= 0 ? '+' : ''}{returnPct.toFixed(2)}%
          </span>
        ) : canSimulate ? (
          <button
            style={simBtn}
            onClick={(e) => { e.stopPropagation(); handleSimulate(); }}
            disabled={simulating}
          >
            {simulating ? '...' : 'Simulate'}
          </button>
        ) : (
          <span style={{ color: 'var(--text3)' }}>--</span>
        )}
      </td>
      <td style={td}>
        <button style={viewBtn} onClick={() => onView(item.id)}>
          View
        </button>
      </td>
    </tr>
  );
}

export default function HistoryTable({ items, onView, onRefresh, selectedIds, onToggleSelect }: HistoryTableProps) {
  if (items.length === 0) {
    return <div style={emptyStyle}>No analyses found. Run your first analysis to see it here.</div>;
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={tableStyle}>
        <thead>
          <tr>
            <th style={{ ...thStyle, width: 40 }}></th>
            <th style={thStyle}>Date</th>
            <th style={thStyle}>Stock</th>
            <th style={thStyle}>Market</th>
            <th style={thStyle}>Horizon</th>
            <th style={thStyle}>Recommendation</th>
            <th style={thStyle}>Confidence</th>
            <th style={thStyle}>Outcome</th>
            <th style={thStyle}></th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <HoverRow
              key={item.id}
              item={item}
              onView={onView}
              onRefresh={onRefresh}
              selected={selectedIds.includes(item.id)}
              onToggleSelect={onToggleSelect}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}
