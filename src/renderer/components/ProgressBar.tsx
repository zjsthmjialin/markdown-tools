interface ProgressBarProps {
  progress: number
  currentFile?: string
  elapsedTime?: number
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return m > 0 ? `${m}分${s}秒` : `${s}秒`
}

export default function ProgressBar({ progress, currentFile, elapsedTime }: ProgressBarProps) {
  if (progress === 0 && !elapsedTime) return null

  return (
    <div className="progress-section active">
      <div className="progress-info">
        <span>{currentFile ? `正在转换: ${currentFile}` : (progress === 100 ? '转换完成' : '正在转换...')}</span>
        <span className="progress-stats">
          {elapsedTime != null && elapsedTime > 0 && <span className="elapsed-time">{formatTime(elapsedTime)}</span>}
          <span>{progress}%</span>
        </span>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
      </div>
    </div>
  )
}