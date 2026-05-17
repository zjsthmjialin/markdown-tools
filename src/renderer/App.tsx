import { useState, useCallback, useRef } from 'react'
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
  const [outputPath, setOutputPath] = useState('')
  const [progress, setProgress] = useState(0)
  const [currentFile, setCurrentFile] = useState('')
  const [isConverting, setIsConverting] = useState(false)
  const [elapsedTime, setElapsedTime] = useState(0)
  const convertingRef = useRef(false)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const handleFilesSelected = useCallback((newFiles: File[]) => {
    const fileItems: FileItem[] = newFiles.map((f, i) => ({
      id: `${Date.now()}-${i}`,
      name: f.name,
      path: (f as any).path || f.name,
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
    if (window.electronAPI?.selectDirectory) {
      const selected = await window.electronAPI.selectDirectory()
      if (selected) {
        setOutputPath(selected)
      }
    } else {
      alert('目录选择功能需要在 Electron 环境中使用')
    }
  }, [])

  const handleConvert = useCallback(async () => {
    if (convertingRef.current) return
    convertingRef.current = true
    setIsConverting(true)
    setProgress(0)
    setElapsedTime(0)
    const startTime = Date.now()
    timerRef.current = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime) / 1000))
    }, 1000)

    // Capture current files synchronously to avoid stale closure
    const currentFiles = files.map(f => ({ ...f, status: 'processing' as const }))
    setFiles(currentFiles)

    if (currentFiles.length === 0) {
      setIsConverting(false)
      convertingRef.current = false
      if (timerRef.current) clearInterval(timerRef.current)
      return
    }

    const totalFiles = currentFiles.length

    for (let i = 0; i < currentFiles.length; i++) {
      const file = currentFiles[i]
      setCurrentFile(file.name)
      setProgress(Math.round((i / totalFiles) * 100))

      if (window.electronAPI?.convertFile) {
        try {
          const result = await window.electronAPI.convertFile(
            file.path,
            sourceFormat,
            targetFormat,
            outputPath
          )
          setFiles(prev => prev.map(f =>
            f.id === file.id ? { ...f, status: result.success ? 'completed' : 'error', error: result.error } : f
          ))
        } catch (e) {
          setFiles(prev => prev.map(f =>
            f.id === file.id ? { ...f, status: 'error', error: String(e) } : f
          ))
        }
      }
    }

    setProgress(100)
    setCurrentFile('')
    setIsConverting(false)
    convertingRef.current = false
    if (timerRef.current) clearInterval(timerRef.current)
    setElapsedTime(Math.floor((Date.now() - startTime) / 1000))
  }, [files, sourceFormat, targetFormat, outputPath])

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
        <ProgressBar progress={progress} currentFile={currentFile} elapsedTime={elapsedTime} />
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