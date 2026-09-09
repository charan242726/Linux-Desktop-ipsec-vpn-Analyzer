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

// Auto-launch backend.exe with admin privileges (Dev Only)
function launchBackend() {
  if (app.isPackaged) {
    // In production, the backend is a Windows Service running as SYSTEM
    // We don't need to launch it here!
    return;
  }

  // Development: spawn python directly
  const repoRoot = path.join(__dirname, '..', '..');
  const exePath = path.join(repoRoot, 'backend', 'venv', 'Scripts', 'python.exe');
  const mainScript = path.join(repoRoot, 'backend', 'api', 'main.py');
  
  backendProcess = spawn(exePath, [mainScript], { detached: false });
  backendProcess.on('error', (err) => console.error('Backend error:', err));
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
