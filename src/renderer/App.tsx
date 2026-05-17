import { useState, useCallback, useRef, useEffect } from 'react'
import './App.css'
import Header from './components/Header'
import DirectionSelect from './components/DirectionSelect'
import DropZone from './components/DropZone'
import FileList from './components/FileList'
import ActionBar from './components/ActionBar'
import ProgressBar from './components/ProgressBar'
import Tip from './components/Tip'
import { FileItem, SelectedFile } from './types'

function App() {
  const [files, setFiles] = useState<FileItem[]>([])
  const [sourceFormat, setSourceFormat] = useState('auto')
  const [outputPath, setOutputPath] = useState('')
  const [progress, setProgress] = useState(0)
  const [currentFile, setCurrentFile] = useState('')
  const [isConverting, setIsConverting] = useState(false)
  const [elapsedTime, setElapsedTime] = useState(0)
  const convertingRef = useRef(false)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [])

  // Handle files from drag-and-drop (File objects need path resolution)
  const handleFilesSelected = useCallback(async (newFiles: File[]) => {
    const fileItems: FileItem[] = []
    for (let i = 0; i < newFiles.length; i++) {
      const f = newFiles[i]
      let filePath = f.name
      if (window.electronAPI?.getPathForFile) {
        try {
          filePath = window.electronAPI.getPathForFile(f)
        } catch {
          // Fallback to filename
        }
      }
      fileItems.push({
        id: `${Date.now()}-${i}`,
        name: f.name,
        path: filePath,
        size: f.size,
        extension: '.' + f.name.split('.').pop()?.toLowerCase(),
        status: 'pending' as const
      })
    }
    setFiles(prev => [...prev, ...fileItems])
  }, [])

  // Handle files from dialog (already have real paths)
  const handleFilesSelectedViaDialog = useCallback((selectedFiles: SelectedFile[]) => {
    const fileItems: FileItem[] = selectedFiles.map((f, i) => ({
      id: `${Date.now()}-${i}`,
      name: f.name,
      path: f.path,
      size: f.size,
      extension: f.extension,
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
      if (!convertingRef.current) break
      const file = currentFiles[i]
      setCurrentFile(file.name)
      setProgress(Math.round((i / totalFiles) * 100))

      if (window.electronAPI?.convertFile) {
        try {
          const result = await window.electronAPI.convertFile(
            file.path,
            sourceFormat,
            'md',
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
  }, [files, sourceFormat, outputPath])

  const handleCancel = useCallback(() => {
    convertingRef.current = false
    if (timerRef.current) clearInterval(timerRef.current)
    setIsConverting(false)
    setCurrentFile('')
    setFiles(prev => prev.map(f =>
      f.status === 'processing' ? { ...f, status: 'pending' } : f
    ))
  }, [])

  const handleClearCompleted = useCallback(() => {
    setFiles(prev => prev.filter(f => f.status !== 'completed'))
  }, [])

  return (
    <div className="app-container">
      <Header />
      <div className="main-card">
        <DirectionSelect
          sourceFormat={sourceFormat}
          onSourceChange={setSourceFormat}
        />
        <DropZone onFilesSelected={handleFilesSelected} onFilesSelectedViaDialog={handleFilesSelectedViaDialog} />
        <FileList files={files} onRemove={handleRemoveFile} />
        <ProgressBar progress={progress} currentFile={currentFile} elapsedTime={elapsedTime} />
        <ActionBar
          outputPath={outputPath}
          onBrowse={handleBrowse}
          onConvert={handleConvert}
          onCancel={handleCancel}
          onClearCompleted={handleClearCompleted}
          disabled={files.length === 0 || isConverting}
          isConverting={isConverting}
          hasCompleted={files.some(f => f.status === 'completed')}
        />
        <Tip />
      </div>
    </div>
  )
}

export default App
