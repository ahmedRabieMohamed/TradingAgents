import { create } from 'zustand';

interface MarketState {
  marketId: string | null;
  marketLabel: string;
  setMarket: (id: string, label: string) => void;
}

export const useMarketStore = create<MarketState>((set) => ({
  marketId: null,
  marketLabel: 'No market selected',
  setMarket: (id, label) => set({ marketId: id, marketLabel: label }),
}));
