import { app, BrowserWindow } from 'electron'
import path from 'path'

const win = new BrowserWindow({
  width: 900,
  height: 700,
  minWidth: 700,
  minHeight: 500,
  webPreferences: { preload: path.join(__dirname, 'preload.js') }
})

app.whenReady().then(() => {
  win.loadURL('http://localhost:5173')
  win.webContents.openDevTools()
})
