export interface FileItem {
  id: string
  name: string
  size: number
  extension: string
  status: 'pending' | 'processing' | 'completed' | 'error'
  progress?: number
  outputPath?: string
}