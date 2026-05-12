# MarkAny - 文档双向转换工具设计文档

**版本**: 1.0
**日期**: 2026-05-12
**状态**: 已批准

---

## 1. 项目概述

### 1.1 项目目标
开发一款桌面应用程序 **MarkAny**，实现文档格式的双向高质量转换：
- **正向转换**：PDF、Word、Excel、PowerPoint、HTML、TXT → Markdown
- **反向转换**：Markdown → PDF、Word、HTML

### 1.2 核心价值
- 高质量格式还原（标题、表格、图片、代码块）
- 一键安装，无需配置任何运行环境
- 简洁直观的用户界面

---

## 2. 技术架构

### 2.1 桌面框架
| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 桌面框架 | Electron | 跨平台桌面应用框架 |
| 前端UI | React + TypeScript | 现代化组件化开发 |
| 后端服务 | Python | 文档转换处理核心 |
| 通信方式 | IPC | 主进程与渲染进程通信 |

### 2.2 打包方案
| 项目 | 方案 |
|------|------|
| 打包工具 | electron-builder + PyInstaller |
| 安装格式 | Windows (.exe installer) |
| 预期大小 | ~200-300 MB |

### 2.3 运行时捆绑
用户**无需预装任何环境**，安装包完整捆绑：
- Electron 运行时
- Node.js 运行时
- Python 3.11/3.12
- Tesseract OCR 5.x + 语言数据包

---

## 3. 功能规格

### 3.1 支持的转换格式

#### 正向转换（文档 → Markdown）
| 源格式 | 扩展名 | 处理库 |
|--------|--------|--------|
| PDF | .pdf | pdfplumber / PyMuPDF + Tesseract OCR |
| Word | .doc, .docx | python-docx |
| Excel | .xls, .xlsx | openpyxl |
| PowerPoint | .ppt, .pptx | python-pptx |
| HTML | .html, .htm | BeautifulSoup + html2text |
| TXT | .txt | 自动编码检测 |

#### 反向转换（Markdown → 文档）
| 目标格式 | 实现库 |
|----------|--------|
| PDF | WeasyPrint / reportlab |
| Word | python-docx |
| HTML | Markdown解析器 |

### 3.2 转换质量标准
- [x] 保留原始文档层级结构（# 标题）
- [x] 保留表格格式（Markdown表格语法）
- [x] 保留图片（自动提取并本地化）
- [x] 保留代码块和语法高亮标记
- [x] 保留超链接
- [x] OCR支持扫描件PDF

---

## 4. 用户界面设计

### 4.1 界面风格
- **主题**：深色主题（#0f0f0f 背景）
- **主色调**：紫色渐变（#6366f1 → #818cf8）
- **字体**：Noto Sans SC（中文）+ JetBrains Mono（代码）
- **圆角**：8px / 12px / 16px 三级

### 4.2 布局结构

```
┌─────────────────────────────────────────────┐
│  📄 MarkAny                                  │
│  支持多格式双向转换                           │
├─────────────────────────────────────────────┤
│                                              │
│  源格式: [自动检测 ▼]  →  目标格式: [MD ▼]   │
│                                              │
│  ┌─────────────────────────────────────┐    │
│  │       📁 拖放文件到此处              │    │
│  │         或点击选择文件                │    │
│  └─────────────────────────────────────┘    │
│                                              │
│  待转换文件                    3 个文件       │
│  ┌─────────────────────────────────────┐    │
│  │ 📕 2024报告.pdf     ✅ 已完成  ✕   │    │
│  │ 📗 PRD文档.docx     🔄 转换中  ✕   │    │
│  │ 📘 数据统计.xlsx    ⏳ 等待中  ✕   │    │
│  └─────────────────────────────────────┘    │
│                                              │
│  进度: ████████░░░░░░░░░░ 67%              │
│                                              │
│  输出目录: C:\...\MarkAny    [浏览...]       │
│                           [▶ 开始转换]      │
│                                              │
│  💡 支持拖放多个文件批量转换...              │
└─────────────────────────────────────────────┘
```

### 4.3 状态指示
| 状态 | 颜色 | 图标 |
|------|------|------|
| 已完成 | 绿色 (#22c55e) | ✅ |
| 转换中 | 紫色 (#6366f1) | 🔄 |
| 等待中 | 黄色 (#f59e0b) | ⏳ |
| 错误 | 红色 (#ef4444) | ❌ |

---

## 5. 项目结构

```
markany/
├── src/
│   ├── main/                    # Electron 主进程
│   │   ├── index.ts             # 入口文件
│   │   ├── ipc-handlers.ts      # IPC 通信处理
│   │   └── python-bridge.ts    # Python 服务桥接
│   ├── renderer/                # React 前端
│   │   ├── components/          # UI 组件
│   │   │   ├── Header.tsx
│   │   │   ├── DropZone.tsx
│   │   │   ├── FileList.tsx
│   │   │   ├── ProgressBar.tsx
│   │   │   └── ActionBar.tsx
│   │   ├── hooks/              # 自定义 Hooks
│   │   ├── styles/             # 样式文件
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── python/                 # Python 后端
│       ├── converters/         # 各格式转换器
│       │   ├── pdf_converter.py
│       │   ├── docx_converter.py
│       │   ├── xlsx_converter.py
│       │   ├── pptx_converter.py
│       │   ├── html_converter.py
│       │   └── markdown_converter.py
│       ├── markdown/           # Markdown 解析/生成
│       │   ├── parser.py
│       │   └── generator.py
│       ├── ocr/                # OCR 处理
│       │   └── tesseract_ocr.py
│       └── utils/
│           ├── file_handler.py
│           └── image_extractor.py
├── installer/                  # 安装包配置
├── docs/                       # 文档
│   └── specs/                  # 设计文档
├── markany-prototype.html      # 界面原型
├── package.json
├── requirements.txt            # Python 依赖
├── README.md
└── CLAUDE.md
```

---

## 6. 用户体验要求

### 6.1 安装体验
- [x] 一键安装，无需配置
- [x] Windows x64 系统兼容
- [x] 安装包可执行文件格式

### 6.2 使用体验
- [x] 拖放文件即可添加
- [x] 批量文件转换支持
- [x] 实时进度显示
- [x] 转换结果预览
- [x] 文件状态实时更新

---

## 7. 后续迭代（暂不实现）
- [ ] macOS / Linux 支持
- [ ] 便携版（无需安装）
- [ ] 命令行模式
- [ ] 云端同步

---

## 8. 验收标准
- [ ] 界面原型已确认
- [ ] 设计文档已批准
- [ ] 核心转换功能可运行
- [ ] 安装包可正常安装
- [ ] 基础转换功能测试通过
