export interface FileItem {
  id: string
  name: string
  path: string
  size: number
  extension: string
  status: 'pending' | 'processing' | 'completed' | 'error'
  error?: string
}

export interface SelectedFile {
  name: string
  path: string
  size: number
  extension: string
}

declare global {
  interface Window {
    electronAPI: {
      selectFiles: () => Promise<SelectedFile[]>
      selectDirectory: () => Promise<string | null>
      convertFile: (
        filePath: string,
        sourceFormat: string,
        targetFormat: string,
        outputDir?: string
      ) => Promise<{ success: boolean; outputPath?: string; error?: string }>
      getPathForFile: (file: File) => string
      minimize: () => Promise<void>
      maximize: () => Promise<void>
      close: () => Promise<void>
    }
  }
}
