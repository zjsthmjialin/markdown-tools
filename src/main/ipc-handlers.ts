import { ipcMain, dialog, BrowserWindow } from 'electron'
import { spawn, ChildProcess } from 'child_process'
import http from 'http'
import path from 'path'

let pythonProcess: ChildProcess | null = null

export function startPythonService() {
  // 获取Python脚本路径
  const pythonScript = path.join(__dirname, '../../src/python/main.py')

  pythonProcess = spawn('python', [pythonScript], {
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd: path.join(__dirname, '../../src/python')
  })

  pythonProcess.stdout?.on('data', (data) => {
    console.log('[Python]', data.toString().trim())
  })

  pythonProcess.stderr?.on('data', (data) => {
    console.error('[Python Error]', data.toString().trim())
  })

  pythonProcess.on('error', (err) => {
    console.error('Failed to start Python service:', err)
  })

  console.log('Python conversion service starting...')
}

// 通过HTTP与Python服务通信
async function callPythonService(data: {
  filePath: string
  sourceFormat: string
  targetFormat: string
  outputDir?: string
}): Promise<{ success: boolean; outputPath?: string; error?: string; content?: string }> {
  return new Promise((resolve) => {
    const postData = JSON.stringify(data)

    const options = {
      hostname: 'localhost',
      port: 8765,
      path: '/',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    }

    const req = http.request(options, (res) => {
      let data = ''
      res.on('data', (chunk) => { data += chunk })
      res.on('end', () => {
        try {
          const result = JSON.parse(data)
          resolve(result)
        } catch (e) {
          resolve({ success: false, error: 'Invalid response from Python service' })
        }
      })
    })

    req.on('error', (e) => {
      resolve({ success: false, error: `连接Python服务失败: ${e.message}` })
    })

    req.write(postData)
    req.end()

    // 超时处理
    setTimeout(() => {
      req.destroy()
      resolve({ success: false, error: '请求超时' })
    }, 60000)
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
  ipcMain.handle('convert-file', async (_event, filePath: string, sourceFormat: string, targetFormat: string, outputDir?: string) => {
    console.log(`Converting: ${filePath} (${sourceFormat} -> ${targetFormat})`)

    try {
      const result = await callPythonService({
        filePath,
        sourceFormat,
        targetFormat,
        outputDir
      })

      return result
    } catch (error) {
      return { success: false, error: String(error) }
    }
  })

  // 健康检查
  ipcMain.handle('check-python-service', async () => {
    return new Promise((resolve) => {
      http.get('http://localhost:8765/', (res) => {
        let data = ''
        res.on('data', (chunk) => { data += chunk })
        res.on('end', () => {
          try {
            resolve({ status: 'ok', ...JSON.parse(data) })
          } catch {
            resolve({ status: 'ok' })
          }
        })
      }).on('error', () => {
        resolve({ status: 'not running' })
      })
    })
  })
}

export function stopPythonService() {
  if (pythonProcess) {
    pythonProcess.kill()
    pythonProcess = null
    console.log('Python service stopped')
  }
}