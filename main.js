const { app, BrowserWindow, shell } = require('electron');
const path = require('path');

const APP_URL = process.env.AUREVIA_APP_URL || 'https://orbiretail-saas.streamlit.app/';

function createWindow() {
  const win = new BrowserWindow({
    width: 1360,
    height: 900,
    minWidth: 1100,
    minHeight: 720,
    title: 'Aurevia 智策云',
    backgroundColor: '#071225',
    show: false,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  win.once('ready-to-show', () => {
    win.show();
  });

  win.loadFile(path.join(__dirname, 'splash.html'));

  setTimeout(() => {
    win.loadURL(APP_URL);
  }, 1600);

  win.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  win.webContents.on('did-fail-load', () => {
    win.loadFile(path.join(__dirname, 'splash.html'));
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
