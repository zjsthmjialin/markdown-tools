# MarkAny - 文档转 Markdown 工具设计文档

**版本**: 2.0
**日期**: 2026-05-17
**状态**: 已完成

---

## 1. 项目概述

### 1.1 项目目标
开发一款桌面应用程序 **MarkAny**，实现文档格式到 Markdown 的高质量转换：
- **转换方向**：PDF、Word、Excel、PowerPoint、HTML、TXT → Markdown
- **核心价值**：
  - 一键安装，无需任何外部运行环境
  - 简洁直观的用户界面
  - 批量处理能力

### 1.2 设计决策

**为什么只做正向转换？**
1. 反向转换（Markdown → 文档）需要 Microsoft Office COM 自动化，用户环境不一致容易失败
2. PDF 转 DOCX/PPTX 无法保留原有格式和可编辑性
3. 简化产品聚焦核心功能，降低维护成本

**为什么使用 MarkItDown？**
- 无需 Office 安装即可处理 DOCX/XLSX/PPTX
- 统一接口简化代码复杂度
- 稳定可靠的开源解决方案

---

## 2. 技术架构

### 2.1 桌面框架
| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 桌面框架 | Electron 29 | 跨平台桌面应用框架 |
| 前端UI | React 18 + TypeScript | 现代化组件化开发 |
| 后端服务 | Python HTTP Server | 文档转换处理核心 |
| 通信方式 | IPC + HTTP | 主进程与渲染进程、Python 服务通信 |

### 2.2 Python 服务架构
```
renderer (React)
    ↓ IPC
main (Electron)
    ↓ HTTP POST :8765
python-backend (Flask)
    ↓
converters/ (各格式转换器)
    ↓
image_extractor/ (图片提取)
```

### 2.3 打包方案
| 项目 | 方案 |
|------|------|
| 前端打包 | electron-builder |
| 后端打包 | PyInstaller (--onedir) |
| 安装格式 | Windows (.exe installer) |
| 预期大小 | ~200-300 MB |

### 2.4 运行时捆绑
用户**无需预装任何环境**，安装包完整捆绑：
- Electron 运行时
- Node.js 运行时
- Python 3.11/3.12
- Tesseract OCR 5.x + 语言数据包（可选）

---

## 3. 功能规格

### 3.1 支持的转换格式

| 源格式 | 扩展名 | 处理库 |
|--------|--------|--------|
| PDF | .pdf | PyMuPDF + Tesseract OCR（可选） |
| Word | .docx, .doc | MarkItDown |
| Excel | .xlsx, .xls | MarkItDown |
| PowerPoint | .pptx, .ppt | MarkItDown |
| HTML | .html, .htm | MarkItDown |
| TXT | .txt | 自动编码检测 |

### 3.2 图片处理
- 从 PDF/DOCX/PPTX 中自动提取嵌入图片
- 保存到输出目录的 `images/` 子目录
- Markdown 中使用相对路径引用：`![](images/xxx.png)`

### 3.3 转换质量标准
- [x] 保留原始文档层级结构（# 标题）
- [x] 保留表格格式（Markdown表格语法）
- [x] 保留图片（自动提取并本地化）
- [x] 保留代码块和语法高亮标记
- [x] 保留超链接
- [x] OCR支持扫描件PDF（需要 Tesseract）

---

## 4. 用户界面设计

### 4.1 界面风格
- **主题**：深色主题（#252525 背景）
- **主色调**：紫色渐变（#6366f1 → #818cf8）
- **字体**：系统默认字体
- **圆角**：8px / 12px / 16px 三级

### 4.2 布局结构

```
┌─────────────────────────────────────────────────┐
│  📄 MarkAny                                      │
│  文档转 Markdown                                  │
├─────────────────────────────────────────────────┤
│                                                  │
│  源格式: [自动检测 ▼]  →  目标格式: [Markdown]   │
│                                                  │
│  ┌─────────────────────────────────────────┐   │
│  │       📁 拖放文件到此处                   │   │
│  │         或点击选择文件                     │   │
│  └─────────────────────────────────────────┘   │
│                                                  │
│  待转换文件                          3 个文件     │
│  ┌─────────────────────────────────────────┐   │
│  │ 📕 2024报告.pdf        ✅ 已完成   ✕    │   │
│  │ 📗 PRD文档.docx        🔄 转换中   ✕    │   │
│  │ 📘 数据统计.xlsx       ⏳ 等待中   ✕    │   │
│  └─────────────────────────────────────────┘   │
│                                                  │
│  进度: ████████░░░░░░░░░  67%  12秒            │
│                                                  │
│  输出目录: [默认位置：原文件目录    ] [浏览...]  │
│                              [▶ 开始转换]       │
│                                                  │
│  💡 支持拖放多个文件批量转换...                   │
└─────────────────────────────────────────────────┘
```

### 4.3 状态指示
| 状态 | 颜色 | 图标 |
|------|------|------|
| 已完成 | 绿色 (#4caf50) | ✅ |
| 转换中 | 紫色 (#818cf8) | 🔄 |
| 等待中 | 灰色 (#888) | ⏳ |
| 错误 | 红色 (#f44336) | ❌ |

### 4.4 交互状态

**空闲状态**
- 显示"开始转换"按钮
- 输出目录显示或浏览按钮

**转换中状态**
- 显示"取消"按钮（红色）
- 进度条实时更新
- 当前处理文件名显示
- 已用时间显示

**转换完成状态**
- 显示"清除已完成"和"重置"按钮
- 已完成文件保持绿色标记

---

## 5. 项目结构

```
markany/
├── src/
│   ├── main/                    # Electron 主进程
│   │   ├── index.ts             # 入口文件，创建窗口
│   │   ├── ipc-handlers.ts      # IPC 通信处理
│   │   └── preload.ts           # 预加载脚本，暴露 API
│   ├── renderer/                # React 前端
│   │   ├── components/          # UI 组件
│   │   │   ├── Header.tsx       # 顶部标题
│   │   │   ├── DirectionSelect.tsx  # 格式选择
│   │   │   ├── DropZone.tsx     # 文件拖放区
│   │   │   ├── FileList.tsx     # 文件列表
│   │   │   ├── ProgressBar.tsx  # 进度条
│   │   │   ├── ActionBar.tsx    # 操作栏
│   │   │   └── Tip.tsx          # 提示信息
│   │   ├── __tests__/          # 组件测试
│   │   ├── App.tsx             # 主组件
│   │   ├── App.css             # 样式
│   │   └── types.ts            # TypeScript 类型
│   └── python/                 # Python 后端
│       ├── main.py             # HTTP 服务入口
│       ├── converters/         # 各格式转换器
│       │   ├── pdf_converter.py # PDF 处理
│       │   └── markitdown_converter.py  # MarkItDown 封装
│       └── utils/
│           └── image_extractor.py  # 图片提取
├── docs/                       # 文档
├── package.json               # Node 依赖
├── requirements.txt           # Python 依赖
├── electron-builder.yml       # 打包配置
├── README.md
└── CLAUDE.md
```

---

## 6. 核心模块说明

### 6.1 Electron 主进程
- `index.ts`: 创建 BrowserWindow，管理应用生命周期
- `ipc-handlers.ts`: 处理 selectFiles、selectDirectory、convertFile 等 IPC 调用
- `preload.ts`: 在 contextIsolation 下安全暴露 electronAPI

### 6.2 React 前端
- `App.tsx`: 状态管理，处理文件转换流程
- `DropZone.tsx`: 拖放和点击选择文件
- `FileList.tsx`: 显示文件列表及状态
- `ActionBar.tsx`: 输出路径和操作按钮

### 6.3 Python 后端
- `main.py`: Flask HTTP 服务，端口 8765
- `/convert`: POST 接口，接收文件路径和参数
- `pdf_converter.py`: PyMuPDF 提取文本 + OCR
- `markitdown_converter.py`: MarkItDown 处理 Office 格式
- `image_extractor.py`: 从文档提取图片

---

## 7. 用户体验要求

### 7.1 安装体验
- [x] 一键安装，无需配置
- [x] Windows x64 系统兼容
- [x] 安装包可执行文件格式

### 7.2 使用体验
- [x] 拖放文件即可添加
- [x] 点击也可选择文件
- [x] 批量文件转换支持
- [x] 实时进度显示
- [x] 文件状态实时更新
- [x] 转换可取消
- [x] 完成后可清除结果

---

## 8. 验收标准

- [x] 界面设计与规格一致
- [x] 设计文档已更新
- [x] 核心转换功能可运行
- [x] 安装包可正常安装
- [x] 全部测试通过 (22 tests)
- [x] README 已更新

---

## 9. 技术限制

### 9.1 已移除的功能
- ~~Markdown → PDF~~ (需要 WeasyPrint/GTK)
- ~~Markdown → DOCX~~ (需要 Office COM)
- ~~Markdown → PPTX~~ (需要 Office COM)
- ~~DOCX → PDF~~ (格式无法保留)
- ~~PPTX → PDF~~ (格式无法保留)

### 9.2 可选功能
- OCR: 需要系统安装 Tesseract，无则降级为纯文本提取

---

**更新日志**
- v2.0 (2026-05-17): 移除反向转换功能，聚焦文档→Markdown 单向转换
- v1.0 (2026-05-12): 初始设计，支持双向转换