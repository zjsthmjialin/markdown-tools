interface ActionBarProps {
  outputPath: string
  onBrowse: () => void
  onConvert: () => void
  disabled: boolean
}

export default function ActionBar({
  outputPath,
  onBrowse,
  onConvert,
  disabled
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
      <button
        className="btn-primary"
        onClick={onConvert}
        disabled={disabled}
      >
        <span>▶</span>
        开始转换
      </button>
    </div>
  )
}