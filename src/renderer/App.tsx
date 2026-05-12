import './App.css'
import DropZone from './components/DropZone'

function App() {
  const handleFilesSelected = (files: File[]) => {
    console.log('Selected files:', files)
  }

  return (
    <div className="app-container">
      <DropZone onFilesSelected={handleFilesSelected} />
    </div>
  )
}

export default App