<div align="center">

# MarkAny

**简洁高效的桌面应用 —— 将 PDF / Word / Excel / PowerPoint / HTML 一键转换为 Markdown**

无需安装 Office、Adobe Acrobat 或单独的 OCR 引擎，下载即用。

<br/>

[![Platform](https://img.shields.io/badge/平台-Windows%20%7C%20macOS-2b7de9?style=flat-square)](https://github.com/zjsthmjialin/markdown-tools/releases/latest)
[![Release](https://img.shields.io/github/v/release/zjsthmjialin/markdown-tools?style=flat-square&label=版本&color=44cc11)](https://github.com/zjsthmjialin/markdown-tools/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/zjsthmjialin/markdown-tools/total?style=flat-square&label=下载量&color=f39c12)](https://github.com/zjsthmjialin/markdown-tools/releases)
![Electron](https://img.shields.io/badge/Electron-29-47848F?style=flat-square&logo=electron&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)

</div>

---

## 下载

<div align="center">

[![下载 Windows 版](https://img.shields.io/badge/下载-Windows%20安装包-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/zjsthmjialin/markdown-tools/releases/download/v1.0.3/MarkAny-Setup-1.0.3.exe)
&nbsp;&nbsp;
[![下载 macOS 版](https://img.shields.io/badge/下载-macOS%20安装包-000000?style=for-the-badge&logo=apple&logoColor=white)](https://github.com/zjsthmjialin/markdown-tools/releases/download/v1.0.3/MarkAny-1.0.3-mac-arm64.dmg)

</div>

| 操作系统 | 安装包 | 说明 |
|:---|:---|:---|
| **Windows** 10 / 11（64 位） | [`MarkAny-Setup-1.0.3.exe`](https://github.com/zjsthmjialin/markdown-tools/releases/download/v1.0.3/MarkAny-Setup-1.0.3.exe) | 双击安装，约 245 MB，已内置 OCR 引擎 |
| **macOS** 12+（Apple 芯片 / arm64） | [`MarkAny-1.0.3-mac-arm64.dmg`](https://github.com/zjsthmjialin/markdown-tools/releases/download/v1.0.3/MarkAny-1.0.3-mac-arm64.dmg) | 拖入「应用程序」即可，已内置 OCR 引擎 |

> Windows 与 macOS 为各自独立的安装包，均已内置 Tesseract OCR 引擎及中英文语言包，下载后直接安装、无需任何额外配置。完整历史版本见 **[Releases 页面](https://github.com/zjsthmjialin/markdown-tools/releases)**。

---

## 功能特点

- **多格式支持** —— PDF、DOCX、DOC、XLSX、XLS、PPTX、PPT、HTML、HTM、TXT → Markdown
- **格式保留** —— PDF 转换保留粗体、斜体、标题层级等格式
- **图片提取** —— 自动提取文档中的图片并保存
- **OCR 识别** —— 扫描件 / 图片版 PDF 通过内置 Tesseract OCR 识别中英文文本，无需额外安装
- **智能分流** —— 自动检测文字版 / 扫描版 PDF，文字版快速提取，扫描版 OCR 兜底
- **批量处理** —— 一次添加多个文件批量转换
- **跨平台** —— 提供 Windows（.exe）与 macOS（.dmg）两种安装包，共用同一套转换核心
- **零依赖** —— 无需 Microsoft Office、Adobe Acrobat 或单独安装 Tesseract OCR
- **简洁界面** —— 拖放操作，开箱即用

---

## 支持格式

| 格式类型 | 支持扩展名 | 处理方式 |
|:---|:---|:---|
| PDF（文字版） | `.pdf` | PyMuPDF 结构化提取（保留粗体 / 斜体 / 标题） |
| PDF（扫描件） | `.pdf` | 图片渲染 + OpenCV 增强 + Tesseract OCR（中英文） |
| Word | `.docx` `.doc` | MarkItDown |
| Excel | `.xlsx` `.xls` | MarkItDown |
| PowerPoint | `.pptx` `.ppt` | MarkItDown |
| HTML | `.html` `.htm` | MarkItDown |
| 纯文本 | `.txt` | 自动编码检测 |

---

## 安装

### Windows

下载 [`MarkAny-Setup-1.0.3.exe`](https://github.com/zjsthmjialin/markdown-tools/releases/download/v1.0.3/MarkAny-Setup-1.0.3.exe) 运行安装即可，无需配置任何环境。安装包约 245 MB（已内置 Tesseract OCR 引擎及中英文语言包）。

### macOS

1. 下载 [`MarkAny-1.0.3-mac-arm64.dmg`](https://github.com/zjsthmjialin/markdown-tools/releases/download/v1.0.3/MarkAny-1.0.3-mac-arm64.dmg)（Apple 芯片）
2. 打开 DMG，将 **MarkAny** 拖入「应用程序」文件夹
3. 首次打开如提示「已损坏」或「无法验证开发者」，在终端执行一次：

   ```bash
   sudo xattr -rd com.apple.quarantine /Applications/MarkAny.app
   ```

   然后重新打开即可（应用未做 Apple 签名 / 公证，这是自用未签名 App 的正常提示）。

---

## 使用方法

1. 选择源文件格式（或选择「自动检测」）
2. 拖放或点击选择文件
3. 设置输出目录（默认与原文件相同目录）
4. 点击「开始转换」

---

## OCR 说明

扫描版 PDF 的转换流程：

1. 自动检测 PDF 是否为扫描件（按页面图片 / 文字比例判断）
2. 对图片页面渲染为 300 DPI 图像
3. OpenCV 图像增强（灰度 + 去噪 + CLAHE 对比度增强，二值化交由 Tesseract 内部完成）
4. 调用内置 Tesseract OCR 识别中英文文本
5. 对识别结果进行文本清洗（去除控制字符）

> OCR 质量取决于原始扫描件的清晰度，清晰度越高识别效果越好。

---

## 技术栈

| 层 | 技术 |
|:---|:---|
| 界面 | React 18 + TypeScript + Vite |
| 桌面外壳 | Electron 29 |
| 转换后端 | Python（PyMuPDF + Microsoft MarkItDown） |
| OCR | Tesseract 5 + OpenCV 图像增强 |
| 打包 | electron-builder（Windows NSIS / macOS dmg）+ PyInstaller / 便携 Python |

---

## 更新日志

### v1.0.3
- 重构 PDF 转 Markdown 核心转换逻辑；文字版使用 PyMuPDF dict 格式提取，保留粗体、斜体、标题层级
- 全局字体检测：跨文档统计正文字号 / 字体，避免版权页等特殊页粗体误判
- 扫描版 PDF：自动检测 + OpenCV 图像增强 + OCR 兜底；页间分隔改为 `---` 分隔线
- 新增 `forceOCR` 选项；添加 PyInstaller `_MEIPASS` 路径检测，完善打包兼容性
- 打包改为 onedir 模式并排除 chardet，修复部分环境安装后无法启动、后端崩溃（0xC0000005）的问题
- **macOS 适配**：便携 Python 运行后端、绑定 macOS 版 Tesseract（含 chi_sim + eng），新增 electron-builder `mac`（dmg / arm64）目标，转换功能与 Windows 完全一致
- **OCR 修复**：移除扫描件增强中的手工自适应二值化，改为灰度交给 Tesseract 内部二值化，修复部分扫描件识别乱码

### v1.0.2
- 添加自适应图像增强提升扫描件 OCR 质量
- 延长 HTTP 请求超时至 30 分钟以支持大型扫描件 OCR

### v1.0.0
- 初始发布

---

## 系统要求

- **Windows** 10 / 11（64 位），或 **macOS** 12+（Apple 芯片）
- 约 500 MB 可用磁盘空间

---

## 联系作者

- 邮箱：**zjsthm@gmail.com**
