export const RELAY_URL = import.meta.env.VITE_RELAY_URL || 'ws://localhost:8765';

export const QUALITY_PRESETS = {
  low: { quality: 20, max_fps: 10, label: 'Nizka' },
  medium: { quality: 40, max_fps: 15, label: 'Stredna' },
  high: { quality: 70, max_fps: 30, label: 'Vysoka' },
};

export const MOUSE_THROTTLE_MS = 1000 / 60; // 60 per second
export const PING_INTERVAL_MS = 3000;
export const RECONNECT_DELAY_MS = 3000;
export const MAX_RECONNECT_ATTEMPTS = 5;
