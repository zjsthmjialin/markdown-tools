# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**MarkAny** is a Windows desktop app (Electron 29 + Python backend) that converts documents to Markdown. Supports PDF (text extraction + scanned OCR), Word, Excel, PowerPoint, HTML, TXT.

## Commands

```bash
npm run dev              # Start dev server with hot reload
npm run build            # Full production build (tesseract setup → PyInstaller → tsc → vite → electron-builder)
npm run build:dir        # Build without creating installer (unpacked directory)
npm run build:no-python  # Build without rebuilding Python backend
npm test                 # Frontend tests (Vitest + React Testing Library)
npm run test:python      # cd src/python && python -m pytest tests/ -v
npm run test:all         # Run both frontend and Python tests
npm run python:build     # PyInstaller build of Python backend only
```

No linter is configured.

## Architecture

```
Renderer (React 18 + TypeScript)
    ↕ IPC via preload.ts contextBridge
Main Process (Electron 29)
    ↕ HTTP POST to localhost:8765
Python Backend (http.server + PyMuPDF + MarkItDown + Tesseract OCR)
```

### Electron Main Process (`src/main/`)

- **index.ts** — Creates frameless BrowserWindow, spawns Python backend, manages lifecycle
- **ipc-handlers.ts** — IPC handlers + `callPythonService()` (HTTP to Python, 30-min timeout)
- **preload.ts** — Exposes `window.electronAPI` bridge (selectFiles, convertFile, window controls)

### React Frontend (`src/renderer/`)

- **App.tsx** — Root component, state management, sequential file conversion orchestration
- Single CSS file (`App.css`), dark theme
- Components: TitleBar, Header, DirectionSelect, DropZone, FileList, ProgressBar, ActionBar, Tip

### Python Backend (`src/python/`)

- **main.py** — HTTP server on port 8765. GET `/` = health check, POST `/` = conversion request `{filePath, targetFormat, outputDir}`
- **converters/pdf_converter.py** — `PDFConverter`: PyMuPDF text extraction for text PDFs, 300 DPI render → OpenCV image enhancement (denoise + CLAHE + adaptive threshold) → Tesseract OCR for scanned PDFs. Detects garbled text via Unicode analysis.
- **converters/markitdown_converter.py** — `MarkItDownConverter`: wraps Microsoft MarkItDown for DOCX/XLSX/PPTX/HTML/TXT
- **converters/base.py** — `BaseConverter` ABC + `sanitize_text()` utility
- **ocr/tesseract_ocr.py** — `TesseractOCR`: auto-discovers bundled tesseract-portable, sets TESSDATA_PREFIX env var, falls back chi_sim+eng → eng only
- **utils/image_extractor.py** — Extracts embedded images from PDF/DOCX/PPTX into `images/` subdirectory

### Conversion Pipeline

1. User drops files → `App.tsx` calls `window.electronAPI.convertFile()`
2. IPC → `ipc-handlers.ts` → HTTP POST to Python backend
3. Python dispatches to converter by file extension
4. PDF scanned pages: render 300 DPI → `enhance_scan_image()` → Tesseract OCR
5. After conversion, `ImageExtractor` extracts embedded images
6. `.md` file written to output directory, response travels back through HTTP → IPC → renderer

## Key Config Files

- **electron-builder.yml** — NSIS installer for Windows x64, bundles PyInstaller exe + tesseract-portable as extraResources
- **src/python/markany-backend.spec** — PyInstaller single-file spec, hidden imports include cv2, numpy, pymupdf, pytesseract, magika
- **vite.config.ts** — React + vite-plugin-electron, strips ELECTRON_RUN_AS_NODE (required for correct Electron behavior)

## Tesseract Bundling

`src/python/setup_tesseract.sh` copies tesseract.exe + DLLs + tessdata from system Tesseract installation into `src/python/tesseract-portable/`. At runtime, `TesseractOCR` searches: PyInstaller exe dir → source file dir → TESSERACT_PATH env → system default. Path with spaces handled via TESSDATA_PREFIX env var (not --tessdata-dir flag).
