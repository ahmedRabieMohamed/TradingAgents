import { create } from 'zustand';
import type {
  AnalysisStatus,
  WSEvent,
  WSAgentStarted,
  WSAgentCompleted,
  WSAgentMessage,
  WSStatsUpdate,
  WSAnalysisCompleted,
  WSAnalysisFailed,
} from '../types';

export interface PipelineStage {
  name: string;
  phase: string;
  status: 'waiting' | 'active' | 'done';
  description: string;
}

export interface AgentMessage {
  timestamp: string;
  agentName: string;
  content: string;
  messageType: string;
}

export interface StatsData {
  agents_completed: number;
  agents_total: number;
  llm_calls: number;
  tool_calls: number;
  tokens_in: number;
  tokens_out: number;
  reports_generated: number;
  elapsed_seconds: number;
}

interface AnalysisState {
  sessionId: string | null;
  status: AnalysisStatus | null;
  stages: PipelineStage[];
  messages: AgentMessage[];
  stats: StatsData | null;
  reports: Record<string, string>;
  recommendation: string | null;
  confidence: number | null;
  summary: string | null;
  error: string | null;

  reset: () => void;
  setSession: (id: string) => void;
  handleEvent: (event: WSEvent) => void;
}

const DEFAULT_STAGES: PipelineStage[] = [
  { name: 'Market Analyst', phase: 'research', status: 'waiting', description: 'Analyzing market data, technicals, and price action' },
  { name: 'News Analyst', phase: 'research', status: 'waiting', description: 'Scanning recent news articles and press releases' },
  { name: 'Social Media Analyst', phase: 'research', status: 'waiting', description: 'Evaluating social sentiment and trending discussions' },
  { name: 'Fundamentals Analyst', phase: 'research', status: 'waiting', description: 'Reviewing financial statements and key ratios' },
  { name: 'Bull vs Bear Debate', phase: 'debate', status: 'waiting', description: 'Investment thesis debate between bull and bear cases' },
  { name: 'Trader', phase: 'decision', status: 'waiting', description: 'Formulating trade entry, exit, and position sizing' },
  { name: 'Risk Assessment', phase: 'risk', status: 'waiting', description: 'Evaluating risk factors and downside scenarios' },
  { name: 'Portfolio Manager', phase: 'final', status: 'waiting', description: 'Final recommendation with portfolio-level context' },
];

function createInitialState() {
  return {
    sessionId: null,
    status: null,
    stages: DEFAULT_STAGES.map((s) => ({ ...s })),
    messages: [],
    stats: null,
    reports: {},
    recommendation: null,
    confidence: null,
    summary: null,
    error: null,
  };
}

export const useAnalysisStore = create<AnalysisState>((set) => ({
  ...createInitialState(),

  reset: () => set(createInitialState()),

  setSession: (id: string) =>
    set({
      ...createInitialState(),
      sessionId: id,
      status: 'running',
    }),

  handleEvent: (event: WSEvent) => {
    switch (event.type) {
      case 'agent_started':
        set((state) => {
          const e = event as WSAgentStarted;
          return {
            stages: state.stages.map((s) =>
              s.name === e.agent_name ? { ...s, status: 'active' as const } : s
            ),
          };
        });
        break;

      case 'agent_completed':
        set((state) => {
          const e = event as WSAgentCompleted;
          return {
            stages: state.stages.map((s) =>
              s.name === e.agent_name ? { ...s, status: 'done' as const } : s
            ),
            reports: { ...state.reports, [e.agent_name]: e.report_full },
          };
        });
        break;

      case 'agent_message':
        set((state) => {
          const e = event as WSAgentMessage;
          const msg: AgentMessage = {
            timestamp: e.timestamp,
            agentName: e.agent_name,
            content: e.content,
            messageType: e.message_type,
          };
          return { messages: [...state.messages, msg] };
        });
        break;

      case 'debate_round':
        set((state) => {
          const msg: AgentMessage = {
            timestamp: event.timestamp,
            agentName: 'Debate',
            content: `Round ${event.round}/${event.total_rounds} - ${event.debate_type}`,
            messageType: 'info',
          };
          return { messages: [...state.messages, msg] };
        });
        break;

      case 'stats_update':
        set(() => {
          const e = event as WSStatsUpdate;
          return {
            stats: {
              agents_completed: e.agents_completed,
              agents_total: e.agents_total,
              llm_calls: e.llm_calls,
              tool_calls: e.tool_calls,
              tokens_in: e.tokens_in,
              tokens_out: e.tokens_out,
              reports_generated: e.reports_generated,
              elapsed_seconds: e.elapsed_seconds,
            },
          };
        });
        break;

      case 'analysis_completed':
        set(() => {
          const e = event as WSAnalysisCompleted;
          return {
            status: 'completed' as const,
            recommendation: e.recommendation,
            confidence: e.confidence,
            summary: e.summary,
          };
        });
        break;

      case 'analysis_failed':
        set(() => {
          const e = event as WSAnalysisFailed;
          return {
            status: 'failed' as const,
            error: e.error,
          };
        });
        break;

      case 'analysis_cancelled':
        set(() => ({
          status: 'cancelled' as const,
        }));
        break;
    }
  },
}));
