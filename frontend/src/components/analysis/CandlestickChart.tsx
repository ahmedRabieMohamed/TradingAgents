import { useEffect, useRef, useState, CSSProperties } from 'react';
import { createChart, CandlestickSeries, HistogramSeries, type IChartApi, type ISeriesApi, ColorType } from 'lightweight-charts';
import { getPriceHistory } from '../../services/api';
import type { OHLCBar } from '../../types';

interface CandlestickChartProps {
  ticker: string;
  marketId: string;
  currency: string;
}

const PERIODS = ['1W', '1M', '3M', '6M', '1Y'] as const;
const PERIOD_API_MAP: Record<string, string> = {
  '1W': '1w',
  '1M': '1mo',
  '3M': '3mo',
  '6M': '6mo',
  '1Y': '1y',
};

const containerStyle: CSSProperties = {
  background: 'var(--surface)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-md)',
  padding: 16,
  marginTop: 16,
  boxShadow: 'var(--shadow-sm)',
};

const headerStyle: CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: 12,
};

const titleStyle: CSSProperties = {
  fontSize: 14,
  fontWeight: 600,
  color: 'var(--text)',
};

const periodBarStyle: CSSProperties = {
  display: 'flex',
  gap: 4,
};

function periodBtnStyle(active: boolean): CSSProperties {
  return {
    padding: '4px 10px',
    fontSize: 11,
    fontWeight: active ? 600 : 400,
    border: 'none',
    borderRadius: 'var(--radius-sm)',
    background: active ? 'var(--accent)' : 'var(--surface2)',
    color: active ? '#fff' : 'var(--text3)',
    cursor: 'pointer',
  };
}

const overlayStyle: CSSProperties = {
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: 'var(--text3)',
  fontSize: 13,
  gap: 8,
  background: 'var(--surface)',
  zIndex: 1,
};

export default function CandlestickChart({ ticker, marketId, currency }: CandlestickChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);

  const [period, setPeriod] = useState('3M');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [bars, setBars] = useState<OHLCBar[]>([]);

  // Fetch data
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    getPriceHistory(ticker, marketId, PERIOD_API_MAP[period])
      .then((res) => {
        if (!cancelled) {
          setBars(res.bars);
          setLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError('Unable to load price data');
          setLoading(false);
        }
      });

    return () => { cancelled = true; };
  }, [ticker, marketId, period]);

  // Create chart once
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 300,
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#64748b',
        fontSize: 11,
      },
      grid: {
        vertLines: { color: 'rgba(30, 42, 58, 0.5)' },
        horzLines: { color: 'rgba(30, 42, 58, 0.5)' },
      },
      crosshair: {
        mode: 0,
      },
      rightPriceScale: {
        borderColor: 'rgba(30, 42, 58, 0.8)',
      },
      timeScale: {
        borderColor: 'rgba(30, 42, 58, 0.8)',
      },
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#10b981',
      downColor: '#ef4444',
      borderUpColor: '#10b981',
      borderDownColor: '#ef4444',
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
    });

    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: 'volume' },
      priceScaleId: 'volume',
    });

    volumeSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    volumeSeriesRef.current = volumeSeries;

    // Resize observer
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        chart.applyOptions({ width: entry.contentRect.width });
      }
    });
    resizeObserver.observe(chartContainerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
      candleSeriesRef.current = null;
      volumeSeriesRef.current = null;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Update chart data when bars change
  useEffect(() => {
    if (!candleSeriesRef.current || !volumeSeriesRef.current || bars.length === 0) return;

    const candleData = bars.map((b) => ({
      time: (period === '1W' ? Math.floor(new Date(b.timestamp).getTime() / 1000) : b.timestamp.slice(0, 10)) as any,
      open: b.open,
      high: b.high,
      low: b.low,
      close: b.close,
    }));

    const volumeData = bars.map((b) => ({
      time: (period === '1W' ? Math.floor(new Date(b.timestamp).getTime() / 1000) : b.timestamp.slice(0, 10)) as any,
      value: b.volume,
      color: b.close >= b.open ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)',
    }));

    candleSeriesRef.current.setData(candleData);
    volumeSeriesRef.current.setData(volumeData);

    chartRef.current?.timeScale().applyOptions({
      timeVisible: period === '1W',
    });

    chartRef.current?.timeScale().fitContent();
  }, [bars, period]);

  const showOverlay = loading || error !== null || bars.length === 0;

  return (
    <div style={containerStyle}>
      <div style={headerStyle}>
        <span style={titleStyle}>
          {ticker} Price Chart ({currency})
        </span>
        <div style={periodBarStyle}>
          {PERIODS.map((p) => (
            <button
              key={p}
              style={periodBtnStyle(p === period)}
              onClick={() => setPeriod(p)}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      <div style={{ position: 'relative', height: 300 }}>
        {showOverlay && (
          <div style={overlayStyle}>
            {loading && (
              <>
                <span className="spinner" />
                Loading chart data...
              </>
            )}
            {!loading && error && <span>{error}</span>}
            {!loading && !error && bars.length === 0 && (
              <span>No price data available for this period</span>
            )}
          </div>
        )}
        <div ref={chartContainerRef} style={{ height: 300 }} />
      </div>
    </div>
  );
}
