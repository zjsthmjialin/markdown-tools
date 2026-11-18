import { ArrowRightIcon } from './Icons'

interface DirectionSelectProps {
  sourceFormat: string
  onSourceChange: (value: string) => void
}

export default function DirectionSelect({
  sourceFormat,
  onSourceChange
}: DirectionSelectProps) {
  const sourceOptions = [
    { value: 'auto', label: '自动检测' },
    { value: 'pdf', label: 'PDF 文档' },
    { value: 'docx', label: 'Word 文档' },
    { value: 'xlsx', label: 'Excel 表格' },
    { value: 'pptx', label: 'PowerPoint' },
    { value: 'html', label: 'HTML 网页' },
    { value: 'txt', label: '纯文本' }
  ]

  return (
    <div className="direction-section">
      <div className="direction-group">
        <label className="direction-label" htmlFor="source-format">源格式</label>
        <div className="select-wrapper">
          <select
            id="source-format"
            value={sourceFormat}
            onChange={e => onSourceChange(e.target.value)}
          >
            {sourceOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>
      <div className="direction-arrow"><ArrowRightIcon /></div>
      <div className="direction-group">
        <div className="direction-label">目标格式</div>
        <div className="target-chip">Markdown</div>
      </div>
    </div>
  )
}