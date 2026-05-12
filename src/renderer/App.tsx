import { useState } from 'react'
import './App.css'
import Header from './components/Header'
import DirectionSelect from './components/DirectionSelect'
import DropZone from './components/DropZone'
import FileList from './components/FileList'
import ActionBar from './components/ActionBar'
import ProgressBar from './components/ProgressBar'
import { FileItem } from './types'

function App() {
  const [files, setFiles] = useState<FileItem[]>([])
  const [sourceFormat, setSourceFormat] = useState('auto')
  const [targetFormat, setTargetFormat] = useState('md')
  const [outputPath, setOutputPath] = useState(
    'C:\\Users\\' + (process.env.USERNAME || 'User') + '\\Documents\\MarkAny'
  )

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

  const handleBrowse = async () => {
    const selected = await window.electronAPI.selectDirectory()
    if (selected) {
      setOutputPath(selected)
    }
  }

  const handleConvert = async () => {
    setFiles(prev => prev.map(f => ({ ...f, status: 'processing' as const, progress: 0 })))

    for (const file of files) {
      try {
        const result = await window.electronAPI.convertFile(
          file.name,
          sourceFormat,
          targetFormat
        )

        if (result.success) {
          setFiles(prev => prev.map(f =>
            f.id === file.id ? { ...f, status: 'completed' as const, outputPath: result.outputPath } : f
          ))
        } else {
          setFiles(prev => prev.map(f =>
            f.id === file.id ? { ...f, status: 'error' as const } : f
          ))
        }
      } catch (error) {
        setFiles(prev => prev.map(f =>
          f.id === file.id ? { ...f, status: 'error' as const } : f
        ))
      }
    }
  }

  return (
    <div className="app-container">
      <Header />
      <div className="main-card">
        <DirectionSelect
          sourceFormat={sourceFormat}
          targetFormat={targetFormat}
          onSourceChange={setSourceFormat}
          onTargetChange={setTargetFormat}
        />
        <DropZone onFilesSelected={handleFilesSelected} />
        <FileList files={files} onRemove={handleRemoveFile} />
        <ProgressBar progress={0} />
        <ActionBar
          outputPath={outputPath}
          onBrowse={handleBrowse}
          onConvert={handleConvert}
          disabled={files.length === 0}
        />
      </div>
    </div>
  )
}

export default App