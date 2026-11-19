import { contextBridge, ipcRenderer, webUtils } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  selectFiles: () => ipcRenderer.invoke('select-files'),
  selectDirectory: () => ipcRenderer.invoke('select-directory'),
  convertFile: (filePath: string, sourceFormat: string, targetFormat: string, outputDir?: string) =>
    ipcRenderer.invoke('convert-file', filePath, sourceFormat, targetFormat, outputDir),
  cancelConversion: () => ipcRenderer.invoke('cancel-conversion'),
  onConversionProgress: (callback: (progress: { file: string; page: number; pageCount: number; phase: string }) => void) => {
    const listener = (_event: Electron.IpcRendererEvent, progress: { file: string; page: number; pageCount: number; phase: string }) => callback(progress)
    ipcRenderer.on('conversion-progress', listener)
    return () => ipcRenderer.removeListener('conversion-progress', listener)
  },
  getPathForFile: (file: File) => webUtils.getPathForFile(file),
  minimize: () => ipcRenderer.invoke('window-minimize'),
  maximize: () => ipcRenderer.invoke('window-maximize'),
  close: () => ipcRenderer.invoke('window-close')
})
