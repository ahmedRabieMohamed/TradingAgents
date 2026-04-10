import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Alert, Button, Space, Spin, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import Topbar from '../components/layout/Topbar';
import FilterBar, { type HistoryFilters } from '../components/history/FilterBar';
import HistoryTable from '../components/history/HistoryTable';
import CompareModal from '../components/history/CompareModal';
import { listAnalyses, getAnalysis } from '../services/api';
import type { AnalysisListItem, AnalysisSession } from '../types';

const { Title, Text } = Typography;

export default function History() {
  const navigate = useNavigate();
  const { t } = useTranslation(['history', 'common']);
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
    navigate(`/analysis?session=${id}`);
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
      <Topbar title={t('title')} />
      <div style={{ padding: 24, maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, marginBottom: 4 }}>
          <Title level={4} style={{ margin: 0 }}>{t('title')}</Title>
          <Space>
            {selectedIds.length > 0 && selectedIds.length < 2 && (
              <Text type="secondary" style={{ fontSize: 12 }}>
                Select 1 more to compare
              </Text>
            )}
            {selectedIds.length === 2 && (
              <Button
                type="primary"
                onClick={handleCompare}
                loading={comparing}
              >
                {t('common:actions.compare')}
              </Button>
            )}
            <Button onClick={handleExportAll}>
              {t('common:actions.export')}
            </Button>
          </Space>
        </div>

        <FilterBar filters={filters} onChange={setFilters} />

        {loading ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 60 }}>
            <Spin size="default" />
          </div>
        ) : error ? (
          <Alert
            type="error"
            message={error}
            style={{ marginTop: 16 }}
            showIcon
          />
        ) : (
          <>
            <HistoryTable
              items={items}
              onView={handleView}
              onRefresh={fetchData}
              selectedIds={selectedIds}
              onToggleSelect={handleToggleSelect}
            />
            <Text type="secondary" style={{ display: 'block', fontSize: 12, marginTop: 12, textAlign: 'right' }}>
              Showing {items.length} of {total} analyses
            </Text>
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
    </>
  );
}
