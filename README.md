# MarkAny - 文档转 Markdown 工具

一款简洁高效的桌面应用，将 PDF、Word、Excel、PowerPoint、HTML 等格式文档转换为 Markdown，无需安装任何额外软件。

## 功能特点

- **多格式支持**：PDF、DOCX、DOC、XLSX、XLS、PPTX、PPT、HTML、HTM、TXT → Markdown
- **格式保留**：PDF 转换保留粗体、斜体、标题层级等格式
- **图片提取**：自动提取文档中的图片并保存
- **OCR 识别**：扫描件/图片版 PDF 通过 Tesseract OCR 识别中英文文本（OCR 引擎已内置，无需额外安装）
- **智能分流**：自动检测文字版/扫描版 PDF，文字版快速提取，扫描版 OCR 兜底
- **批量处理**：一次添加多个文件批量转换
- **零依赖**：无需 Microsoft Office、Adobe Acrobat、或单独安装 Tesseract OCR
- **简洁界面**：拖放操作，开箱即用
- **跨平台**：提供 Windows（.exe）与 macOS（.dmg）两种安装包

## 支持格式

| 格式类型 | 支持扩展名 | 处理方式 |
|---------|-----------|----------|
| PDF（文字版） | .pdf | PyMuPDF 结构化提取（保留粗体/斜体/标题） |
| PDF（扫描件） | .pdf | 图片渲染 + OpenCV 增强 + Tesseract OCR（中英文） |
| Word | .docx, .doc | MarkItDown |
| Excel | .xlsx, .xls | MarkItDown |
| PowerPoint | .pptx, .ppt | MarkItDown |
| HTML | .html, .htm | MarkItDown |
| 纯文本 | .txt | 自动编码检测 |

## 更新日志

### v1.0.3-mac
- 在 v1.0.3 基础上适配 macOS：便携 Python 运行后端、绑定 macOS 版 Tesseract（含 chi_sim + eng 语言包）
- 新增 `electron-builder` 的 `mac` 目标（dmg / arm64），Python 源码、便携 Python、Tesseract 作为 `extraResources` 打进 `.app`
- 转换功能与 Windows v1.0.3 完全一致（共用同一套 Python 核心）

### v1.0.3
- 重构 PDF 转 Markdown 核心转换逻辑
- 文字版 PDF：使用 PyMuPDF dict 格式提取，保留粗体、斜体、标题层级
- 全局字体检测：跨文档统计正文字号/字体，避免版权页等特殊页粗体误判
- 扫描版 PDF：自动检测 + OpenCV 图像增强 + OCR 兜底
- 页间分隔改为 `---` 分隔线
- 添加 PyInstaller `_MEIPASS` 路径检测，完善打包兼容性
- 新增 `forceOCR` 选项支持
- 打包改为 onedir 模式并排除 chardet，修复部分环境下安装后无法启动、后端崩溃（0xC0000005）的问题；字符集检测改用纯 Python 版 charset-normalizer
- 清理反向转换遗留死代码，修复 Python 测试与依赖

### v1.0.2
- 添加自适应图像增强提升扫描件 OCR 质量
- 延长 HTTP 请求超时至 30 分钟以支持大型扫描件 OCR

### v1.0.0
- 初始发布

## 安装

### Windows

下载 `MarkAny-Setup-1.0.3.exe` 运行安装即可，无需配置任何环境。安装包约 245MB（已内置 Tesseract OCR 引擎及中英文语言包）。

### macOS

1. 下载 `MarkAny-1.0.3-mac-arm64.dmg`（Apple 芯片）
2. 打开 DMG，将 MarkAny 拖入「应用程序」文件夹
3. **首次打开如果提示「已损坏」或「无法验证开发者」**，在终端运行一次：

   ```bash
   sudo xattr -rd com.apple.quarantine /Applications/MarkAny.app
   ```

   然后重新打开即可。（因为应用未做 Apple 签名/公证，这是自用未签名 App 的正常提示。）

## 使用方法

1. 选择源文件格式（或选择"自动检测"）
2. 拖放或点击选择文件
3. 设置输出目录（默认与原文件相同目录）
4. 点击"开始转换"

## OCR 说明

扫描版 PDF 的转换流程：
1. 自动检测 PDF 是否为扫描件（按页面图片/文字比例判断）
2. 对图片页面渲染为 300 DPI 图像
3. OpenCV 自适应图像增强（去噪 + 对比度增强 + 二值化）
4. 调用内置 Tesseract OCR 识别中英文文本
5. 对识别结果进行文本清洗（去除控制字符）

OCR 质量取决于原始扫描件的清晰度。清晰度越高，识别效果越好。

## 系统要求

- Windows 10/11（64 位），或 macOS 12+（Apple 芯片）
- 约 500MB 可用磁盘空间

## 联系作者

- 邮箱：zjsthm@gmail.com
