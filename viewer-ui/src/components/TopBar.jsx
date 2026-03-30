import { useState, useCallback } from 'react';
import { QUALITY_PRESETS } from '../config';

const LOGO_URL =
  'https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR.svg';

export default function TopBar({ sessionId, latency, send, onDisconnect }) {
  const [quality, setQuality] = useState('medium');

  const handleQualityChange = useCallback(
    (e) => {
      const key = e.target.value;
      setQuality(key);
      const preset = QUALITY_PRESETS[key];
      if (preset) {
        send({
          type: 'quality_change',
          quality: preset.quality,
          max_fps: preset.max_fps,
        });
      }
    },
    [send]
  );

  const latencyColor =
    latency == null
      ? 'bg-tk-black-40'
      : latency < 50
        ? 'bg-green-500'
        : latency < 150
          ? 'bg-yellow-500'
          : 'bg-primary';

  return (
    <div className="flex items-center justify-between px-4 py-2 bg-white border-b border-tk-border h-14 shrink-0">
      {/* Left: Logo */}
      <div className="flex items-center gap-3">
        <img src={LOGO_URL} alt="Logo" className="h-7" />
      </div>

      {/* Center: Session + latency */}
      <div className="flex items-center gap-4 text-sm">
        <span className="font-mono text-tk-black-60">
          Relacia: <span className="text-tk-black font-semibold">{sessionId}</span>
        </span>

        <span className="flex items-center gap-1.5">
          <span
            className={`inline-block w-2 h-2 rounded-full ${latencyColor} ${
              latency == null ? 'animate-pulse-dot' : ''
            }`}
          />
          <span className="font-mono text-tk-black-60 text-xs">
            {latency != null ? `${latency} ms` : '...'}
          </span>
        </span>

        {/* Quality */}
        <select
          value={quality}
          onChange={handleQualityChange}
          className="text-xs px-2 py-1 rounded-input border border-tk-border bg-surface text-tk-black-80 focus:outline-none focus:ring-1 focus:ring-primary-ring"
        >
          {Object.entries(QUALITY_PRESETS).map(([key, preset]) => (
            <option key={key} value={key}>
              {preset.label}
            </option>
          ))}
        </select>
      </div>

      {/* Right: Disconnect */}
      <button
        onClick={onDisconnect}
        className="px-4 py-1.5 rounded-btn bg-primary text-white text-sm font-semibold hover:bg-primary-hover transition-colors focus:outline-none focus:ring-2 focus:ring-primary-ring focus:ring-offset-1"
      >
        Odpojit
      </button>
    </div>
  );
}
