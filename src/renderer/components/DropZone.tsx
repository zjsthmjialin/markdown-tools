import { useCallback, useState } from 'react'

interface DropZoneProps {
  onFilesSelected: (files: File[]) => void
}

export default function DropZone({ onFilesSelected }: DropZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    const files = Array.from(e.dataTransfer.files)
    onFilesSelected(files)
  }, [onFilesSelected])

  const handleClick = useCallback(() => {
    const input = document.createElement('input')
    input.type = 'file'
    input.multiple = true
    input.accept = '.pdf,.docx,.xlsx,.pptx,.html,.txt,.md'
    input.onchange = (e) => {
      const files = Array.from((e.target as HTMLInputElement).files || [])
      onFilesSelected(files)
    }
    input.click()
  }, [onFilesSelected])

  return (
    <div
      className={`drop-zone ${isDragOver ? 'dragover' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <div className="drop-zone-content">
        <div className="drop-icon">📁</div>
        <div className="drop-title">拖放文件到此处</div>
        <div className="drop-subtitle">
          或<span>点击选择文件</span> · 支持批量选择
        </div>
      </div>
    </div>
  )
}