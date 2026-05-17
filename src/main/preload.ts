import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  selectDirectory: () => ipcRenderer.invoke('select-directory'),
  convertFile: (filePath: string, sourceFormat: string, targetFormat: string, outputDir?: string) =>
    ipcRenderer.invoke('convert-file', filePath, sourceFormat, targetFormat, outputDir)
})