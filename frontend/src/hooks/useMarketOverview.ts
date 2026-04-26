import { useState, useEffect, useCallback, useRef } from 'react';
import { fetchMarketOverview } from '../services/api';
import type { MarketOverviewResponse } from '../types';

interface UseMarketOverviewResult {
  data: MarketOverviewResponse | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

export function useMarketOverview(marketId: string | null): UseMarketOverviewResult {
  const [data, setData] = useState<MarketOverviewResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const load = useCallback(async (id: string) => {
    // Cancel any in-flight request
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setLoading(true);
    setError(null);

    try {
      const result = await fetchMarketOverview(id);
      if (!controller.signal.aborted) {
        setData(result);
      }
    } catch (err: unknown) {
      if (!controller.signal.aborted) {
        const message = err instanceof Error ? err.message : 'Failed to load market overview';
        setError(message);
      }
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    if (!marketId) {
      setData(null);
      setLoading(false);
      setError(null);
      return;
    }

    load(marketId);

    return () => {
      abortRef.current?.abort();
    };
  }, [marketId, load]);

  const refresh = useCallback(() => {
    if (marketId) {
      load(marketId);
    }
  }, [marketId, load]);

  return { data, loading, error, refresh };
}
