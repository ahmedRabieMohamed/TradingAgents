import { useEffect, useRef, useState, useCallback } from 'react';
import type { WSEvent } from '../types';

const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 2000;

interface UseWebSocketReturn {
  connected: boolean;
  send: (data: Record<string, unknown>) => void;
  close: () => void;
}

export function useWebSocket(
  url: string | null,
  onEvent: (event: WSEvent) => void
): UseWebSocketReturn {
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const retriesRef = useRef(0);
  const retryTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const onEventRef = useRef(onEvent);
  const unmountedRef = useRef(false);

  // Keep callback ref fresh without triggering reconnect
  onEventRef.current = onEvent;

  const cleanup = useCallback(() => {
    if (retryTimerRef.current) {
      clearTimeout(retryTimerRef.current);
      retryTimerRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.onopen = null;
      wsRef.current.onclose = null;
      wsRef.current.onerror = null;
      wsRef.current.onmessage = null;
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnected(false);
  }, []);

  const connect = useCallback(
    (wsUrl: string) => {
      if (unmountedRef.current) return;

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        if (unmountedRef.current) return;
        setConnected(true);
        retriesRef.current = 0;
      };

      ws.onmessage = (messageEvent: MessageEvent) => {
        if (unmountedRef.current) return;
        try {
          const data = JSON.parse(messageEvent.data as string) as WSEvent;
          onEventRef.current(data);
        } catch {
          // ignore malformed messages
        }
      };

      ws.onerror = () => {
        // onclose will fire after onerror
      };

      ws.onclose = () => {
        if (unmountedRef.current) return;
        setConnected(false);
        wsRef.current = null;

        if (retriesRef.current < MAX_RETRIES) {
          retriesRef.current += 1;
          retryTimerRef.current = setTimeout(() => {
            connect(wsUrl);
          }, RETRY_DELAY_MS);
        }
      };
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  useEffect(() => {
    unmountedRef.current = false;

    if (!url) {
      cleanup();
      return;
    }

    retriesRef.current = 0;
    cleanup();
    connect(url);

    return () => {
      unmountedRef.current = true;
      cleanup();
    };
  }, [url, connect, cleanup]);

  const send = useCallback((data: Record<string, unknown>) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  const close = useCallback(() => {
    retriesRef.current = MAX_RETRIES; // prevent reconnect
    cleanup();
  }, [cleanup]);

  return { connected, send, close };
}
