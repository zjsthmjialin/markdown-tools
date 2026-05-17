import { ipcMain, dialog, BrowserWindow } from 'electron'
import { spawn, ChildProcess } from 'child_process'
import http from 'http'
import path from 'path'
import fs from 'fs'

let pythonProcess: ChildProcess | null = null

function waitForPythonService(maxRetries = 30, interval = 1000): Promise<void> {
  return new Promise((resolve) => {
    let retries = 0
    const check = () => {
      http.get('http://127.0.0.1:8765/', (res) => {
        res.resume()
        resolve()
      }).on('error', () => {
        retries++
        if (retries >= maxRetries) {
          console.error('[Python] Service failed to start after', maxRetries, 'retries')
          resolve()
        } else {
          setTimeout(check, interval)
        }
      })
    }
    check()
  })
}

export async function startPythonService() {
  const isDev = process.env.NODE_ENV === 'development'

  let command: string
  let args: string[]
  let cwd: string

  if (isDev) {
    const pythonDir = path.join(__dirname, '../../src/python')
    command = 'python'
    args = [path.join(pythonDir, 'main.py')]
    cwd = pythonDir
  } else {
    // In production, use the bundled PyInstaller executable
    const backendExe = path.join(process.resourcesPath!, 'python-backend', 'markany-backend.exe')
    // Fall back to Python script if PyInstaller bundle not found
    if (fs.existsSync(backendExe)) {
      command = backendExe
      args = []
      cwd = path.join(process.resourcesPath!, 'python-backend')
    } else {
      const pythonDir = path.join(process.resourcesPath!, 'python-source')
      command = 'python'
      args = [path.join(pythonDir, 'main.py')]
      cwd = pythonDir
    }
  }

  console.log('[Python] Starting service...')
  console.log('[Python] Command:', command, args.join(' '))

  pythonProcess = spawn(command, args, {
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd
  })

  pythonProcess.stdout?.on('data', (data) => {
    console.log('[Python]', data.toString().trim())
  })

  pythonProcess.stderr?.on('data', (data) => {
    console.error('[Python Error]', data.toString().trim())
  })

  pythonProcess.on('error', (err) => {
    console.error('Failed to start Python service:', err)
    pythonProcess = null
  })

  pythonProcess.on('exit', (code) => {
    console.error('[Python] Process exited with code', code)
    pythonProcess = null
  })

  await waitForPythonService()
  console.log('[Python] Service ready')
}

// 通过HTTP与Python服务通信
async function callPythonService(data: {
  filePath: string
  sourceFormat: string
  targetFormat: string
  outputDir?: string
}): Promise<{ success: boolean; outputPath?: string; error?: string; content?: string }> {
  return new Promise((resolve) => {
    let resolved = false
    const postData = JSON.stringify(data)

    const options = {
      hostname: '127.0.0.1',
      port: 8765,
      path: '/',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    }

    const timeout = setTimeout(() => {
      if (!resolved) {
        resolved = true
        req.destroy()
        resolve({ success: false, error: '请求超时' })
      }
    }, 300000)

    const req = http.request(options, (res) => {
      let data = ''
      res.on('data', (chunk) => { data += chunk })
      res.on('end', () => {
        if (!resolved) {
          resolved = true
          clearTimeout(timeout)
          try {
            const result = JSON.parse(data)
            resolve(result)
          } catch (e) {
            resolve({ success: false, error: 'Invalid response from Python service' })
          }
        }
      })
    })

    req.on('error', (e) => {
      if (!resolved) {
        resolved = true
        clearTimeout(timeout)
        resolve({ success: false, error: `连接Python服务失败: ${e.message}` })
      }
    })

    req.write(postData)
    req.end()
  })
}

export function setupIpcHandlers() {
  // 选择文件
  ipcMain.handle('select-files', async () => {
    const result = await dialog.showOpenDialog({
      properties: ['openFile', 'multiSelections'],
      filters: [
        { name: 'Documents', extensions: ['pdf', 'docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt', 'html', 'htm', 'txt', 'md'] }
      ]
    })
    if (result.canceled || result.filePaths.length === 0) return []

    return result.filePaths.map(p => {
      const stat = fs.statSync(p)
      return {
        name: path.basename(p),
        path: p,
        size: stat.size,
        extension: path.extname(p).toLowerCase()
      }
    })
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
    if (outputDir) console.log(`Output dir: ${outputDir}`)

    try {
      const result = await callPythonService({
        filePath,
        sourceFormat,
        targetFormat,
        outputDir
      })

      console.log(`Result: success=${result.success}, error=${result.error || 'none'}`)
      return result
    } catch (error) {
      console.error(`Convert error:`, error)
      return { success: false, error: String(error) }
    }
  })

  // 窗口控制
  ipcMain.handle('window-minimize', () => {
    BrowserWindow.getFocusedWindow()?.minimize()
  })

  ipcMain.handle('window-maximize', () => {
    const win = BrowserWindow.getFocusedWindow()
    if (win?.isMaximized()) {
      win.unmaximize()
    } else {
      win?.maximize()
    }
  })

  ipcMain.handle('window-close', () => {
    BrowserWindow.getFocusedWindow()?.close()
  })
}

export function stopPythonService() {
  if (pythonProcess) {
    pythonProcess.kill()
    pythonProcess = null
    console.log('Python service stopped')
  }
}