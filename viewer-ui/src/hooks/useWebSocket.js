import { useState, useRef, useCallback, useEffect } from 'react';
import {
  RELAY_URL,
  PING_INTERVAL_MS,
  RECONNECT_DELAY_MS,
  MAX_RECONNECT_ATTEMPTS,
} from '../config';

/**
 * WebSocket hook for relay server communication.
 * Manages connection lifecycle, ping/pong latency, and message routing.
 */
export function useWebSocket() {
  const [status, setStatus] = useState('disconnected'); // disconnected | connecting | connected
  const [latency, setLatency] = useState(null);
  const [hostScreen, setHostScreen] = useState(null);
  const [lastFrame, setLastFrame] = useState(null);
  const [lastDelta, setLastDelta] = useState(null);
  const [error, setError] = useState(null);

  const wsRef = useRef(null);
  const pingIntervalRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const credentialsRef = useRef(null);
  const intentionalCloseRef = useRef(false);

  const cleanup = useCallback(() => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  const send = useCallback((msg) => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(msg));
    }
  }, []);

  const startPing = useCallback(() => {
    if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
    pingIntervalRef.current = setInterval(() => {
      send({ type: 'ping', timestamp: Date.now() });
    }, PING_INTERVAL_MS);
  }, [send]);

  const connectWs = useCallback(
    (sessionId, password) => {
      cleanup();
      intentionalCloseRef.current = false;

      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }

      credentialsRef.current = { sessionId, password };
      setStatus('connecting');
      setError(null);

      const ws = new WebSocket(RELAY_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        reconnectAttemptsRef.current = 0;
        send({
          type: 'viewer_connect',
          session_id: sessionId,
          password: password,
        });
      };

      ws.onmessage = (event) => {
        let msg;
        try {
          msg = JSON.parse(event.data);
        } catch {
          return;
        }

        switch (msg.type) {
          case 'connect_success':
            setStatus('connected');
            setHostScreen(msg.host_screen);
            setError(null);
            startPing();
            break;

          case 'frame_full':
            setLastFrame(msg);
            break;

          case 'frame_delta':
            setLastDelta(msg);
            break;

          case 'pong':
            if (msg.timestamp) {
              setLatency(Date.now() - msg.timestamp);
            }
            break;

          case 'error':
            setError(msg.message || `Chyba: ${msg.code}`);
            break;

          case 'peer_disconnected':
            setError('Hostitel sa odpojil');
            setStatus('disconnected');
            cleanup();
            break;

          default:
            break;
        }
      };

      ws.onclose = () => {
        cleanup();
        const wasConnected = status === 'connected';

        if (
          !intentionalCloseRef.current &&
          credentialsRef.current &&
          reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS
        ) {
          setStatus('connecting');
          setError('Pripojenie stratene, pokus o znovupripojenie...');
          reconnectAttemptsRef.current += 1;
          reconnectTimeoutRef.current = setTimeout(() => {
            const c = credentialsRef.current;
            if (c) connectWs(c.sessionId, c.password);
          }, RECONNECT_DELAY_MS);
        } else if (!intentionalCloseRef.current) {
          setStatus('disconnected');
          setError('Nepodarilo sa obnovit pripojenie');
        }
      };

      ws.onerror = () => {
        setError('Chyba pripojenia k serveru');
      };
    },
    [cleanup, send, startPing, status]
  );

  const disconnect = useCallback(() => {
    intentionalCloseRef.current = true;
    credentialsRef.current = null;
    reconnectAttemptsRef.current = 0;
    cleanup();

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setStatus('disconnected');
    setHostScreen(null);
    setLastFrame(null);
    setLastDelta(null);
    setLatency(null);
    setError(null);
  }, [cleanup]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      intentionalCloseRef.current = true;
      cleanup();
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [cleanup]);

  return {
    status,
    latency,
    hostScreen,
    lastFrame,
    lastDelta,
    error,
    connect: connectWs,
    disconnect,
    send,
  };
}
