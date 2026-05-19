# MarkAny 文档转 Markdown 工具

## 功能简介

MarkAny 是一款简洁高效的桌面应用，将 PDF、Word、Excel、PowerPoint、HTML 等格式文档转换为 Markdown。内置 Tesseract OCR 引擎和中英文语言包，扫描件 PDF 也能识别，无需安装任何额外软件。

## 安装

双击运行 `MarkAny-Setup-1.0.0.exe`，按照提示完成安装。

> 安装过程中如遇到 Windows SmartScreen 提示"Windows 已保护你的电脑"，点击"更多信息" → "仍要运行"即可。

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
| PDF（文字版） | .pdf | PyMuPDF 文本提取 |
| PDF（扫描件） | .pdf | 渲染为图片 + OCR 识别 |
| Word | .docx, .doc | MarkItDown |
| Excel | .xlsx, .xls | MarkItDown |
| PowerPoint | .pptx, .ppt | MarkItDown |
| HTML | .html, .htm | MarkItDown |
| 纯文本 | .txt | 自动编码检测 |

## 特性

- 自动检测扫描版 PDF 并触发 OCR
- OCR 支持中英文混合识别
- 图片自动提取保存到 `images/` 文件夹
- 批量文件转换
- 无需 Microsoft Office 或 Adobe Acrobat

## 常见问题

**Q: 扫描版 PDF 转换效果不好？**
OCR 识别质量取决于原始扫描件的清晰度。建议使用 300 DPI 或更高清晰度的扫描件。模糊、倾斜或低对比度的扫描件会影响识别效果。

**Q: 转换 Word 文件报错？**
请确保 Word 文件未被其他程序占用，且文件完整未损坏。如仍有问题，请将错误提示截图反馈。

**Q: 安装包为什么这么大（约 210MB）？**
安装包内置了完整的 Tesseract OCR 引擎及中英文语言数据包，确保用户无需单独安装任何组件即可使用 OCR 功能。

## 联系作者

邮箱：zjsthm@gmail.com