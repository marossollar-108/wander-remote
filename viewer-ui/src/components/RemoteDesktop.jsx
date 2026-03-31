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
  const { canvasRef, cursorCanvasRef, mouseHandlers } = useRemoteCanvas({
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
      <div className="flex-1 flex items-center justify-center bg-[#111] overflow-hidden relative">
        <div className="relative" style={{ aspectRatio: aspect, maxWidth: '100%', maxHeight: '100%' }}>
          <canvas
            ref={canvasRef}
            style={{ width: '100%', height: '100%' }}
            className="block"
          />
          <canvas
            ref={cursorCanvasRef}
            style={{ width: '100%', height: '100%', position: 'absolute', top: 0, left: 0, pointerEvents: 'none' }}
            className="block"
          />
          <div
            style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', cursor: 'none' }}
            tabIndex={0}
            {...mouseHandlers}
          />
        </div>
      </div>
    </div>
  );
}
