import { contextBridge, ipcRenderer, webUtils } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  selectFiles: () => ipcRenderer.invoke('select-files'),
  selectDirectory: () => ipcRenderer.invoke('select-directory'),
  convertFile: (filePath: string, sourceFormat: string, targetFormat: string, outputDir?: string) =>
    ipcRenderer.invoke('convert-file', filePath, sourceFormat, targetFormat, outputDir),
  getPathForFile: (file: File) => webUtils.getPathForFile(file)
})
