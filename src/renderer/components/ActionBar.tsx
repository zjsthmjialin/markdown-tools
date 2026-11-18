import { PlayIcon } from './Icons'

interface ActionBarProps {
  outputPath: string
  onBrowse: () => void
  onConvert: () => void
  onCancel: () => void
  onClearCompleted: () => void
  disabled: boolean
  isConverting: boolean
  hasCompleted: boolean
}

export default function ActionBar({
  outputPath,
  onBrowse,
  onConvert,
  onCancel,
  onClearCompleted,
  disabled,
  isConverting,
  hasCompleted
}: ActionBarProps) {
  return (
    <div className="action-bar">
      <div className="output-path">
        <label className="output-label" htmlFor="output-path">输出目录</label>
        <input
          id="output-path"
          type="text"
          className="output-input"
          value={outputPath || '默认位置：原文件目录'}
          readOnly
        />
        <button className="btn-browse" onClick={onBrowse}>
          浏览...
        </button>
      </div>
      {isConverting ? (
        <button className="btn-cancel" onClick={onCancel}>
          取消
        </button>
      ) : hasCompleted ? (
        <div className="action-buttons">
          <button className="btn-clear" onClick={onClearCompleted}>
            清除已完成
          </button>
          <button className="btn-reset" onClick={onBrowse}>
            重置
          </button>
        </div>
      ) : (
        <button
          className="btn-primary"
          onClick={onConvert}
          disabled={disabled}
        >
          <PlayIcon />
          开始转换
        </button>
      )}
    </div>
  )
}