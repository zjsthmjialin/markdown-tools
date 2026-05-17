import { app, BrowserWindow, screen } from 'electron'
import path from 'path'
import { setupIpcHandlers, startPythonService, stopPythonService } from './ipc-handlers'

let win: BrowserWindow | null = null
const isDev = process.env.NODE_ENV === 'development'

app.whenReady().then(async () => {
  const primaryDisplay = screen.getPrimaryDisplay()
  const { width, height } = primaryDisplay.workAreaSize

  win = new BrowserWindow({
    width: 900,
    height: 700,
    minWidth: 700,
    minHeight: 500,
    x: Math.floor((width - 900) / 2),
    y: Math.floor((height - 700) / 2),
    show: false,
    webPreferences: {
      preload: path.join(__dirname, '../preload/preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  })

  setupIpcHandlers()
  await startPythonService()

  if (isDev) {
    win.loadURL('http://localhost:5173')
    win.webContents.openDevTools()
    win.show()
  } else {
    win.loadFile(path.join(__dirname, '../../dist/index.html'))
  }

  win.webContents.on('did-finish-load', () => {
    win?.show()
  })

  win.on('closed', () => {
    win = null
  })
})

app.on('window-all-closed', () => {
  stopPythonService()
  app.quit()
})

app.on('activate', () => {
  if (win === null) {
    app.whenReady()
  }
})
