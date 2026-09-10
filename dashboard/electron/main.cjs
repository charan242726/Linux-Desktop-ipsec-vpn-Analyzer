const { app, BrowserWindow, ipcMain, Notification, Tray, Menu } = require('electron');
const path = require('path');

let mainWindow;
let tray = null;
const isDev = process.env.NODE_ENV === 'development';

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    frame: false,
    show: false,
    backgroundColor: '#040711',
    icon: path.join(__dirname, isDev ? '../public/vpnguard-logo.png' : '../dist/vpnguard-logo.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  // Prevent app from quitting when window is closed, hide to tray instead
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
    return false;
  });
}

function createTray() {
  // Try to load a generic icon or a built icon
  let iconPath;
  if (isDev) {
    iconPath = path.join(__dirname, '..', 'public', 'vpnguard-logo.png');
  } else {
    iconPath = path.join(__dirname, '..', 'dist', 'vpnguard-logo.png');
  }
  
  // Wrap in try-catch in case icon doesn't exist (Electron handles native empty icons usually)
  try {
    tray = new Tray(iconPath);
  } catch(e) {
    // If no icon file exists, just create an empty tray (on some OSes this still reserves space)
    console.warn("Tray icon not found, using default");
    tray = new Tray(path.join(__dirname, 'preload.cjs')); // Hack to just use a random file for dummy icon
  }
  
  const contextMenu = Menu.buildFromTemplate([
    { label: 'Show Dashboard', click: () => {
      if (mainWindow) {
        mainWindow.show();
        mainWindow.focus();
      }
    }},
    { type: 'separator' },
    { label: 'Quit VPNGUARD', click: () => {
      app.isQuitting = true;
      app.quit();
    }}
  ]);
  
  tray.setToolTip('VPNGUARD Analyzer');
  tray.setContextMenu(contextMenu);

  tray.on('click', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.focus();
      } else {
        mainWindow.show();
        mainWindow.focus();
      }
    }
  });
}

// Fix for Linux AppImage: Set a strict app name so the lock file is consistent
// regardless of the random /tmp/.mount_XXXX path the AppImage runs from.
app.name = 'vpnguard-analyzer';

const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', (event, commandLine, workingDirectory) => {
    // Someone tried to run a second instance, we should focus our window.
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.show();
      mainWindow.focus();
    }
  });

  app.whenReady().then(() => {
    createWindow();
    createTray();
    
    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
      }
    });
  });
}

app.on('before-quit', () => {
  app.isQuitting = true;
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

// We override close to hide the window
ipcMain.on('window:close', () => {
  if (mainWindow) {
    mainWindow.hide();
  }
});

// Expose a method to wake up the UI automatically
ipcMain.on('window:show', () => {
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.show();
    mainWindow.focus();
  }
});

// IPC Handler for OS desktop notifications
ipcMain.on('notify:send', (event, { title, body, urgency }) => {
  if (!Notification.isSupported()) return;
  const n = new Notification({
    title: title || 'VPNGUARD Analyzer',
    body: body || '',
    urgency: urgency || 'normal',
    silent: urgency === 'low',
  });
  n.on('click', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.show();
      mainWindow.focus();
    }
  });
  n.show();
});
