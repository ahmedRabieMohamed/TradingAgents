import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Alert, Button, Empty, Input, Popconfirm, Select, Space, Spin, Table } from 'antd';
import { useTranslation } from 'react-i18next';
import Topbar from '../components/layout/Topbar';
import { getWatchlist, addToWatchlist, removeFromWatchlist, validateStock } from '../services/api';
import type { WatchlistItem } from '../types';
import type { ColumnsType } from 'antd/es/table';

const pnlColor = (v: number | null) =>
  v == null ? 'var(--text3)' : v >= 0 ? 'var(--green)' : 'var(--red)';

export default function WatchlistPage() {
  const navigate = useNavigate();
  const { t } = useTranslation(['watchlist', 'common']);

  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [ticker, setTicker] = useState('');
  const [market, setMarket] = useState('us');
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function fetchItems() {
    getWatchlist()
      .then((res) => setItems(res.items))
      .catch(() => {})
      .finally(() => setLoading(false));
  }

  useEffect(() => { fetchItems(); }, []);

  async function handleAdd() {
    if (!ticker.trim()) return;
    setAdding(true);
    setError(null);

    try {
      const validated = await validateStock(ticker.trim(), market);
      await addToWatchlist(validated.ticker, market, validated.name);
      setTicker('');
      fetchItems();
    } catch (err: any) {
      const msg = err?.message || 'Failed to add ticker';
      setError(msg.includes('409') ? 'Already in watchlist' : msg.includes('404') ? 'Invalid ticker' : msg);
    } finally {
      setAdding(false);
    }
  }

  async function handleRemove(id: string) {
    await removeFromWatchlist(id).catch(() => {});
    setItems((prev) => prev.filter((i) => i.id !== id));
  }

  const columns: ColumnsType<WatchlistItem> = [
    {
      title: t('table.ticker'),
      dataIndex: 'ticker',
      key: 'ticker',
      render: (val: string) => <strong>{val}</strong>,
    },
    {
      title: t('table.name'),
      dataIndex: 'name',
      key: 'name',
      render: (val: string | null) => (
        <span style={{ color: 'var(--text2)' }}>{val || '—'}</span>
      ),
    },
    {
      title: t('table.market'),
      dataIndex: 'market_id',
      key: 'market_id',
      render: (val: string) => val === 'egypt' ? 'EGX' : 'US',
    },
    {
      title: t('table.price'),
      dataIndex: 'price',
      key: 'price',
      render: (_: unknown, record: WatchlistItem) =>
        record.price != null
          ? `${record.currency === 'EGP' ? 'E£' : '$'}${record.price.toFixed(2)}`
          : '—',
    },
    {
      title: t('table.change'),
      dataIndex: 'change_pct',
      key: 'change_pct',
      render: (val: number | null) => (
        <span style={{ color: pnlColor(val), fontWeight: 600 }}>
          {val != null ? `${val >= 0 ? '+' : ''}${val.toFixed(2)}%` : '—'}
        </span>
      ),
    },
    {
      title: t('table.actions'),
      key: 'actions',
      render: (_: unknown, record: WatchlistItem) => (
        <Space size="small">
          <Button
            size="small"
            type="link"
            onClick={() => navigate(`/analysis?ticker=${record.ticker}&market=${record.market_id}`)}
          >
            {t('common:actions.startAnalysis')}
          </Button>
          <Popconfirm
            title={t('removeConfirm')}
            onConfirm={() => handleRemove(record.id)}
            okText={t('common:actions.remove')}
            cancelText="Cancel"
          >
            <Button size="small" danger>
              {t('common:actions.remove')}
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  if (loading) {
    return (
      <>
        <Topbar title={t('title')} />
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', gap: 8 }}>
          <Spin size="large" />
          <span>{t('common:status.loading')}</span>
        </div>
      </>
    );
  }

  return (
    <>
      <Topbar title={t('title')} />
      <div style={{ padding: 24, maxWidth: 900 }}>
        {/* Add bar */}
        <Space style={{ marginBottom: 20, width: '100%' }} wrap>
          <Select
            value={market}
            onChange={(val) => setMarket(val)}
            style={{ width: 120 }}
            options={[
              { value: 'us', label: 'US' },
              { value: 'egypt', label: 'Egypt' },
            ]}
          />
          <Input
            style={{ width: 300 }}
            placeholder={t('tickerPlaceholder')}
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            onPressEnter={handleAdd}
          />
          <Button type="primary" onClick={handleAdd} loading={adding}>
            {adding ? t('common:status.loading') : t('common:actions.add')}
          </Button>
        </Space>

        {error && (
          <Alert
            type="error"
            message={error}
            showIcon
            closable
            onClose={() => setError(null)}
            style={{ marginBottom: 16 }}
          />
        )}

        {items.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={
              <span>
                <span style={{ display: 'block', fontSize: 14, color: 'var(--text2)' }}>
                  {t('empty')}
                </span>
                <span style={{ fontSize: 12 }}>Add tickers above to track them.</span>
              </span>
            }
            style={{ padding: 60 }}
          />
        ) : (
          <Table<WatchlistItem>
            rowKey="id"
            columns={columns}
            dataSource={items}
            pagination={false}
            size="middle"
            scroll={{ x: true }}
          />
        )}
      </div>
    </>
  );
}
