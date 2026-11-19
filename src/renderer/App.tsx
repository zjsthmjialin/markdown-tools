import { useState, useCallback, useRef, useEffect } from 'react'
import './App.css'
import Header from './components/Header'
import TitleBar from './components/TitleBar'
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
  const [progressDetail, setProgressDetail] = useState('')
  const [isCancelling, setIsCancelling] = useState(false)
  const [isConverting, setIsConverting] = useState(false)
  const [elapsedTime, setElapsedTime] = useState(0)
  const convertingRef = useRef(false)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const cancelRequestedRef = useRef(false)

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [])

  const handleFilesSelected = useCallback(async (newFiles: File[]) => {
    const fileItems: FileItem[] = []
    for (let i = 0; i < newFiles.length; i++) {
      const f = newFiles[i]
      let filePath = f.name
      if (window.electronAPI?.getPathForFile) {
        try {
          filePath = window.electronAPI.getPathForFile(f)
        } catch {
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
    cancelRequestedRef.current = false
    setIsCancelling(false)
    setProgress(0)
    setElapsedTime(0)
    const startTime = Date.now()
    timerRef.current = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime) / 1000))
    }, 1000)

    const currentFiles = files.filter(f => f.status === 'pending' || f.status === 'cancelled' || f.status === 'error')

    if (currentFiles.length === 0) {
      setIsConverting(false)
      convertingRef.current = false
      if (timerRef.current) clearInterval(timerRef.current)
      return
    }

    let completedFiles = files.filter(f => f.status === 'completed').length
    let currentPageFraction = 0
    const removeProgressListener = window.electronAPI?.onConversionProgress?.((detail) => {
      setCurrentFile(detail.file)
      setProgressDetail(detail.pageCount ? `${detail.phase}（第 ${detail.page}/${detail.pageCount} 页）` : detail.phase)
      if (detail.pageCount) {
        currentPageFraction = detail.page / detail.pageCount
        setProgress(Math.min(99, Math.round(((completedFiles + currentPageFraction) / files.length) * 100)))
      }
    })

    for (let i = 0; i < currentFiles.length; i++) {
      if (!convertingRef.current) break
      const file = currentFiles[i]
      setFiles(prev => prev.map(f => f.id === file.id ? { ...f, status: 'processing' } : f))
      setCurrentFile(file.name)
      setProgressDetail('正在准备转换')
      setProgress(Math.min(99, Math.round((completedFiles / files.length) * 100)))

      if (window.electronAPI?.convertFile) {
        try {
          const result = await window.electronAPI.convertFile(
            file.path,
            sourceFormat,
            'md',
            outputPath
          )
          setFiles(prev => prev.map(f =>
            f.id === file.id ? { ...f, status: result.success ? 'completed' : result.cancelled ? 'cancelled' : 'error', error: result.error } : f
          ))
          if (result.success) completedFiles++
          if (result.cancelled || cancelRequestedRef.current) break
        } catch (e) {
          setFiles(prev => prev.map(f =>
            f.id === file.id ? { ...f, status: 'error', error: String(e) } : f
          ))
        }
      }
    }

    removeProgressListener?.()

    const wasCancelled = cancelRequestedRef.current
    setProgress(wasCancelled ? Math.min(99, Math.round(((completedFiles + currentPageFraction) / files.length) * 100)) : 100)
    setCurrentFile('')
    setProgressDetail(wasCancelled ? '已停止；未处理的文件仍在等待' : '')
    setIsCancelling(false)
    cancelRequestedRef.current = false
    setIsConverting(false)
    convertingRef.current = false
    if (timerRef.current) clearInterval(timerRef.current)
    setElapsedTime(Math.floor((Date.now() - startTime) / 1000))
  }, [files, sourceFormat, outputPath])

  const handleCancel = useCallback(async () => {
    cancelRequestedRef.current = true
    setIsCancelling(true)
    if (window.electronAPI?.cancelConversion) await window.electronAPI.cancelConversion()
    else convertingRef.current = false
  }, [])

  const handleClearCompleted = useCallback(() => {
    setFiles(prev => prev.filter(f => f.status !== 'completed'))
  }, [])

  const handleRemoveFile = useCallback((id: string) => {
    if (convertingRef.current) return
    setFiles(prev => prev.filter(f => f.id !== id))
  }, [])

  return (
    <div className="app-container">
      <TitleBar />
      <div className="main-card">
        <Header />
        <DirectionSelect
          sourceFormat={sourceFormat}
          onSourceChange={setSourceFormat}
        />
        <DropZone onFilesSelected={handleFilesSelected} onFilesSelectedViaDialog={handleFilesSelectedViaDialog} />
        <FileList files={files} onRemove={handleRemoveFile} />
        <ProgressBar progress={progress} currentFile={currentFile} detail={isCancelling ? '正在结束当前页面…' : progressDetail} elapsedTime={elapsedTime} />
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
