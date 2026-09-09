const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  minimize: () => ipcRenderer.send('window:minimize'),
  maximize: () => ipcRenderer.send('window:maximize'),
  close: () => ipcRenderer.send('window:close'),
  startBackend: () => ipcRenderer.invoke('backend:start'),
  wakeUp: () => ipcRenderer.send('window:show'),
  // Fire an OS-level desktop notification
  sendNotification: (opts) => ipcRenderer.send('notify:send', opts),
});
