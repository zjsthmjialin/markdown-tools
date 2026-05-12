import { useState, useCallback } from 'react'
import './App.css'
import Header from './components/Header'
import DirectionSelect from './components/DirectionSelect'
import DropZone from './components/DropZone'
import FileList from './components/FileList'
import ActionBar from './components/ActionBar'
import ProgressBar from './components/ProgressBar'
import Tip from './components/Tip'
import { FileItem } from './types'

function App() {
  const [files, setFiles] = useState<FileItem[]>([])
  const [sourceFormat, setSourceFormat] = useState('auto')
  const [targetFormat, setTargetFormat] = useState('md')
  const [outputPath, setOutputPath] = useState(
    'C:\\Users\\' + (process.env.USERNAME || 'User') + '\\Documents\\MarkAny'
  )
  const [progress, setProgress] = useState(0)
  const [currentFile, setCurrentFile] = useState('')
  const [isConverting, setIsConverting] = useState(false)

  const handleFilesSelected = useCallback((newFiles: File[]) => {
    const fileItems: FileItem[] = newFiles.map((f, i) => ({
      id: `${Date.now()}-${i}`,
      name: f.name,
      size: f.size,
      extension: '.' + f.name.split('.').pop()?.toLowerCase(),
      status: 'pending' as const
    }))
    setFiles(prev => [...prev, ...fileItems])
  }, [])

  const handleRemoveFile = useCallback((id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id))
  }, [])

  const handleBrowse = useCallback(async () => {
    // 在 Electron 环境中调用 API
    if (window.electronAPI?.selectDirectory) {
      const selected = await window.electronAPI.selectDirectory()
      if (selected) {
        setOutputPath(selected)
      }
    } else {
      // 模拟选择目录
      alert('目录选择功能需要在 Electron 环境中使用')
    }
  }, [])

  const handleConvert = useCallback(async () => {
    if (files.length === 0) return

    setIsConverting(true)
    setFiles(prev => prev.map(f => ({ ...f, status: 'processing' as const, progress: 0 })))

    const totalFiles = files.length
    let completed = 0

    for (const file of files) {
      setCurrentFile(file.name)

      // 模拟转换进度
      for (let i = 0; i <= 100; i += 20) {
        setProgress(Math.round(((completed * 100 + i) / totalFiles)))
        await new Promise(resolve => setTimeout(resolve, 200))
      }

      // 在 Electron 环境中调用实际转换 API
      if (window.electronAPI?.convertFile) {
        try {
          const result = await window.electronAPI.convertFile(
            file.name,
            sourceFormat,
            targetFormat
          )
          setFiles(prev => prev.map(f =>
            f.id === file.id ? { ...f, status: result.success ? 'completed' : 'error', progress: 100 } : f
          ))
        } catch {
          setFiles(prev => prev.map(f =>
            f.id === file.id ? { ...f, status: 'error', progress: 100 } : f
          ))
        }
      } else {
        // 模拟成功
        setFiles(prev => prev.map(f =>
          f.id === file.id ? { ...f, status: 'completed', progress: 100 } : f
        ))
      }

      completed++
    }

    setProgress(100)
    setCurrentFile('')
    setIsConverting(false)
  }, [files, sourceFormat, targetFormat])

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
        <ProgressBar progress={progress} currentFile={currentFile} />
        <ActionBar
          outputPath={outputPath}
          onBrowse={handleBrowse}
          onConvert={handleConvert}
          disabled={files.length === 0 || isConverting}
        />
        <Tip />
      </div>
    </div>
  )
}

export default App