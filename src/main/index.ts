import { app, BrowserWindow } from 'electron'
import path from 'path'
import { setupIpcHandlers, startPythonService, stopPythonService } from './ipc-handlers'

const win = new BrowserWindow({
  width: 900,
  height: 700,
  minWidth: 700,
  minHeight: 500,
  webPreferences: {
    preload: path.join(__dirname, 'preload.js'),
    contextIsolation: true,
    nodeIntegration: false
  }
})

app.whenReady().then(() => {
  setupIpcHandlers()
  startPythonService()

  if (process.env.NODE_ENV === 'development') {
    win.loadURL('http://localhost:5173')
    win.webContents.openDevTools()
  } else {
    win.loadFile(path.join(__dirname, '../dist/index.html'))
  }
})

app.on('window-all-closed', () => {
  stopPythonService()
  app.quit()
})