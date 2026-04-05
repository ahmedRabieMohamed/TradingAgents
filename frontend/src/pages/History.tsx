import { CSSProperties, useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Topbar from '../components/layout/Topbar';
import FilterBar, { type HistoryFilters } from '../components/history/FilterBar';
import HistoryTable from '../components/history/HistoryTable';
import CompareModal from '../components/history/CompareModal';
import { listAnalyses, getAnalysis, exportAnalysis } from '../services/api';
import type { AnalysisListItem, AnalysisSession } from '../types';

const pageStyle: CSSProperties = {
  padding: 24,
  maxWidth: 1200,
  margin: '0 auto',
};

const headerRow: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  gap: 12,
  marginBottom: 4,
};

const headerTitle: CSSProperties = {
  fontSize: 18,
  fontWeight: 600,
  color: 'var(--text)',
};

const headerActions: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 8,
};

const btnPrimary: CSSProperties = {
  padding: '6px 16px',
  borderRadius: 8,
  fontSize: 13,
  fontWeight: 500,
  border: 'none',
  background: 'var(--accent)',
  color: '#fff',
  cursor: 'pointer',
  transition: 'opacity 0.12s ease',
};

const btnOutline: CSSProperties = {
  padding: '6px 16px',
  borderRadius: 8,
  fontSize: 13,
  fontWeight: 500,
  border: '1px solid var(--border)',
  background: 'var(--surface2)',
  color: 'var(--text2)',
  cursor: 'pointer',
  transition: 'all 0.12s ease',
};

const loadingStyle: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: 60,
  color: 'var(--text3)',
  fontSize: 14,
};

const spinnerStyle: CSSProperties = {
  width: 20,
  height: 20,
  border: '2px solid var(--border)',
  borderTop: '2px solid var(--accent)',
  borderRadius: '50%',
  animation: 'spin 0.8s linear infinite',
  marginRight: 10,
};

const totalStyle: CSSProperties = {
  fontSize: 12,
  color: 'var(--text3)',
  marginTop: 12,
  textAlign: 'right',
};

export default function History() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<HistoryFilters>({});
  const [items, setItems] = useState<AnalysisListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Comparison state
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [compareSessions, setCompareSessions] = useState<[AnalysisSession, AnalysisSession] | null>(null);
  const [comparing, setComparing] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: Record<string, string> = {};
      if (filters.market) params.market_id = filters.market;
      if (filters.recommendation) params.recommendation = filters.recommendation;
      params.limit = '50';
      params.offset = '0';

      const res = await listAnalyses(params);
      // Backend may return { analyses: [...], total } or { items: [...], total }
      const list = (res as any).analyses || (res as any).items || [];
      setItems(list);
      setTotal(res.total);
    } catch (err: any) {
      setError(err.message || 'Failed to load analyses');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  function handleView(id: string) {
    navigate(`/?session=${id}`);
  }

  function handleToggleSelect(id: string) {
    setSelectedIds((prev) => {
      if (prev.includes(id)) return prev.filter((x) => x !== id);
      if (prev.length >= 2) return prev; // max 2
      return [...prev, id];
    });
  }

  async function handleCompare() {
    if (selectedIds.length !== 2) return;
    setComparing(true);
    try {
      const [a, b] = await Promise.all([
        getAnalysis(selectedIds[0]),
        getAnalysis(selectedIds[1]),
      ]);
      setCompareSessions([a, b]);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch analyses for comparison');
    } finally {
      setComparing(false);
    }
  }

  async function handleExportAll() {
    // Export all visible items as a simple JSON download
    const blob = new Blob([JSON.stringify(items, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analyses-export-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <>
      <Topbar title="History" />
      <div style={pageStyle}>
        <div style={headerRow}>
          <span style={headerTitle}>Analysis History</span>
          <div style={headerActions}>
            {selectedIds.length === 2 && (
              <button
                style={btnPrimary}
                onClick={handleCompare}
                disabled={comparing}
              >
                {comparing ? 'Loading...' : 'Compare Selected'}
              </button>
            )}
            {selectedIds.length > 0 && selectedIds.length < 2 && (
              <span style={{ fontSize: 12, color: 'var(--text3)' }}>
                Select 1 more to compare
              </span>
            )}
            <button style={btnOutline} onClick={handleExportAll}>
              Export All
            </button>
          </div>
        </div>

        <FilterBar filters={filters} onChange={setFilters} />

        {loading ? (
          <div style={loadingStyle}>
            <div style={spinnerStyle} />
            Loading analyses...
          </div>
        ) : error ? (
          <div style={{ ...loadingStyle, color: '#ef4444' }}>{error}</div>
        ) : (
          <>
            <HistoryTable
              items={items}
              onView={handleView}
              selectedIds={selectedIds}
              onToggleSelect={handleToggleSelect}
            />
            <div style={totalStyle}>
              Showing {items.length} of {total} analyses
            </div>
          </>
        )}
      </div>

      {compareSessions && (
        <CompareModal
          sessions={compareSessions}
          onClose={() => {
            setCompareSessions(null);
            setSelectedIds([]);
          }}
        />
      )}

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </>
  );
}
