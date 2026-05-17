import { useCallback, useState } from 'react'
import { SelectedFile } from '../types'

interface DropZoneProps {
  onFilesSelected: (files: File[]) => void
  onFilesSelectedViaDialog: (files: SelectedFile[]) => void
}

export default function DropZone({ onFilesSelected, onFilesSelectedViaDialog }: DropZoneProps) {
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

  const handleClick = useCallback(async () => {
    if (window.electronAPI?.selectFiles) {
      const selectedFiles = await window.electronAPI.selectFiles()
      if (selectedFiles && selectedFiles.length > 0) {
        onFilesSelectedViaDialog(selectedFiles)
      }
    }
  }, [onFilesSelectedViaDialog])

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
