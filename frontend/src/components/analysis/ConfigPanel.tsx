import { useState } from 'react';
import type { CSSProperties } from 'react';
import type { AnalysisRequest, TradeHorizon, AnalystType, ResearchDepth } from '../../types';

interface ConfigPanelProps {
  onStart: (config: Partial<AnalysisRequest>) => void;
  ticker: string;
  marketId: string;
}

// --- Provider model lists ---

const PROVIDER_MODELS: Record<string, { quick: string[]; deep: string[] }> = {
  openai: {
    quick: ['gpt-4o-mini', 'gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    deep: ['o1', 'o1-mini', 'o3-mini', 'gpt-4o'],
  },
  anthropic: {
    quick: ['claude-3-5-haiku-latest', 'claude-3-5-sonnet-latest', 'claude-sonnet-4-20250514'],
    deep: ['claude-opus-4-20250514', 'claude-sonnet-4-20250514', 'claude-3-5-sonnet-latest'],
  },
  google: {
    quick: ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro'],
    deep: ['gemini-2.0-pro', 'gemini-1.5-pro', 'gemini-2.5-pro-preview-06-05'],
  },
  xai: {
    quick: ['grok-2', 'grok-2-mini'],
    deep: ['grok-2', 'grok-3'],
  },
  openrouter: {
    quick: ['openai/gpt-4o-mini', 'anthropic/claude-3-5-haiku', 'google/gemini-2.0-flash'],
    deep: ['openai/o1', 'anthropic/claude-opus-4', 'google/gemini-2.5-pro'],
  },
  ollama: {
    quick: ['llama3.1:8b', 'mistral:7b', 'phi3:mini', 'gemma2:9b'],
    deep: ['llama3.1:70b', 'mixtral:8x7b', 'qwen2.5:72b', 'deepseek-r1:32b'],
  },
};

const HORIZON_OPTIONS: { value: TradeHorizon; label: string; desc: string }[] = [
  { value: 'intraday', label: 'Intraday', desc: 'Same day' },
  { value: 'short-term', label: 'Short-term', desc: '1-5 days' },
  { value: 'medium-term', label: 'Medium-term', desc: '1-4 weeks' },
  { value: 'long-term', label: 'Long-term', desc: '1-6 months' },
];

const ANALYST_OPTIONS: { value: AnalystType; label: string }[] = [
  { value: 'market', label: 'Market Analyst' },
  { value: 'news', label: 'News Analyst' },
  { value: 'social', label: 'Social Media Analyst' },
  { value: 'fundamentals', label: 'Fundamentals Analyst' },
];

const DEPTH_OPTIONS: { value: ResearchDepth; label: string; rounds: number }[] = [
  { value: 'shallow', label: 'Shallow', rounds: 1 },
  { value: 'medium', label: 'Medium', rounds: 3 },
  { value: 'deep', label: 'Deep', rounds: 5 },
];

const PROVIDER_OPTIONS = [
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'google', label: 'Google' },
  { value: 'xai', label: 'xAI' },
  { value: 'openrouter', label: 'OpenRouter' },
  { value: 'ollama', label: 'Ollama' },
];

// --- Styles ---

const panelStyle: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 24,
};

const sectionLabel: CSSProperties = {
  fontSize: 13,
  fontWeight: 600,
  color: 'var(--text2)',
  marginBottom: 8,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
};

const optionRow: CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: 8,
};

function optionBtnStyle(selected: boolean): CSSProperties {
  return {
    padding: '8px 16px',
    borderRadius: 'var(--radius-sm)',
    border: selected ? '1.5px solid var(--accent)' : '1px solid var(--border)',
    background: selected ? 'rgba(99, 102, 241, 0.1)' : 'var(--surface)',
    color: selected ? 'var(--accent)' : 'var(--text2)',
    cursor: 'pointer',
    fontSize: 13,
    fontWeight: selected ? 600 : 400,
    transition: 'all 0.15s ease',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 2,
  };
}

const checkboxRow: CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: 12,
};

function checkboxLabelStyle(checked: boolean): CSSProperties {
  return {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    padding: '6px 12px',
    borderRadius: 'var(--radius-sm)',
    border: checked ? '1.5px solid var(--accent)' : '1px solid var(--border)',
    background: checked ? 'rgba(99, 102, 241, 0.1)' : 'var(--surface)',
    color: checked ? 'var(--accent)' : 'var(--text2)',
    cursor: 'pointer',
    fontSize: 13,
    fontWeight: checked ? 600 : 400,
    transition: 'all 0.15s ease',
  };
}

const selectStyle: CSSProperties = {
  padding: '8px 12px',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid var(--border)',
  background: 'var(--surface)',
  color: 'var(--text)',
  fontSize: 13,
  minWidth: 200,
  outline: 'none',
};

const dateInputStyle: CSSProperties = {
  padding: '8px 12px',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid var(--border)',
  background: 'var(--surface)',
  color: 'var(--text)',
  fontSize: 13,
  outline: 'none',
  colorScheme: 'dark',
};

const startBtnStyle: CSSProperties = {
  padding: '12px 32px',
  borderRadius: 'var(--radius-sm)',
  border: 'none',
  background: 'var(--green)',
  color: '#fff',
  fontSize: 15,
  fontWeight: 700,
  cursor: 'pointer',
  alignSelf: 'flex-start',
  transition: 'opacity 0.15s ease',
};

const modelRow: CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: 16,
  alignItems: 'flex-end',
};

const modelGroup: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 4,
};

const modelLabel: CSSProperties = {
  fontSize: 11,
  color: 'var(--text3)',
  fontWeight: 500,
};

// --- Component ---

function formatToday(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

export default function ConfigPanel({ onStart, ticker, marketId }: ConfigPanelProps) {
  const [horizon, setHorizon] = useState<TradeHorizon>('short-term');
  const [analysts, setAnalysts] = useState<AnalystType[]>(['market', 'news', 'social', 'fundamentals']);
  const [depth, setDepth] = useState<ResearchDepth>('medium');
  const [provider, setProvider] = useState('openai');
  const [quickModel, setQuickModel] = useState(PROVIDER_MODELS.openai.quick[0]);
  const [deepModel, setDeepModel] = useState(PROVIDER_MODELS.openai.deep[0]);
  const [analysisDate, setAnalysisDate] = useState(formatToday());

  function handleProviderChange(newProvider: string) {
    setProvider(newProvider);
    const models = PROVIDER_MODELS[newProvider];
    setQuickModel(models.quick[0]);
    setDeepModel(models.deep[0]);
  }

  function toggleAnalyst(a: AnalystType) {
    setAnalysts((prev) =>
      prev.includes(a) ? prev.filter((x) => x !== a) : [...prev, a]
    );
  }

  function handleStart() {
    onStart({
      ticker,
      market_id: marketId,
      analysis_date: analysisDate,
      trade_horizon: horizon,
      analysts,
      research_depth: depth,
      llm_provider: provider,
      quick_think_model: quickModel,
      deep_think_model: deepModel,
    });
  }

  const currentModels = PROVIDER_MODELS[provider];

  return (
    <div style={panelStyle}>
      {/* Trade Horizon */}
      <div>
        <div style={sectionLabel}>Trade Horizon</div>
        <div style={optionRow}>
          {HORIZON_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              style={optionBtnStyle(horizon === opt.value)}
              onClick={() => setHorizon(opt.value)}
            >
              <span>{opt.label}</span>
              <span style={{ fontSize: 10, opacity: 0.7 }}>{opt.desc}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Analyst Team */}
      <div>
        <div style={sectionLabel}>Analyst Team</div>
        <div style={checkboxRow}>
          {ANALYST_OPTIONS.map((opt) => {
            const checked = analysts.includes(opt.value);
            return (
              <label key={opt.value} style={checkboxLabelStyle(checked)}>
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => toggleAnalyst(opt.value)}
                  style={{ accentColor: 'var(--accent)' }}
                />
                {opt.label}
              </label>
            );
          })}
        </div>
      </div>

      {/* Research Depth */}
      <div>
        <div style={sectionLabel}>Research Depth</div>
        <div style={optionRow}>
          {DEPTH_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              style={optionBtnStyle(depth === opt.value)}
              onClick={() => setDepth(opt.value)}
            >
              <span>{opt.label}</span>
              <span style={{ fontSize: 10, opacity: 0.7 }}>{opt.rounds} round{opt.rounds > 1 ? 's' : ''}</span>
            </button>
          ))}
        </div>
      </div>

      {/* LLM Provider */}
      <div>
        <div style={sectionLabel}>LLM Provider</div>
        <div style={optionRow}>
          {PROVIDER_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              style={optionBtnStyle(provider === opt.value)}
              onClick={() => handleProviderChange(opt.value)}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Model Selection */}
      <div>
        <div style={sectionLabel}>Models</div>
        <div style={modelRow}>
          <div style={modelGroup}>
            <span style={modelLabel}>Quick-think model</span>
            <select
              style={selectStyle}
              value={quickModel}
              onChange={(e) => setQuickModel(e.target.value)}
            >
              {currentModels.quick.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>
          <div style={modelGroup}>
            <span style={modelLabel}>Deep-think model</span>
            <select
              style={selectStyle}
              value={deepModel}
              onChange={(e) => setDeepModel(e.target.value)}
            >
              {currentModels.deep.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Analysis Date */}
      <div>
        <div style={sectionLabel}>Analysis Date</div>
        <input
          type="date"
          style={dateInputStyle}
          value={analysisDate}
          onChange={(e) => setAnalysisDate(e.target.value)}
        />
      </div>

      {/* Start Button */}
      <button
        style={{
          ...startBtnStyle,
          opacity: analysts.length === 0 ? 0.5 : 1,
        }}
        disabled={analysts.length === 0}
        onClick={handleStart}
      >
        Start Analysis
      </button>
    </div>
  );
}
