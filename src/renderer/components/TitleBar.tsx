import { MinimizeIcon, MaximizeIcon, CloseIcon } from './Icons'

export default function TitleBar() {
  const handleMinimize = () => {
    window.electronAPI?.minimize()
  }

  const handleMaximize = () => {
    window.electronAPI?.maximize()
  }

  const handleClose = () => {
    window.electronAPI?.close()
  }

  return (
    <div className="title-bar">
      <div className="title-bar-drag">MarkAny</div>
      <div className="title-bar-controls">
        <button className="title-btn minimize" onClick={handleMinimize} aria-label="最小化"><MinimizeIcon /></button>
        <button className="title-btn maximize" onClick={handleMaximize} aria-label="最大化"><MaximizeIcon /></button>
        <button className="title-btn close" onClick={handleClose} aria-label="关闭"><CloseIcon /></button>
      </div>
    </div>
  )
}
