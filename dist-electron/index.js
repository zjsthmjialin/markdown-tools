"use strict";
const electron = require("electron");
const path = require("path");
const win = new electron.BrowserWindow({
  width: 900,
  height: 700,
  minWidth: 700,
  minHeight: 500,
  webPreferences: { preload: path.join(__dirname, "preload.js") }
});
electron.app.whenReady().then(() => {
  win.loadURL("http://localhost:5173");
  win.webContents.openDevTools();
});
