"use strict";

// src/main/preload.ts
var import_electron = require("electron");
import_electron.contextBridge.exposeInMainWorld("electronAPI", {
  selectFiles: () => import_electron.ipcRenderer.invoke("select-files"),
  selectDirectory: () => import_electron.ipcRenderer.invoke("select-directory"),
  convertFile: (filePath, sourceFormat, targetFormat) => import_electron.ipcRenderer.invoke("convert-file", filePath, sourceFormat, targetFormat),
  onConversionProgress: (callback) => import_electron.ipcRenderer.on("conversion-progress", (_event, progress) => callback(progress))
});
