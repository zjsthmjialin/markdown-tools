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
        <button className="title-btn minimize" onClick={handleMinimize}>─</button>
        <button className="title-btn maximize" onClick={handleMaximize}>□</button>
        <button className="title-btn close" onClick={handleClose}>✕</button>
      </div>
    </div>
  )
}