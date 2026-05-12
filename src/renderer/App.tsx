import { useState } from 'react'
import './App.css'
import DropZone from './components/DropZone'
import FileList from './components/FileList'
import { FileItem } from './types'

function App() {
  const [files, setFiles] = useState<FileItem[]>([])

  const handleFilesSelected = (newFiles: File[]) => {
    const fileItems: FileItem[] = newFiles.map((f, i) => ({
      id: `${Date.now()}-${i}`,
      name: f.name,
      size: f.size,
      extension: '.' + f.name.split('.').pop()?.toLowerCase(),
      status: 'pending'
    }))
    setFiles(prev => [...prev, ...fileItems])
  }

  const handleRemoveFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id))
  }

  return (
    <div className="app-container">
      <DropZone onFilesSelected={handleFilesSelected} />
      <FileList files={files} onRemove={handleRemoveFile} />
    </div>
  )
}

export default App