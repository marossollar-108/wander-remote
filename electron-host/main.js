const { app, BrowserWindow, Tray, Menu, nativeImage, desktopCapturer, screen, systemPreferences, dialog, shell } = require('electron');
const { autoUpdater } = require('electron-updater');
const WebSocket = require('ws');
const robot = require('robotjs');
const path = require('path');
const os = require('os');
const fs = require('fs');
const crypto = require('crypto');

// Config
const RELAY_URL = process.env.RELAY_URL || 'ws://142.93.169.75:8765';
const CAPTURE_FPS = 15;
const JPEG_QUALITY = 40;

let mainWindow;
let tray = null;
let isQuitting = false;
let ws;
let hostId = null;
let sessionId = null;
let password = null;
let viewerConnected = false;
let captureInterval = null;
let reconnectTimeout = null;

// --- Host ID (persistent, z MAC adresy) ---

function getMacAddress() {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      // Preskoc loopback a internal
      if (!iface.internal && iface.mac && iface.mac !== '00:00:00:00:00:00') {
        return iface.mac;
      }
    }
  }
  return '00:00:00:00:00:00';
}

function generateHostIdFromMac(mac) {
  const hash = crypto.createHash('sha256').update(mac).digest();
  const num = hash.readUInt32BE(0);
  return String(100000 + (num % 900000));
}

function getOrCreateHostId() {
  const hostIdDir = path.join(os.homedir(), '.wander-remote');
  const hostIdFile = path.join(hostIdDir, 'host_id');

  try {
    const existing = fs.readFileSync(hostIdFile, 'utf-8').trim();
    if (existing) return existing;
  } catch {
    // subor neexistuje, vytvorime
  }

  const mac = getMacAddress();
  const id = generateHostIdFromMac(mac);

  fs.mkdirSync(hostIdDir, { recursive: true });
  fs.writeFileSync(hostIdFile, id, 'utf-8');
  return id;
}

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
    console.log(`Host ID: ${hostId}`);
    ws.send(JSON.stringify({ type: 'host_register', host_id: hostId }));
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

function createTray() {
  // Vytvor 16x16 tray ikonu programaticky (cerveny kruh - "W")
  const size = 16;
  const canvas = Buffer.alloc(size * size * 4); // RGBA
  const cx = 7.5, cy = 7.5, r = 7;
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const idx = (y * size + x) * 4;
      const dist = Math.sqrt((x - cx) ** 2 + (y - cy) ** 2);
      if (dist <= r) {
        canvas[idx] = 0xEB;     // R
        canvas[idx + 1] = 0x00; // G
        canvas[idx + 2] = 0x2F; // B
        canvas[idx + 3] = 0xFF; // A
      }
    }
  }
  const icon = nativeImage.createFromBuffer(canvas, { width: size, height: size });
  if (process.platform === 'darwin') icon.setTemplateImage(false);

  tray = new Tray(icon);
  tray.setToolTip('Wander Remote Host');

  function updateTrayMenu() {
    const statusText = viewerConnected ? 'Viewer pripojeny' : 'Cakam na viewer...';
    const idText = sessionId ? `ID: ${sessionId}` : 'Nepripojeny';

    const contextMenu = Menu.buildFromTemplate([
      { label: 'Wander Remote Host', enabled: false },
      { type: 'separator' },
      { label: idText, enabled: false },
      { label: statusText, enabled: false },
      { type: 'separator' },
      {
        label: 'Zobrazit okno',
        click: () => {
          if (mainWindow) {
            mainWindow.show();
            mainWindow.focus();
          }
        },
      },
      {
        label: 'Skryt do pozadia',
        click: () => {
          if (mainWindow) mainWindow.hide();
        },
      },
      { type: 'separator' },
      {
        label: 'Ukoncit',
        click: () => {
          isQuitting = true;
          app.quit();
        },
      },
    ]);
    tray.setContextMenu(contextMenu);
  }

  // Klik na tray ikonu = zobraz/skry okno
  tray.on('click', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
        mainWindow.focus();
      }
    }
  });

  // Aktualizuj tray menu raz za 2 sekundy (pre status)
  setInterval(updateTrayMenu, 2000);
  updateTrayMenu();
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

  // Zatvorenie okna = skrytie do tray, nie ukoncenie
  mainWindow.on('close', (e) => {
    if (!isQuitting) {
      e.preventDefault();
      mainWindow.hide();
    }
  });
}

// --- Kontrola macOS povoleni ---

async function checkPermissions() {
  if (process.platform !== 'darwin') return;

  // 1. Accessibility - potrebne pre robotjs (mouse/keyboard)
  const accessibilityOk = systemPreferences.isTrustedAccessibilityClient(false);
  if (!accessibilityOk) {
    const { response } = await dialog.showMessageBox({
      type: 'warning',
      title: 'Povolenie potrebne',
      message: 'Wander Remote Host potrebuje povolenie na Accessibility (ovladanie mysi a klavesnice).',
      detail: 'Kliknite "Otvorit nastavenia" a pridajte Wander Remote Host do zoznamu povolenych aplikacii.\n\nPo povoleni restartujte aplikaciu.',
      buttons: ['Otvorit nastavenia', 'Pokracovat bez povolenia'],
      defaultId: 0,
    });
    if (response === 0) {
      // Toto otvori System Settings na spravnu stranku A zaroven zobrazi systemovy prompt
      systemPreferences.isTrustedAccessibilityClient(true);
      shell.openExternal('x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility');
    }
  }

  // 2. Screen Recording - potrebne pre desktopCapturer
  const screenOk = systemPreferences.getMediaAccessStatus('screen');
  if (screenOk !== 'granted') {
    // Skusime capture aby macOS zaregistrovalo pokus o pristup
    try {
      await desktopCapturer.getSources({ types: ['screen'], thumbnailSize: { width: 1, height: 1 } });
    } catch (e) {
      console.log('Screen capture trigger:', e.message);
    }

    const screenOkAfter = systemPreferences.getMediaAccessStatus('screen');
    if (screenOkAfter !== 'granted') {
      const { response } = await dialog.showMessageBox({
        type: 'warning',
        title: 'Povolenie potrebne',
        message: 'Wander Remote Host potrebuje povolenie na nahravanie obrazovky.',
        detail: 'Postup:\n1. Kliknite "Otvorit nastavenia"\n2. Otvorte: Sukromie a bezpecnost > Nahravanie obrazovky\n3. Kliknite "+" dole a pridajte Wander Remote Host z Applications\n4. Zapnite prepinac\n5. Restartujte aplikaciu',
        buttons: ['Otvorit nastavenia', 'Pokracovat bez povolenia'],
        defaultId: 0,
      });
      if (response === 0) {
        // Otvorime priamo sekciu Privacy & Security
        shell.openExternal('x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenRecording');
      }
    }
  }
}

// --- Auto-updater ---

function setupAutoUpdater() {
  autoUpdater.autoDownload = false;
  autoUpdater.autoInstallOnAppQuit = true;

  autoUpdater.on('update-available', async (info) => {
    console.log('Update available:', info.version);
    const { response } = await dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Dostupna aktualizacia',
      message: `Je dostupna nova verzia ${info.version}.`,
      detail: 'Chcete ju stiahnut a nainstalovat?',
      buttons: ['Aktualizovat', 'Neskor'],
      defaultId: 0,
    });
    if (response === 0) {
      updateStatus('Stahujem aktualizaciu...');
      autoUpdater.downloadUpdate();
    }
  });

  autoUpdater.on('update-not-available', () => {
    console.log('App is up to date');
  });

  autoUpdater.on('download-progress', (progress) => {
    updateStatus(`Stahujem aktualizaciu: ${Math.round(progress.percent)}%`);
  });

  autoUpdater.on('update-downloaded', async () => {
    const { response } = await dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Aktualizacia pripravena',
      message: 'Aktualizacia bola stiahnutá. Aplikacia sa reštartuje.',
      buttons: ['Restartovat teraz', 'Neskor'],
      defaultId: 0,
    });
    if (response === 0) {
      autoUpdater.quitAndInstall();
    }
  });

  autoUpdater.on('error', (err) => {
    console.error('Auto-updater error:', err.message);
  });

  // Skontroluj aktualizacie
  autoUpdater.checkForUpdates().catch((err) => {
    console.log('Update check skipped:', err.message);
  });
}

app.whenReady().then(async () => {
  hostId = getOrCreateHostId();
  console.log(`Persistent Host ID: ${hostId}`);
  createTray();
  createWindow();
  await checkPermissions();
  setupAutoUpdater();
  connect();
});

// Na macOS - skry dock ikonu ked je okno skryte (volitelne)
app.on('activate', () => {
  if (mainWindow) {
    mainWindow.show();
    mainWindow.focus();
  }
});

// Neskoncuj app ked sa zatvoria okna - bezi na pozadi v tray
app.on('window-all-closed', () => {
  // Nic - app bezi dalej v tray
});

app.on('before-quit', () => {
  isQuitting = true;
  if (ws) ws.close();
  if (reconnectTimeout) clearTimeout(reconnectTimeout);
});
