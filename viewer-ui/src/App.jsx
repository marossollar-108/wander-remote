import { useState, useCallback } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import ConnectScreen from './components/ConnectScreen';
import RemoteDesktop from './components/RemoteDesktop';

export default function App() {
  const [credentials, setCredentials] = useState(null);

  const {
    status,
    latency,
    hostScreen,
    lastFrame,
    lastDelta,
    error,
    connect,
    disconnect,
    send,
  } = useWebSocket();

  const handleConnect = useCallback(
    (sessionId, password) => {
      setCredentials({ sessionId, password });
      connect(sessionId, password);
    },
    [connect]
  );

  const handleDisconnect = useCallback(() => {
    disconnect();
    setCredentials(null);
  }, [disconnect]);

  if (status === 'connected' && hostScreen) {
    return (
      <RemoteDesktop
        hostScreen={hostScreen}
        lastFrame={lastFrame}
        lastDelta={lastDelta}
        latency={latency}
        sessionId={credentials?.sessionId}
        send={send}
        onDisconnect={handleDisconnect}
      />
    );
  }

  return (
    <ConnectScreen
      status={status}
      error={error}
      onConnect={handleConnect}
    />
  );
}
