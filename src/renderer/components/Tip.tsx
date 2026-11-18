import { InfoIcon } from './Icons'

export default function Tip() {
  return (
    <div className="tip">
      <span className="tip-icon"><InfoIcon /></span>
      <div>
        <div>支持拖放多个文件进行批量转换。转换后的文件将保存在您指定的输出目录中。</div>
        <div className="tip-contact">联系作者：zjsthm@gmail.com</div>
      </div>
    </div>
  )
}
