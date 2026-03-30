import { useRemoteCanvas } from '../hooks/useRemoteCanvas';
import TopBar from './TopBar';

export default function RemoteDesktop({
  hostScreen,
  lastFrame,
  lastDelta,
  latency,
  sessionId,
  send,
  onDisconnect,
}) {
  const { canvasRef, mouseHandlers } = useRemoteCanvas({
    hostScreen,
    lastFrame,
    lastDelta,
    send,
  });

  // Compute aspect ratio for the canvas container
  const aspect = hostScreen
    ? `${hostScreen.width} / ${hostScreen.height}`
    : '16 / 9';

  return (
    <div className="h-screen flex flex-col bg-tk-black remote-view">
      <TopBar
        sessionId={sessionId}
        latency={latency}
        send={send}
        onDisconnect={onDisconnect}
      />

      {/* Canvas area */}
      <div className="flex-1 flex items-center justify-center bg-[#111] overflow-hidden">
        <canvas
          ref={canvasRef}
          style={{ aspectRatio: aspect, maxWidth: '100%', maxHeight: '100%' }}
          className="block cursor-crosshair"
          tabIndex={0}
          {...mouseHandlers}
        />
      </div>
    </div>
  );
}
