interface ProgressBarProps {
  progress: number
  currentFile?: string
}

export default function ProgressBar({ progress, currentFile }: ProgressBarProps) {
  if (progress === 0) return null

  return (
    <div className="progress-section active">
      <div className="progress-info">
        <span>{currentFile ? `正在转换: ${currentFile}` : '正在转换...'}</span>
        <span>{progress}%</span>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
      </div>
    </div>
  )
}