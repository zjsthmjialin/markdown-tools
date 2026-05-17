interface ActionBarProps {
  outputPath: string
  onBrowse: () => void
  onConvert: () => void
  onCancel: () => void
  onReset: () => void
  disabled: boolean
  isConverting: boolean
  hasCompleted: boolean
}

export default function ActionBar({
  outputPath,
  onBrowse,
  onConvert,
  onCancel,
  onReset,
  disabled,
  isConverting,
  hasCompleted
}: ActionBarProps) {
  return (
    <div className="action-bar">
      <div className="output-path">
        <span className="output-label">输出目录:</span>
        <input
          type="text"
          className="output-input"
          value={outputPath}
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
        <button className="btn-reset" onClick={onReset}>
          重置
        </button>
      ) : (
        <button
          className="btn-primary"
          onClick={onConvert}
          disabled={disabled}
        >
          <span>▶</span>
          开始转换
        </button>
      )}
    </div>
  )
}
