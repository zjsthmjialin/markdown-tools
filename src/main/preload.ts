import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  selectFiles: () => ipcRenderer.invoke('select-files'),
  selectDirectory: () => ipcRenderer.invoke('select-directory'),
  convertFile: (filePath: string, sourceFormat: string, targetFormat: string) =>
    ipcRenderer.invoke('convert-file', filePath, sourceFormat, targetFormat),
  onConversionProgress: (callback: (progress: number) => void) =>
    ipcRenderer.on('conversion-progress', (_event, progress) => callback(progress)),
  onConversionComplete: (callback: (result: any) => void) =>
    ipcRenderer.on('conversion-complete', (_event, result) => callback(result))
})