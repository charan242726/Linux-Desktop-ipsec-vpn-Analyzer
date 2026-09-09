const { app, BrowserWindow, ipcMain, Notification } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let backendProcess = null;
const isDev = process.env.NODE_ENV === 'development';

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    frame: false,
    show: false,               // Don't show until ready-to-show fires
    backgroundColor: '#040711', // Match CSS --foundation-bg, prevents white flash
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  // Show only once fully rendered — avoids blank/white frame
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }
}

app.whenReady().then(() => {
  createWindow();
  launchBackend();  // Auto-launch backend on startup

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Kill backend when app quits
app.on('will-quit', () => {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
});

const sudo = require('sudo-prompt');

// Auto-launch backend with admin privileges (Required for Linux scapy packet capture)
function launchBackend() {
  const options = {
    name: 'IPsec VPN Analyzer',
  };
  
  let command;
  if (app.isPackaged) {
    // In production AppImage, launch the bundled backend executable
    const exePath = path.join(process.resourcesPath, 'backend', 'backend');
    command = `"${exePath}"`;
  } else {
    // Development: spawn python using local virtual environment
    const repoRoot = path.join(__dirname, '..', '..');
    const pythonPath = path.join(repoRoot, 'backend', 'venv', 'bin', 'python');
    const mainScript = path.join(repoRoot, 'backend', 'api', 'main.py');
    command = `"${pythonPath}" "${mainScript}"`;
  }
  
  // Use sudo-prompt to elevate privileges so scapy can bind to interfaces
  sudo.exec(command, options, (error, stdout, stderr) => {
    if (error) {
      console.error('Sudo prompt error or backend crashed:', error);
      return;
    }
    console.log('Backend stdout:', stdout);
  });
}

// IPC Handlers for frameless window controls
ipcMain.on('window:minimize', () => mainWindow?.minimize());
ipcMain.on('window:maximize', () => {
  if (mainWindow?.isMaximized()) {
    mainWindow.unmaximize();
  } else {
    mainWindow?.maximize();
  }
});
ipcMain.on('window:close', () => mainWindow?.close());

// IPC Handler to manually restart backend if needed
ipcMain.handle('backend:start', async () => {
  launchBackend();
  return true;
});

// IPC Handler for OS desktop notifications
// The renderer calls window.electronAPI.sendNotification({ title, body, urgency })
ipcMain.on('notify:send', (event, { title, body, urgency }) => {
  if (!Notification.isSupported()) return;
  const n = new Notification({
    title: title || 'VPN Analyzer',
    body: body || '',
    // urgency: 'normal' | 'critical' | 'low'  (Linux only, silently ignored on Windows/macOS)
    urgency: urgency || 'normal',
    silent: urgency === 'low',
  });
  n.on('click', () => {
    // Bring the window to focus when user clicks the notification
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
  n.show();
});
