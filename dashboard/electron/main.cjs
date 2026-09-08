const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const sudo = require('sudo-prompt');

let mainWindow;
const isDev = process.env.NODE_ENV === 'development';

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    frame: false, // Frameless window for immersive app feel
    transparent: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      nodeIntegration: false,
      contextIsolation: true,
    },
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

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

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

// IPC Handler to start backend with admin privileges
ipcMain.handle('backend:start', async (event) => {
  return new Promise((resolve, reject) => {
    const options = {
      name: 'IPsec VPN Analyzer',
    };
    
    let command;
    
    if (app.isPackaged) {
      // In production, the compiled backend.exe is bundled in resources/backend
      const exePath = path.join(process.resourcesPath, 'backend', process.platform === 'win32' ? 'backend.exe' : 'backend');
      command = `"${exePath}"`;
    } else {
      // In development, use the local virtual environment
      const repoRoot = path.join(__dirname, '..', '..');
      const isWin = process.platform === 'win32';
      const pythonPath = path.join(repoRoot, 'backend', isWin ? 'venv/Scripts/python.exe' : 'venv/bin/python');
      const mainScript = path.join(repoRoot, 'backend', 'api', 'main.py');
      command = `"${pythonPath}" "${mainScript}"`;
    }
    
    sudo.exec(command, options, (error, stdout, stderr) => {
      if (error) {
        console.error('Sudo prompt error:', error);
        reject(error.message);
        return;
      }
      console.log('Backend stdout:', stdout);
      resolve(true);
    });
  });
});
