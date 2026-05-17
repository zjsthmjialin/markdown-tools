# MarkAny 文档转 Markdown 工具

## 功能简介

MarkAny 是一款简洁高效的桌面应用，将 PDF、Word、Excel、PowerPoint、HTML 等格式文档转换为 Markdown，无需安装任何额外软件。

## 安装

双击运行 `MarkAny-Setup-1.0.0.exe`，按照提示完成安装。

## 使用方法

1. 打开 MarkAny
2. 选择源文件格式（默认"自动检测"即可）
3. 拖放文件到窗口，或点击"点击选择文件"按钮
4. 设置输出目录（默认与原文件相同）
5. 点击"开始转换"
6. 转换完成后，文件保存在输出目录

## 支持格式

| 格式类型 | 扩展名 | 处理方式 |
|---------|--------|----------|
| PDF | .pdf | PyMuPDF + OCR |
| Word | .docx, .doc | MarkItDown |
| Excel | .xlsx, .xls | MarkItDown |
| PowerPoint | .pptx, .ppt | MarkItDown |
| HTML | .html, .htm | MarkItDown |
| 纯文本 | .txt | 自动编码检测 |

## 特性

- 图片自动提取保存到 images 文件夹
- 扫描件 PDF 支持 OCR 识别
- 批量文件转换
- 无需 Microsoft Office 或 Adobe Acrobat

## 联系作者

邮箱：zjsthm@gmail.com