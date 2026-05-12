import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import electron from 'vite-plugin-electron'
import path from 'path'

const isDev = process.env.NODE_ENV !== 'production'

export default defineConfig({
  plugins: [
    react(),
    ...(isDev ? [
      electron([
        {
          entry: 'src/main/index.ts',
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
    ] : [])
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
