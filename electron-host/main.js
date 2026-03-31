const { app, BrowserWindow, desktopCapturer, screen } = require('electron');
const { WebSocketServer } = require('ws');
const http = require('http');
const fs = require('fs');
const path = require('path');
const robot = require('robotjs');

// Config
const PORT = 7417;
const CAPTURE_FPS = 15;
const JPEG_QUALITY = 40;

let mainWindow;
let httpServer;
let wss;
let captureInterval;

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

function handleInput(data) {
  try {
    const events = JSON.parse(data);
    for (const event of events) {
      const type = event[0];
      if (type === 0) {
        robot.moveMouse(event[1], event[2]);
      } else if (type === 1) {
        const btn = ['left', 'middle', 'right'][event[3]] || 'left';
        robot.moveMouse(event[1], event[2]);
        robot.mouseToggle('down', btn);
      } else if (type === 2) {
        const btn = ['left', 'middle', 'right'][event[3]] || 'left';
        robot.moveMouse(event[1], event[2]);
        robot.mouseToggle('up', btn);
      } else if (type === 3) {
        robot.moveMouse(event[1], event[2]);
        robot.scrollMouse(0, event[3]);
      } else if (type === 4) {
        robot.keyToggle(event[1], 'down');
      } else if (type === 5) {
        robot.keyToggle(event[1], 'up');
      }
    }
  } catch (e) {
    console.error('Input error:', e.message);
  }
}

function startServer() {
  // HTTP server — servuje viewer stranku
  httpServer = http.createServer((req, res) => {
    if (req.url === '/' || req.url === '/index.html') {
      const viewerPath = path.join(__dirname, '..', 'httprd', 'index.html');
      if (fs.existsSync(viewerPath)) {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(fs.readFileSync(viewerPath));
      } else {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end('<h1>Wander Remote Host</h1><p>Viewer HTML not found</p>');
      }
    } else {
      res.writeHead(404);
      res.end('Not found');
    }
  });

  // WebSocket server na rovnakom porte
  wss = new WebSocketServer({ noServer: true });

  httpServer.on('upgrade', (req, socket, head) => {
    wss.handleUpgrade(req, socket, head, (ws) => {
      wss.emit('connection', ws, req);
    });
  });

  wss.on('connection', (ws, req) => {
    const urlPath = req.url || '';
    console.log(`WS connection: ${urlPath}`);

    // View WebSocket — posiela framy
    if (urlPath.includes('connect_view_ws')) {
      updateStatus('Viewer pripojeny!');
      handleViewConnection(ws);
    }
    // Input WebSocket — prijima myš/klavesnicu
    else if (urlPath.includes('connect_input_ws')) {
      handleInputConnection(ws);
    }
    // Fallback — httprd style (combined)
    else {
      updateStatus('Viewer pripojeny!');
      handleCombinedConnection(ws);
    }
  });

  httpServer.listen(PORT, () => {
    console.log(`Server on http://0.0.0.0:${PORT}`);
    updateStatus('Cakam na pripojenie...');
  });
}

function handleViewConnection(ws) {
  const screenSize = getScreenSize();
  let lastFrame = null;

  ws.on('message', async (raw) => {
    const data = Buffer.isBuffer(raw) ? raw : Buffer.from(raw);
    if (data.length === 0) return;
    const packetType = data[0];

    // Frame request (0x01)
    if (packetType === 0x01) {
      try {
        const frame = await captureScreen();
        if (frame && ws.readyState === 1) {
          const header = Buffer.alloc(6);
          header[0] = 0x02;
          header.writeUInt16LE(screenSize.width, 1);
          header.writeUInt16LE(screenSize.height, 3);
          header[5] = 0x01; // full frame
          ws.send(Buffer.concat([header, frame]));
        }
      } catch (e) {
        console.error('Capture error:', e.message);
      }
    }
  });

  ws.on('close', () => {
    console.log('View disconnected');
    updateStatus('Viewer odpojeny');
  });
}

function handleInputConnection(ws) {
  ws.on('message', (raw) => {
    const data = Buffer.isBuffer(raw) ? raw : Buffer.from(raw);
    if (data.length > 1 && data[0] === 0x03) {
      const payload = data.slice(1).toString('ascii');
      handleInput(payload);
    }
  });

  ws.on('close', () => {
    console.log('Input disconnected');
  });
}

function handleCombinedConnection(ws) {
  handleViewConnection(ws);
  handleInputConnection(ws);
}

function updateStatus(text) {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('status', text);
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 400,
    height: 300,
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
  startServer();
});

app.on('window-all-closed', () => {
  if (httpServer) httpServer.close();
  app.quit();
});
