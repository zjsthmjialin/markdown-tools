# MarkAny - 文档转 Markdown 工具

一款简洁高效的桌面应用，将 PDF、Word、Excel、PowerPoint、HTML 等格式文档转换为 Markdown，无需安装任何额外软件。

## 功能特点

- **多格式支持**：PDF、DOCX、DOC、XLSX、XLS、PPTX、PPT、HTML、HTM、TXT → Markdown
- **图片提取**：自动提取文档中的图片并保存
- **OCR 识别**：扫描件 PDF 也能转换为可编辑文本
- **批量处理**：一次添加多个文件批量转换
- **零依赖**：无需 Microsoft Office、Adobe Acrobat 等任何外部软件
- **简洁界面**：拖放操作，开箱即用

## 支持格式

| 格式类型 | 支持扩展名 | 处理方式 |
|---------|-----------|----------|
| PDF | .pdf | PyMuPDF + Tesseract OCR |
| Word | .docx, .doc | MarkItDown |
| Excel | .xlsx, .xls | MarkItDown |
| PowerPoint | .pptx, .ppt | MarkItDown |
| HTML | .html, .htm | MarkItDown |
| 纯文本 | .txt | 自动编码检测 |

## 安装

### Windows

下载 `MarkAny-Setup-1.0.0.exe` 运行安装即可，无需配置任何环境。

### Mac 安装说明

1. 下载 `MarkAny-1.0.1-mac.dmg`
2. 打开 DMG，拖拽到应用程序文件夹
3. **首次打开如果提示"已损坏"**，在终端运行：
```bash
   sudo xattr -rd com.apple.quarantine /Applications/MarkAny.app
```
   然后重新打开即可

## 使用方法

1. 选择源文件格式（或选择"自动检测"）
2. 拖放或点击选择文件
3. 设置输出目录（默认与原文件相同目录）
4. 点击"开始转换"

## 系统要求

- Windows 10/11 (64位)
- 约 500MB 可用磁盘空间

## 联系作者

- 邮箱：zjsthm@gmail.com