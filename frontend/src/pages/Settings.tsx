import { useState, useEffect } from 'react';
import { Card, Form, Input, Select, InputNumber, Button, Spin, Space, Typography, message } from 'antd';
import { getSettings, updateSettings } from '../services/api';
import type { UserSettings, SettingsUpdate, TradeHorizon, ResearchDepth } from '../types';
import Topbar from '../components/layout/Topbar';
import { useTranslation } from 'react-i18next';

const { Title, Text } = Typography;

const API_KEY_FIELDS = [
  { key: 'openai', label: 'OpenAI' },
  { key: 'anthropic', label: 'Anthropic' },
  { key: 'google', label: 'Google' },
  { key: 'xai', label: 'xAI' },
  { key: 'serper', label: 'Serper' },
  { key: 'alpha_vantage', label: 'Alpha Vantage' },
];

const HORIZONS: TradeHorizon[] = ['intraday', 'short-term', 'medium-term', 'long-term'];
const DEPTHS: ResearchDepth[] = ['shallow', 'medium', 'deep'];
const MARKETS = ['us', 'egx'];
const LLM_PROVIDERS = ['openai', 'anthropic', 'google', 'xai'];

export default function Settings() {
  const { t } = useTranslation(['settings', 'common']);
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [apiKeys, setApiKeys] = useState<Record<string, string>>({});
  const [defaultMarket, setDefaultMarket] = useState('us');
  const [defaultHorizon, setDefaultHorizon] = useState<TradeHorizon>('short-term');
  const [defaultDepth, setDefaultDepth] = useState<ResearchDepth>('medium');
  const [defaultLLM, setDefaultLLM] = useState('openai');
  const [startingBalance, setStartingBalance] = useState(100000);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [messageApi, contextHolder] = message.useMessage();

  useEffect(() => {
    getSettings()
      .then((s) => {
        setSettings(s);
        setDefaultMarket(s.default_market);
        setDefaultHorizon(s.default_horizon);
        setDefaultDepth(s.default_depth);
        setDefaultLLM(s.default_llm_provider);
        // Initialize empty api key strings; the server only tells us which are configured (boolean)
        const keys: Record<string, string> = {};
        API_KEY_FIELDS.forEach(({ key }) => {
          keys[key] = '';
        });
        setApiKeys(keys);
      })
      .catch(() => {
        void messageApi.error(t('common:status.error'));
      })
      .finally(() => setLoading(false));
  }, []);

  async function handleSave() {
    setSaving(true);
    try {
      const payload: SettingsUpdate = {
        default_market: defaultMarket,
        default_horizon: defaultHorizon,
        default_depth: defaultDepth,
        default_llm_provider: defaultLLM,
        starting_balance: startingBalance,
      };
      // Only include api keys that have been filled in
      const filledKeys: Record<string, string> = {};
      let hasKeys = false;
      Object.entries(apiKeys).forEach(([k, v]) => {
        if (v.trim()) {
          filledKeys[k] = v.trim();
          hasKeys = true;
        }
      });
      if (hasKeys) {
        payload.api_keys = filledKeys;
      }

      const updated = await updateSettings(payload);
      setSettings(updated);
      void messageApi.success(t('common:status.success'));
      // Clear key inputs after save
      const cleared: Record<string, string> = {};
      API_KEY_FIELDS.forEach(({ key }) => {
        cleared[key] = '';
      });
      setApiKeys(cleared);
    } catch {
      void messageApi.error(t('common:status.error'));
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <>
        <Topbar title={t('title')} />
        <div style={{ padding: 24, display: 'flex', justifyContent: 'center', marginTop: 48 }}>
          <Spin size="large" />
        </div>
      </>
    );
  }

  return (
    <>
      {contextHolder}
      <Topbar title={t('title')} />
      <div style={{ padding: 24, maxWidth: 800 }} className="fade-in">
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* API Keys */}
          <Card>
            <Title level={5} style={{ marginTop: 0, marginBottom: 16 }}>API Keys</Title>
            <Form layout="horizontal" labelCol={{ span: 8 }} wrapperCol={{ span: 16 }}>
              {API_KEY_FIELDS.map(({ key, label }) => (
                <Form.Item
                  key={key}
                  label={
                    <span>
                      {label}
                      {settings?.api_keys[key] && (
                        <Text type="success" style={{ marginLeft: 8, fontSize: 11 }}>
                          Configured
                        </Text>
                      )}
                    </span>
                  }
                >
                  <Input.Password
                    placeholder={settings?.api_keys[key] ? '********' : `Enter ${label} API key`}
                    value={apiKeys[key] || ''}
                    onChange={(e) => setApiKeys({ ...apiKeys, [key]: e.target.value })}
                  />
                </Form.Item>
              ))}
            </Form>
          </Card>

          {/* Default Configuration */}
          <Card>
            <Title level={5} style={{ marginTop: 0, marginBottom: 16 }}>{t('defaults.title')}</Title>
            <Form layout="horizontal" labelCol={{ span: 8 }} wrapperCol={{ span: 16 }}>
              <Form.Item label={t('defaults.defaultMarket')}>
                <Select
                  value={defaultMarket}
                  onChange={(val) => setDefaultMarket(val)}
                  options={MARKETS.map((m) => ({ value: m, label: m.toUpperCase() }))}
                />
              </Form.Item>

              <Form.Item label={t('defaults.defaultHorizon')}>
                <Select
                  value={defaultHorizon}
                  onChange={(val) => setDefaultHorizon(val)}
                  options={HORIZONS.map((h) => ({ value: h, label: h }))}
                />
              </Form.Item>

              <Form.Item label={t('defaults.defaultDepth')}>
                <Select
                  value={defaultDepth}
                  onChange={(val) => setDefaultDepth(val)}
                  options={DEPTHS.map((d) => ({ value: d, label: d }))}
                />
              </Form.Item>

              <Form.Item label="LLM Provider">
                <Select
                  value={defaultLLM}
                  onChange={(val) => setDefaultLLM(val)}
                  options={LLM_PROVIDERS.map((p) => ({ value: p, label: p }))}
                />
              </Form.Item>
            </Form>
          </Card>

          {/* Paper Trading */}
          <Card>
            <Title level={5} style={{ marginTop: 0, marginBottom: 16 }}>Paper Trading</Title>
            <Form layout="horizontal" labelCol={{ span: 8 }} wrapperCol={{ span: 16 }}>
              <Form.Item label="Starting Balance">
                <InputNumber
                  style={{ width: '100%' }}
                  min={1000}
                  step={1000}
                  value={startingBalance}
                  onChange={(val) => setStartingBalance(val ?? 100000)}
                />
              </Form.Item>
            </Form>
            <Text type="secondary" style={{ fontSize: 11 }}>
              Changes apply on next portfolio reset.
            </Text>
          </Card>

          {/* Save */}
          <div>
            <Button
              type="primary"
              size="large"
              loading={saving}
              onClick={handleSave}
            >
              {saving ? t('common:status.loading') : t('common:actions.save')}
            </Button>
          </div>
        </Space>
      </div>
    </>
  );
}
