import { FileItem } from '../types'

interface FileListProps {
  files: FileItem[]
  onRemove: (id: string) => void
}

const FILE_ICONS: Record<string, string> = {
  '.pdf': '📕',
  '.docx': '📗',
  '.doc': '📗',
  '.xlsx': '📘',
  '.xls': '📘',
  '.pptx': '📙',
  '.ppt': '📙',
  '.html': '🌐',
  '.txt': '📝',
  '.md': '📋'
}

const STATUS_TEXT = {
  pending: '等待中',
  processing: '转换中',
  completed: '已完成',
  error: '错误'
}

export default function FileList({ files, onRemove }: FileListProps) {
  if (files.length === 0) return null

  return (
    <div className="file-list">
      <div className="file-list-header">
        <span className="file-list-title">待转换文件</span>
        <span className="file-count">{files.length} 个文件</span>
      </div>
      <div className="file-items">
        {files.map(file => (
          <div key={file.id} className="file-item">
            <div className="file-icon">
              {FILE_ICONS[file.extension] || '📄'}
            </div>
            <div className="file-info">
              <div className="file-name">{file.name}</div>
              <div className="file-meta">
                {formatSize(file.size)} · {getFormatName(file.extension)}
              </div>
            </div>
            <div className="file-status">
              <span className={`status-dot ${file.status}`}></span>
              {STATUS_TEXT[file.status]}
            </div>
            <button
              className="file-remove"
              onClick={() => onRemove(file.id)}
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function getFormatName(ext: string): string {
  const names: Record<string, string> = {
    '.pdf': 'PDF 文档',
    '.docx': 'Word 文档',
    '.doc': 'Word 文档',
    '.xlsx': 'Excel 表格',
    '.xls': 'Excel 表格',
    '.pptx': 'PowerPoint',
    '.ppt': 'PowerPoint',
    '.html': 'HTML 网页',
    '.txt': '纯文本',
    '.md': 'Markdown'
  }
  return names[ext] || ext
}