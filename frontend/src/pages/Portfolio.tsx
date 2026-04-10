import { useState } from 'react';
import {
  Tabs,
  Button,
  Modal,
  Spin,
  Alert,
  Empty,
  Typography,
  Space,
} from 'antd';
import { useTranslation } from 'react-i18next';
import Topbar from '../components/layout/Topbar';
import PortfolioSummary from '../components/portfolio/PortfolioSummary';
import PositionsTable from '../components/portfolio/PositionsTable';
import TradeHistory from '../components/portfolio/TradeHistory';
import PortfolioAnalytics from '../components/portfolio/PortfolioAnalytics';
import AIComparison from '../components/portfolio/AIComparison';
import { usePortfolio } from '../hooks/usePortfolio';
import { resetPortfolio } from '../services/api';

const { Title } = Typography;

type Tab = 'positions' | 'history' | 'analytics';

export default function Portfolio() {
  const { portfolio, loading, error, refresh } = usePortfolio();
  const [activeTab, setActiveTab] = useState<Tab>('positions');
  const [resetting, setResetting] = useState(false);
  const { t } = useTranslation(['portfolio', 'common']);

  async function handleReset() {
    setResetting(true);
    try {
      await resetPortfolio();
      refresh();
    } catch {
      // keep dialog open on error — Modal.confirm handles closure
    } finally {
      setResetting(false);
    }
  }

  function confirmReset() {
    Modal.confirm({
      title: 'Reset Portfolio?',
      content:
        'This will close all positions and reset your balance. This action cannot be undone.',
      okText: 'Yes, Reset',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: handleReset,
    });
  }

  const tabItems = [
    {
      key: 'positions',
      label: t('positions.title'),
      children:
        portfolio ? (
          <PositionsTable positions={portfolio.open_positions} onRefresh={refresh} />
        ) : null,
    },
    {
      key: 'history',
      label: t('trades.title'),
      children: <TradeHistory />,
    },
    {
      key: 'analytics',
      label: 'Analytics',
      children: (
        <>
          <PortfolioAnalytics />
          <AIComparison />
        </>
      ),
    },
  ];

  return (
    <>
      <Topbar title={t('title')} />
      <div style={{ padding: 24, maxWidth: 1100 }}>

        {loading && !portfolio && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: '60vh',
            }}
          >
            <Spin size="large" tip={t('common:status.loading')} />
          </div>
        )}

        {error && !portfolio && (
          <Alert
            type="error"
            message="Failed to load portfolio"
            description={error}
            showIcon
            action={
              <Button size="small" onClick={refresh}>
                {t('common:actions.retry')}
              </Button>
            }
          />
        )}

        {!loading && !error && !portfolio && (
          <Empty
            description={
              <span>
                <strong>{t('empty')}</strong>
                <br />
                Execute your first trade from an analysis to get started.
              </span>
            }
            style={{ padding: 64 }}
          />
        )}

        {portfolio && (
          <>
            <Space
              style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}
              align="center"
            >
              <Title level={4} style={{ margin: 0 }}>
                {t('title')}
              </Title>
              <Button danger onClick={confirmReset} loading={resetting}>
                Reset Portfolio
              </Button>
            </Space>

            <PortfolioSummary portfolio={portfolio} />

            <Tabs
              activeKey={activeTab}
              onChange={(key) => setActiveTab(key as Tab)}
              items={tabItems}
              style={{ marginTop: 20 }}
            />
          </>
        )}

      </div>
    </>
  );
}
