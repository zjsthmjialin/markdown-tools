# MarkAny - 文档转 Markdown 工具

一款简洁高效的桌面应用，将 PDF、Word、Excel、PowerPoint、HTML 等格式文档转换为 Markdown，无需安装任何额外软件。

## 功能特点

- **多格式支持**：PDF、DOCX、DOC、XLSX、XLS、PPTX、PPT、HTML、HTM、TXT → Markdown
- **图片提取**：自动提取文档中的图片并保存
- **OCR 识别**：扫描件/图片版 PDF 通过 Tesseract OCR 识别中英文文本（OCR 引擎已内置，无需额外安装）
- **批量处理**：一次添加多个文件批量转换
- **零依赖**：无需 Microsoft Office、Adobe Acrobat、或单独安装 Tesseract OCR
- **简洁界面**：拖放操作，开箱即用

## 支持格式

| 格式类型 | 支持扩展名 | 处理方式 |
|---------|-----------|----------|
| PDF（文字版） | .pdf | PyMuPDF 文本提取 |
| PDF（扫描件） | .pdf | 图片渲染 + Tesseract OCR（中英文） |
| Word | .docx, .doc | MarkItDown |
| Excel | .xlsx, .xls | MarkItDown |
| PowerPoint | .pptx, .ppt | MarkItDown |
| HTML | .html, .htm | MarkItDown |
| 纯文本 | .txt | 自动编码检测 |

## 安装

下载 `MarkAny-Setup-1.0.0.exe` 运行安装即可，无需配置任何环境。安装包约 210MB（已内置 Tesseract OCR 引擎及中英文语言包）。

## 使用方法

1. 选择源文件格式（或选择"自动检测"）
2. 拖放或点击选择文件
3. 设置输出目录（默认与原文件相同目录）
4. 点击"开始转换"

## OCR 说明

扫描版 PDF 的转换流程：
1. 自动检测 PDF 是否为扫描件（按页面图片/文字比例判断）
2. 对图片页面渲染为 300 DPI 图像
3. 调用内置 Tesseract OCR 识别中英文文本
4. 对识别结果进行文本清洗（去除控制字符）

OCR 质量取决于原始扫描件的清晰度。清晰度越高，识别效果越好。

## 系统要求

- Windows 10/11 (64位)
- 约 500MB 可用磁盘空间

## 联系作者

- 邮箱：zjsthm@gmail.com