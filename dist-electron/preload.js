"use strict";
const electron = require("electron");
electron.contextBridge.exposeInMainWorld("electronAPI", {
  selectFiles: () => electron.ipcRenderer.invoke("select-files"),
  selectDirectory: () => electron.ipcRenderer.invoke("select-directory"),
  convertFile: (filePath, sourceFormat, targetFormat) => electron.ipcRenderer.invoke("convert-file", filePath, sourceFormat, targetFormat),
  onConversionProgress: (callback) => electron.ipcRenderer.on("conversion-progress", (_event, progress) => callback(progress))
});
