interface DirectionSelectProps {
  sourceFormat: string
  targetFormat: string
  onSourceChange: (value: string) => void
  onTargetChange: (value: string) => void
}

export default function DirectionSelect({
  sourceFormat,
  targetFormat,
  onSourceChange,
  onTargetChange
}: DirectionSelectProps) {
  const sourceOptions = [
    { value: 'auto', label: '自动检测' },
    { value: 'pdf', label: 'PDF 文档' },
    { value: 'docx', label: 'Word 文档' },
    { value: 'xlsx', label: 'Excel 表格' },
    { value: 'pptx', label: 'PowerPoint' },
    { value: 'html', label: 'HTML 网页' },
    { value: 'txt', label: '纯文本' },
    { value: 'md', label: 'Markdown' }
  ]

  const getTargetOptions = () => {
    if (sourceFormat === 'md') {
      return [
        { value: 'pdf', label: 'PDF 文档' },
        { value: 'docx', label: 'Word 文档' },
        { value: 'pptx', label: 'PowerPoint' },
        { value: 'html', label: 'HTML 网页' }
      ]
    }
    return [
      { value: 'md', label: 'Markdown' },
      { value: 'pdf', label: 'PDF 文档' },
      { value: 'docx', label: 'Word 文档' },
      { value: 'pptx', label: 'PowerPoint' },
      { value: 'html', label: 'HTML 网页' }
    ]
  }

  return (
    <div className="direction-section">
      <div className="direction-group">
        <div className="direction-label">源格式</div>
        <div className="select-wrapper">
          <select
            value={sourceFormat}
            onChange={e => onSourceChange(e.target.value)}
          >
            {sourceOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>
      <div className="direction-arrow">→</div>
      <div className="direction-group">
        <div className="direction-label">目标格式</div>
        <div className="select-wrapper">
          <select
            value={targetFormat}
            onChange={e => onTargetChange(e.target.value)}
          >
            {getTargetOptions().map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  )
}