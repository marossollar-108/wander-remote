const { app, BrowserWindow, desktopCapturer, screen } = require('electron');
const WebSocket = require('ws');
const robot = require('robotjs');
const path = require('path');

// Config
const RELAY_URL = process.env.RELAY_URL || 'ws://142.93.169.75:8765';
const CAPTURE_FPS = 15;
const JPEG_QUALITY = 40;

let mainWindow;
let ws;
let sessionId = null;
let password = null;
let viewerConnected = false;
let captureInterval = null;
let reconnectTimeout = null;

function getScreenSize() {
  const display = screen.getPrimaryDisplay();
  return { width: display.size.width, height: display.size.height };
}

async function captureScreen() {
  const sources = await desktopCapturer.getSources({
    types: ['screen'],
    thumbnailSize: getScreenSize(),
  });
  if (sources.length === 0) return null;
  return sources[0].thumbnail.toJPEG(JPEG_QUALITY);
}

// --- Input handling (robotjs) ---

const KEY_MAP = {
  'ctrl': 'control', 'meta': 'command', 'win': 'command',
  'esc': 'escape', 'del': 'delete',
};

function mapKey(key) {
  return KEY_MAP[key] || key;
}

function handleMouseMove(msg) {
  const { width, height } = getScreenSize();
  const x = Math.round(msg.x * width);
  const y = Math.round(msg.y * height);
  robot.moveMouse(x, y);
}

function handleMouseClick(msg) {
  const { width, height } = getScreenSize();
  const x = Math.round(msg.x * width);
  const y = Math.round(msg.y * height);
  const btn = msg.button || 'left';
  const action = msg.action || 'click';

  robot.moveMouse(x, y);

  if (action === 'click') {
    robot.mouseClick(btn);
  } else if (action === 'double' || action === 'dblclick') {
    robot.mouseClick(btn, true);
  } else if (action === 'down') {
    robot.mouseToggle('down', btn);
  } else if (action === 'up') {
    robot.mouseToggle('up', btn);
  }
}

function handleMouseScroll(msg) {
  const { width, height } = getScreenSize();
  const x = Math.round(msg.x * width);
  const y = Math.round(msg.y * height);
  robot.moveMouse(x, y);
  robot.scrollMouse(0, -(msg.delta || 0));
}

function handleKeyEvent(msg) {
  const key = mapKey(msg.key);
  const action = msg.action || 'press';

  try {
    if (action === 'press') {
      robot.keyTap(key);
    } else if (action === 'down') {
      robot.keyToggle(key, 'down');
    } else if (action === 'up') {
      robot.keyToggle(key, 'up');
    }
  } catch (e) {
    console.error(`Key error: ${key}`, e.message);
  }
}

function handleKeyCombo(msg) {
  const keys = (msg.keys || []).map(mapKey);
  if (keys.length === 0) return;
  try {
    // Last key is the main key, rest are modifiers
    const modifiers = keys.slice(0, -1);
    const key = keys[keys.length - 1];
    robot.keyTap(key, modifiers);
  } catch (e) {
    console.error(`Combo error: ${msg.keys}`, e.message);
  }
}

// --- Relay connection ---

function connect() {
  updateStatus('Pripajam sa na relay...');
  console.log(`Connecting to ${RELAY_URL}`);

  ws = new WebSocket(RELAY_URL);

  ws.on('open', () => {
    console.log('Connected to relay');
    ws.send(JSON.stringify({ type: 'host_register' }));
  });

  ws.on('message', (raw, isBinary) => {
    if (isBinary) return;

    let msg;
    try {
      msg = JSON.parse(raw.toString());
    } catch {
      return;
    }

    const type = msg.type;

    if (type === 'session_created') {
      sessionId = msg.session_id;
      password = msg.password;
      console.log(`Session: ${sessionId} | Password: ${password}`);
      updateSession(sessionId, password);
      updateStatus('Cakam na viewer...');

      // Send screen info
      const { width, height } = getScreenSize();
      ws.send(JSON.stringify({
        type: 'host_screen_info',
        width,
        height,
      }));
    }

    else if (type === 'viewer_joined') {
      viewerConnected = true;
      console.log('Viewer connected!');
      updateStatus('Viewer pripojeny!');
      startCapture();
    }

    else if (type === 'peer_disconnected') {
      viewerConnected = false;
      console.log('Viewer disconnected');
      updateStatus('Cakam na viewer...');
      stopCapture();
    }

    else if (type === 'mouse_move') {
      handleMouseMove(msg);
    }
    else if (type === 'mouse_click') {
      handleMouseClick(msg);
    }
    else if (type === 'mouse_scroll') {
      handleMouseScroll(msg);
    }
    else if (type === 'key_event') {
      handleKeyEvent(msg);
    }
    else if (type === 'key_combo') {
      handleKeyCombo(msg);
    }
    else if (type === 'quality_change') {
      // TODO: adjust capture settings
      console.log('Quality change:', msg);
    }
    else if (type === 'ping') {
      ws.send(JSON.stringify({ type: 'pong', timestamp: msg.timestamp }));
    }
  });

  ws.on('close', () => {
    console.log('Disconnected from relay');
    viewerConnected = false;
    stopCapture();
    updateStatus('Odpojeny — reconnect o 3s...');
    reconnectTimeout = setTimeout(connect, 3000);
  });

  ws.on('error', (err) => {
    console.error('WS error:', err.message);
  });
}

// --- Screen capture loop ---

function startCapture() {
  if (captureInterval) return;

  const { width, height } = getScreenSize();
  let busy = false;

  captureInterval = setInterval(async () => {
    if (busy || !viewerConnected || !ws || ws.readyState !== 1) return;
    busy = true;

    try {
      const jpeg = await captureScreen();
      if (jpeg && ws.readyState === 1) {
        const base64 = jpeg.toString('base64');
        ws.send(JSON.stringify({
          type: 'frame_full',
          timestamp: Date.now(),
          width,
          height,
          format: 'jpeg',
          quality: JPEG_QUALITY,
          data: base64,
        }));
      }
    } catch (e) {
      console.error('Capture error:', e.message);
    }

    busy = false;
  }, 1000 / CAPTURE_FPS);
}

function stopCapture() {
  if (captureInterval) {
    clearInterval(captureInterval);
    captureInterval = null;
  }
}

// --- GUI ---

function updateStatus(text) {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('status', text);
  }
}

function updateSession(id, pwd) {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('session', { id, password: pwd });
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 400,
    height: 350,
    resizable: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });
  mainWindow.loadFile('gui.html');
  mainWindow.on('closed', () => { mainWindow = null; });
}

app.whenReady().then(() => {
  createWindow();
  connect();
});

app.on('window-all-closed', () => {
  if (ws) ws.close();
  if (reconnectTimeout) clearTimeout(reconnectTimeout);
  app.quit();
});
