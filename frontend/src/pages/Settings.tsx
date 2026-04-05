import { useState, useEffect, CSSProperties } from 'react';
import { getSettings, updateSettings } from '../services/api';
import type { UserSettings, SettingsUpdate, TradeHorizon, ResearchDepth } from '../types';
import Topbar from '../components/layout/Topbar';

const pageStyle: CSSProperties = {
  padding: 24,
  maxWidth: 800,
};

const cardStyle: CSSProperties = {
  background: 'var(--surface)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-lg)',
  padding: 24,
  marginBottom: 20,
};

const cardTitle: CSSProperties = {
  fontSize: 15,
  fontWeight: 600,
  color: 'var(--text)',
  marginBottom: 16,
};

const fieldRow: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  marginBottom: 14,
  gap: 16,
};

const labelStyle: CSSProperties = {
  fontSize: 13,
  color: 'var(--text2)',
  minWidth: 140,
};

const inputStyle: CSSProperties = {
  flex: 1,
  maxWidth: 340,
  padding: '8px 12px',
  background: 'var(--surface2)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  color: 'var(--text)',
  fontSize: 13,
  outline: 'none',
};

const selectStyle: CSSProperties = {
  ...inputStyle,
  cursor: 'pointer',
};

const btnStyle: CSSProperties = {
  padding: '10px 28px',
  background: 'var(--accent)',
  color: '#fff',
  border: 'none',
  borderRadius: 'var(--radius-md)',
  fontSize: 14,
  fontWeight: 600,
  cursor: 'pointer',
  transition: 'opacity 0.15s',
};

const btnDisabled: CSSProperties = {
  ...btnStyle,
  opacity: 0.5,
  cursor: 'not-allowed',
};

const feedbackSuccess: CSSProperties = {
  display: 'inline-block',
  marginLeft: 12,
  fontSize: 13,
  color: 'var(--green)',
};

const feedbackError: CSSProperties = {
  display: 'inline-block',
  marginLeft: 12,
  fontSize: 13,
  color: 'var(--red)',
};

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
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [apiKeys, setApiKeys] = useState<Record<string, string>>({});
  const [defaultMarket, setDefaultMarket] = useState('us');
  const [defaultHorizon, setDefaultHorizon] = useState<TradeHorizon>('short-term');
  const [defaultDepth, setDefaultDepth] = useState<ResearchDepth>('medium');
  const [defaultLLM, setDefaultLLM] = useState('openai');
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; msg: string } | null>(null);
  const [loading, setLoading] = useState(true);

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
        setFeedback({ type: 'error', msg: 'Failed to load settings' });
      })
      .finally(() => setLoading(false));
  }, []);

  async function handleSave() {
    setSaving(true);
    setFeedback(null);
    try {
      const payload: SettingsUpdate = {
        default_market: defaultMarket,
        default_horizon: defaultHorizon,
        default_depth: defaultDepth,
        default_llm_provider: defaultLLM,
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
      setFeedback({ type: 'success', msg: 'Settings saved successfully' });
      // Clear key inputs after save
      const cleared: Record<string, string> = {};
      API_KEY_FIELDS.forEach(({ key }) => {
        cleared[key] = '';
      });
      setApiKeys(cleared);
    } catch {
      setFeedback({ type: 'error', msg: 'Failed to save settings' });
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <>
        <Topbar title="Settings" />
        <div style={pageStyle}>
          <div className="spinner" />
        </div>
      </>
    );
  }

  return (
    <>
      <Topbar title="Settings" />
      <div style={pageStyle} className="fade-in">
        {/* API Keys */}
        <div style={cardStyle}>
          <div style={cardTitle}>API Keys</div>
          {API_KEY_FIELDS.map(({ key, label }) => (
            <div key={key} style={fieldRow}>
              <label style={labelStyle}>
                {label}
                {settings?.api_keys[key] && (
                  <span style={{ marginLeft: 8, color: 'var(--green)', fontSize: 11 }}>
                    Configured
                  </span>
                )}
              </label>
              <input
                type="password"
                style={inputStyle}
                placeholder={settings?.api_keys[key] ? '********' : `Enter ${label} API key`}
                value={apiKeys[key] || ''}
                onChange={(e) => setApiKeys({ ...apiKeys, [key]: e.target.value })}
              />
            </div>
          ))}
        </div>

        {/* Default Configuration */}
        <div style={cardStyle}>
          <div style={cardTitle}>Default Configuration</div>

          <div style={fieldRow}>
            <label style={labelStyle}>Market</label>
            <select
              style={selectStyle}
              value={defaultMarket}
              onChange={(e) => setDefaultMarket(e.target.value)}
            >
              {MARKETS.map((m) => (
                <option key={m} value={m}>
                  {m.toUpperCase()}
                </option>
              ))}
            </select>
          </div>

          <div style={fieldRow}>
            <label style={labelStyle}>Trade Horizon</label>
            <select
              style={selectStyle}
              value={defaultHorizon}
              onChange={(e) => setDefaultHorizon(e.target.value as TradeHorizon)}
            >
              {HORIZONS.map((h) => (
                <option key={h} value={h}>
                  {h}
                </option>
              ))}
            </select>
          </div>

          <div style={fieldRow}>
            <label style={labelStyle}>Research Depth</label>
            <select
              style={selectStyle}
              value={defaultDepth}
              onChange={(e) => setDefaultDepth(e.target.value as ResearchDepth)}
            >
              {DEPTHS.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>

          <div style={fieldRow}>
            <label style={labelStyle}>LLM Provider</label>
            <select
              style={selectStyle}
              value={defaultLLM}
              onChange={(e) => setDefaultLLM(e.target.value)}
            >
              {LLM_PROVIDERS.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Save */}
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <button
            style={saving ? btnDisabled : btnStyle}
            disabled={saving}
            onClick={handleSave}
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
          {feedback && (
            <span style={feedback.type === 'success' ? feedbackSuccess : feedbackError}>
              {feedback.msg}
            </span>
          )}
        </div>
      </div>
    </>
  );
}
