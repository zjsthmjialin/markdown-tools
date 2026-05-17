export interface FileItem {
  id: string
  name: string
  path: string
  size: number
  extension: string
  status: 'pending' | 'processing' | 'completed' | 'error'
  error?: string
}

declare global {
  interface Window {
    electronAPI: {
      selectDirectory: () => Promise<string | null>
      convertFile: (
        filePath: string,
        sourceFormat: string,
        targetFormat: string,
        outputDir?: string
      ) => Promise<{ success: boolean; outputPath?: string; error?: string }>
    }
  }
}