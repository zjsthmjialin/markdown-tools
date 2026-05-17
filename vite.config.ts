import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import electron from 'vite-plugin-electron'
import path from 'path'

// 关键：移除 ELECTRON_RUN_AS_NODE，否则 Electron 会以 Node.js 模式运行
delete process.env.ELECTRON_RUN_AS_NODE

export default defineConfig({
  plugins: [
    react(),
    electron([
      {
        entry: 'src/main/index.ts',
        onstart(options) {
          // 确保子进程也不会继承 ELECTRON_RUN_AS_NODE
          delete process.env.ELECTRON_RUN_AS_NODE
          options.startup()
        },
        vite: {
          build: {
            outDir: 'dist-electron/main'
          }
        }
      },
      {
        entry: 'src/main/preload.ts',
        onstart(options) {
          options.reload()
        },
        vite: {
          build: {
            outDir: 'dist-electron/preload'
          }
        }
      }
    ])
  ],
  build: {
    outDir: 'dist'
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src/renderer')
    }
  }
})
