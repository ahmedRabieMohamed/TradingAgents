import { create } from 'zustand';
import type { StockValidation, TradeHorizon } from '../types';

interface WizardState {
  step: number;
  selectedMarket: string | null;
  selectedStock: StockValidation | null;
  tradeHorizon: TradeHorizon;
  analysisDate: string;
  showCustomTicker: boolean;
  wsUrl: string | null;

  setStep: (step: number) => void;
  setSelectedMarket: (market: string | null) => void;
  setSelectedStock: (stock: StockValidation | null) => void;
  setTradeHorizon: (horizon: TradeHorizon) => void;
  setAnalysisDate: (date: string) => void;
  setShowCustomTicker: (show: boolean) => void;
  setWsUrl: (url: string | null) => void;
  reset: () => void;
}

const INITIAL_STATE = {
  step: 0,
  selectedMarket: null as string | null,
  selectedStock: null as StockValidation | null,
  tradeHorizon: 'short-term' as TradeHorizon,
  analysisDate: '',
  showCustomTicker: false,
  wsUrl: null as string | null,
};

export const useWizardStore = create<WizardState>((set) => ({
  ...INITIAL_STATE,

  setStep: (step) => set({ step }),
  setSelectedMarket: (market) => set({ selectedMarket: market }),
  setSelectedStock: (stock) => set({ selectedStock: stock }),
  setTradeHorizon: (horizon) => set({ tradeHorizon: horizon }),
  setAnalysisDate: (date) => set({ analysisDate: date }),
  setShowCustomTicker: (show) => set({ showCustomTicker: show }),
  setWsUrl: (url) => set({ wsUrl: url }),
  reset: () => set({ ...INITIAL_STATE }),
}));
