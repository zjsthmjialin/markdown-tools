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

  const handleBrowse = () => {
    // TODO: 调用 electron API 选择目录
    console.log('Browse for directory')
  }

  const handleConvert = () => {
    console.log('Start conversion')
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