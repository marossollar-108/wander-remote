import 'dotenv/config';
import { WebSocketServer } from 'ws';
import crypto from 'crypto';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const PORT = parseInt(process.env.PORT || '8765');
const MAX_SESSIONS = parseInt(process.env.MAX_SESSIONS || '100');
const SESSION_TIMEOUT_MS = parseInt(process.env.SESSION_TIMEOUT_MS || '300000');
const RATE_LIMIT_PER_MIN = parseInt(process.env.RATE_LIMIT_PER_MIN || '100');
const MAX_FAILED_ATTEMPTS_PER_MIN = 5;
const DEVICES_FILE = path.join(__dirname, 'devices.json');

// In-memory storage
const sessions = new Map();
const ipConnections = new Map(); // IP -> { count, resetAt }
const ipFailedAttempts = new Map(); // IP -> { count, resetAt }

// Persistent device registry
// { [host_id]: { host_id, name, first_seen, last_seen, ip } }
let devices = {};

function loadDevices() {
  try {
    const data = fs.readFileSync(DEVICES_FILE, 'utf-8');
    devices = JSON.parse(data);
    log(`Loaded ${Object.keys(devices).length} devices from registry`);
  } catch {
    devices = {};
    log('No devices registry found, starting fresh');
  }
}

function saveDevices() {
  fs.writeFileSync(DEVICES_FILE, JSON.stringify(devices, null, 2), 'utf-8');
}

function registerDevice(hostId, ip) {
  const now = new Date().toISOString();
  if (devices[hostId]) {
    devices[hostId].last_seen = now;
    devices[hostId].ip = ip;
  } else {
    devices[hostId] = {
      host_id: hostId,
      name: null,
      password: null,
      first_seen: now,
      last_seen: now,
      ip,
    };
  }
  saveDevices();
  return devices[hostId];
}

// Vrat existujuce heslo alebo vygeneruj nove a uloz
function getOrCreatePassword(hostId) {
  const device = devices[hostId];
  if (device && device.password) {
    return device.password;
  }
  const password = generatePassword();
  if (device) {
    device.password = password;
    saveDevices();
  }
  return password;
}

function log(msg) {
  console.log(`[${new Date().toISOString()}] ${msg}`);
}

function generatePassword() {
  return crypto.randomBytes(3).toString('hex'); // 6 hex chars
}

function getClientIp(req) {
  return req.headers['x-forwarded-for']?.split(',')[0]?.trim() || req.socket.remoteAddress;
}

function checkRateLimit(ip) {
  const now = Date.now();
  let record = ipConnections.get(ip);
  if (!record || now > record.resetAt) {
    record = { count: 0, resetAt: now + 60000 };
    ipConnections.set(ip, record);
  }
  record.count++;
  return record.count <= RATE_LIMIT_PER_MIN;
}

function checkFailedAttempts(ip) {
  const now = Date.now();
  let record = ipFailedAttempts.get(ip);
  if (!record || now > record.resetAt) {
    record = { count: 0, resetAt: now + 60000 };
    ipFailedAttempts.set(ip, record);
  }
  record.count++;
  return record.count <= MAX_FAILED_ATTEMPTS_PER_MIN;
}

function cleanupSession(sessionId) {
  const session = sessions.get(sessionId);
  if (!session) return;
  if (session.timeout) clearTimeout(session.timeout);
  sessions.delete(sessionId);
  log(`Session ${sessionId} removed`);
}

function resetSessionTimeout(sessionId) {
  const session = sessions.get(sessionId);
  if (!session) return;
  if (session.timeout) clearTimeout(session.timeout);
  session.timeout = setTimeout(() => {
    log(`Session ${sessionId} timed out`);
    const s = sessions.get(sessionId);
    if (s) {
      const msg = JSON.stringify({ type: 'peer_disconnected' });
      if (s.host?.readyState === 1) s.host.close(1000, 'timeout');
      if (s.viewer?.readyState === 1) s.viewer.close(1000, 'timeout');
    }
    cleanupSession(sessionId);
  }, SESSION_TIMEOUT_MS);
}

// Message types that go host -> viewer
const HOST_TO_VIEWER = new Set(['frame_full', 'frame_delta']);
// Message types that go viewer -> host
const VIEWER_TO_HOST = new Set([
  'mouse_move', 'mouse_click', 'mouse_scroll',
  'key_event', 'key_combo', 'quality_change'
]);

function sendJson(ws, data) {
  if (ws?.readyState === 1) {
    ws.send(JSON.stringify(data));
  }
}

loadDevices();

const wss = new WebSocketServer({ port: PORT });

wss.on('listening', () => {
  log(`Relay server listening on ws://0.0.0.0:${PORT}`);
  log(`Registered devices: ${Object.keys(devices).length}`);
});

wss.on('connection', (ws, req) => {
  const ip = getClientIp(req);

  if (!checkRateLimit(ip)) {
    log(`Rate limit exceeded for ${ip}`);
    sendJson(ws, { type: 'error', code: 'rate_limited', message: 'Too many connections' });
    ws.close(1008, 'rate_limited');
    return;
  }

  log(`New connection from ${ip}`);

  let role = null;     // 'host' | 'viewer'
  let sessionId = null;

  ws.on('message', (raw, isBinary) => {
    // Forward binary frames directly
    if (isBinary) {
      if (!sessionId) return;
      const session = sessions.get(sessionId);
      if (!session) return;
      resetSessionTimeout(sessionId);

      if (role === 'host' && session.viewer?.readyState === 1) {
        session.viewer.send(raw, { binary: true });
      } else if (role === 'viewer' && session.host?.readyState === 1) {
        session.host.send(raw, { binary: true });
      }
      return;
    }

    let msg;
    try {
      msg = JSON.parse(raw.toString());
    } catch {
      sendJson(ws, { type: 'error', code: 'invalid_json', message: 'Invalid JSON' });
      return;
    }

    if (!msg.type) {
      sendJson(ws, { type: 'error', code: 'missing_type', message: 'Missing type field' });
      return;
    }

    // Host registration
    if (msg.type === 'host_register') {
      const hostId = msg.host_id;

      if (!hostId || !/^\d{6}$/.test(hostId)) {
        sendJson(ws, { type: 'error', code: 'invalid_host_id', message: 'Missing or invalid host_id (6 digits required)' });
        ws.close(1008, 'invalid_host_id');
        return;
      }

      if (sessions.size >= MAX_SESSIONS) {
        sendJson(ws, { type: 'error', code: 'server_full', message: 'Max sessions reached' });
        ws.close(1013, 'server_full');
        return;
      }

      // Ak uz existuje aktivna session s tymto host_id, odpoj staru
      if (sessions.has(hostId)) {
        const oldSession = sessions.get(hostId);
        if (oldSession.host?.readyState === 1) {
          oldSession.host.close(1000, 'replaced');
        }
        if (oldSession.viewer?.readyState === 1) {
          sendJson(oldSession.viewer, { type: 'peer_disconnected' });
          oldSession.viewer.close(1000, 'host_replaced');
        }
        cleanupSession(hostId);
      }

      // Registruj zariadenie do persistent registry
      const device = registerDevice(hostId, ip);

      // Pouzij existujuce heslo alebo vygeneruj nove (perzistentne)
      const password = getOrCreatePassword(hostId);

      sessions.set(hostId, {
        host: ws,
        viewer: null,
        password,
        hostScreenInfo: null,
        timeout: null,
      });

      role = 'host';
      sessionId = hostId;

      resetSessionTimeout(hostId);
      sendJson(ws, { type: 'session_created', session_id: hostId, password });
      log(`Host registered: ${hostId} (device: ${device.name || 'unnamed'}, IP: ${ip})`);
      return;
    }

    // Viewer connection
    if (msg.type === 'viewer_connect') {
      const sid = msg.session_id;
      const pwd = msg.password;

      const session = sessions.get(sid);
      if (!session) {
        if (!checkFailedAttempts(ip)) {
          sendJson(ws, { type: 'error', code: 'rate_limited', message: 'Too many failed attempts' });
          ws.close(1008, 'rate_limited');
          return;
        }
        sendJson(ws, { type: 'error', code: 'invalid_session', message: 'Session not found' });
        return;
      }

      if (session.password !== pwd) {
        if (!checkFailedAttempts(ip)) {
          sendJson(ws, { type: 'error', code: 'rate_limited', message: 'Too many failed attempts' });
          ws.close(1008, 'rate_limited');
          return;
        }
        sendJson(ws, { type: 'error', code: 'wrong_password', message: 'Wrong password' });
        return;
      }

      if (session.viewer) {
        sendJson(ws, { type: 'error', code: 'session_busy', message: 'Viewer already connected' });
        return;
      }

      session.viewer = ws;
      role = 'viewer';
      sessionId = sid;

      resetSessionTimeout(sid);

      sendJson(ws, {
        type: 'connect_success',
        host_screen: session.hostScreenInfo || { width: 0, height: 0 },
      });

      sendJson(session.host, { type: 'viewer_joined' });
      log(`Viewer connected to session ${sid}`);
      return;
    }

    // Host screen info (sent after registration)
    if (msg.type === 'host_screen_info' && role === 'host' && sessionId) {
      const session = sessions.get(sessionId);
      if (session) {
        session.hostScreenInfo = { width: msg.width, height: msg.height };
      }
      return;
    }

    // Ping/Pong
    if (msg.type === 'ping') {
      sendJson(ws, { type: 'pong', timestamp: msg.timestamp });
      return;
    }

    if (!sessionId) return;
    const session = sessions.get(sessionId);
    if (!session) return;

    resetSessionTimeout(sessionId);

    // Forward host -> viewer
    if (role === 'host' && HOST_TO_VIEWER.has(msg.type)) {
      if (session.viewer?.readyState === 1) {
        session.viewer.send(raw.toString());
      }
      return;
    }

    // Forward viewer -> host
    if (role === 'viewer' && VIEWER_TO_HOST.has(msg.type)) {
      log(`[DEBUG] viewer->host: ${msg.type}`);
      if (session.host?.readyState === 1) {
        session.host.send(raw.toString());
      }
      return;
    }
  });

  ws.on('close', () => {
    log(`Connection closed: ${role || 'unknown'} (session ${sessionId || 'none'})`);

    if (!sessionId) return;
    const session = sessions.get(sessionId);
    if (!session) return;

    if (role === 'host') {
      if (session.viewer?.readyState === 1) {
        sendJson(session.viewer, { type: 'peer_disconnected' });
      }
      cleanupSession(sessionId);
    } else if (role === 'viewer') {
      session.viewer = null;
      if (session.host?.readyState === 1) {
        sendJson(session.host, { type: 'peer_disconnected' });
      }
      resetSessionTimeout(sessionId);
    }
  });

  ws.on('error', (err) => {
    log(`WebSocket error: ${err.message}`);
  });
});

// Periodic cleanup of stale rate limit records
setInterval(() => {
  const now = Date.now();
  for (const [ip, record] of ipConnections) {
    if (now > record.resetAt) ipConnections.delete(ip);
  }
  for (const [ip, record] of ipFailedAttempts) {
    if (now > record.resetAt) ipFailedAttempts.delete(ip);
  }
}, 60000);

// Graceful shutdown
process.on('SIGINT', () => {
  log('Shutting down...');
  wss.clients.forEach(client => client.close(1001, 'server_shutdown'));
  wss.close(() => {
    log('Server stopped');
    process.exit(0);
  });
});
