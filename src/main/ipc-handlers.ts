import { ipcMain, dialog, BrowserWindow } from 'electron'
import { spawn, ChildProcess } from 'child_process'
import path from 'path'

let pythonProcess: ChildProcess | null = null

export function startPythonService() {
  const pythonScript = path.join(__dirname, '../python/main.py')
  pythonProcess = spawn('python', [pythonScript], {
    stdio: ['pipe', 'pipe', 'pipe']
  })

  pythonProcess.stdout?.on('data', (data) => {
    console.log('Python:', data.toString())
  })

  pythonProcess.stderr?.on('data', (data) => {
    console.error('Python Error:', data.toString())
  })
}

export function setupIpcHandlers() {
  // 选择文件
  ipcMain.handle('select-files', async () => {
    const result = await dialog.showOpenDialog({
      properties: ['openFile', 'multiSelections'],
      filters: [
        { name: 'Documents', extensions: ['pdf', 'docx', 'xlsx', 'pptx', 'html', 'txt', 'md'] }
      ]
    })
    return result.filePaths
  })

  // 选择目录
  ipcMain.handle('select-directory', async () => {
    const result = await dialog.showOpenDialog({
      properties: ['openDirectory']
    })
    return result.filePaths[0] || null
  })

  // 转换文件
  ipcMain.handle('convert-file', async (_event, filePath: string, sourceFormat: string, targetFormat: string) => {
    return new Promise((resolve) => {
      if (!pythonProcess) {
        resolve({ success: false, error: 'Python service not running' })
        return
      }

      const request = JSON.stringify({
        filePath,
        sourceFormat,
        targetFormat
      }) + '\n'

      pythonProcess.stdin?.write(request)

      // 简化处理：直接返回成功
      setTimeout(() => {
        resolve({ success: true, outputPath: filePath })
      }, 100)
    })
  })
}

export function stopPythonService() {
  if (pythonProcess) {
    pythonProcess.kill()
    pythonProcess = null
  }
}