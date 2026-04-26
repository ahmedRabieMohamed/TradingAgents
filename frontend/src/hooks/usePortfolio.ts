import { useState, useEffect, useCallback, useRef } from 'react';
import { getPortfolio } from '../services/api';
import type { PortfolioResponse } from '../types';

interface UsePortfolioReturn {
  portfolio: PortfolioResponse | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

export function usePortfolio(): UsePortfolioReturn {
  const [portfolio, setPortfolio] = useState<PortfolioResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchPortfolio = useCallback(async () => {
    try {
      const data = await getPortfolio();
      setPortfolio(data);
      setError(null);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load portfolio';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const refresh = useCallback(() => {
    setLoading(true);
    fetchPortfolio();
  }, [fetchPortfolio]);

  useEffect(() => {
    fetchPortfolio();

    intervalRef.current = setInterval(fetchPortfolio, 60000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [fetchPortfolio]);

  return { portfolio, loading, error, refresh };
}
