export interface FileItem {
  id: string
  name: string
  size: number
  extension: string
  status: 'pending' | 'processing' | 'completed' | 'error'
  progress?: number
  outputPath?: string
}

declare global {
  interface Window {
    electronAPI: {
      selectFiles: () => Promise<string[]>
      selectDirectory: () => Promise<string | null>
      convertFile: (
        filePath: string,
        sourceFormat: string,
        targetFormat: string
      ) => Promise<{ success: boolean; outputPath?: string; error?: string }>
      onConversionProgress: (callback: (progress: number) => void) => void
      onConversionComplete: (callback: (result: any) => void) => void
    }
  }
}