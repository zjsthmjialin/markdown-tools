# Mac 版构建提示词（在 Mac 上使用）

> 用途：等你在 Mac 上准备把 MarkAny 从 Windows 版适配为 macOS 版时，把下面 `====` 之间的内容整段复制给编码 agent（Claude Code / Cowork 等）作为起始提示词。

====

你是在一台 **macOS** 机器上工作。请帮我把 MarkAny 这个 Electron + Python 桌面应用从 Windows 版适配为 macOS 可用版本，并完成打包、推送和发布。

## 项目背景
- 仓库：https://github.com/zjsthmjialin/markdown-tools （我是 owner `zjsthmjialin`，本机 `gh` 已认证）
- 当前版本 **v1.0.3**，`master` 分支已推送，`v1.0.3` 标签已存在于本地和远程
- 技术栈：Electron 29 + React 18 + TypeScript（前端）↔ IPC ↔ Python 后端（http.server + PyMuPDF + MarkItDown + Tesseract OCR），Python 用 PyInstaller 打包
- 功能：把 PDF / Word / Excel / PowerPoint / HTML / TXT 转成 Markdown，扫描件走 Tesseract OCR
- **重要：远程已有一个 `mac-build` 分支和一个 `v1.0.0-mac` 标签**，之前起过 Mac 适配。开工前先 `git fetch --all --tags`，checkout 并审查 `mac-build` 分支，判断能否在它基础上继续，而不是从零重写。

## 第一步：先摸清状态（先只读，不要改）
1. `git fetch origin --tags`，`git log --oneline -15 origin/master`，`git log --oneline origin/mac-build`
2. 对比 `mac-build` 与 `master` 的差异：`git diff master..origin/mac-build --stat`
3. 阅读 `CLAUDE.md`、`package.json`、`electron-builder.yml`、`src/python/markany-backend.spec`、`src/python/setup_tesseract.sh`、`src/python/ocr/tesseract_ocr.py`、`src/main/index.ts`
4. 把「为出 Mac 版需要改的点」列成清单给我确认后再动手

## 需要处理的 macOS 适配点（预期，以实际代码为准）
- **PyInstaller**：在 macOS 上重跑 `python:build`，产出原生 Mac 可执行文件（PyInstaller 不能跨平台，Windows 产物不可用）
- **Tesseract 绑定**：`setup_tesseract.sh` 目前拷 Windows 的 `tesseract.exe` + DLL；Mac 需改为绑定 macOS 版 tesseract 二进制及其依赖（可用 Homebrew 的 tesseract 作为来源），并确认 `tessdata`（chi_sim + eng）路径正确
- **运行时路径发现**：`src/python/ocr/tesseract_ocr.py` 里查找 tesseract 的逻辑要覆盖 macOS 的 app 内路径；注意 `.app` 包内资源路径与 Windows 不同
- **electron-builder**：`electron-builder.yml` 增加 `mac` 目标（`dmg` + `zip`，`target` 按 arch 选 `x64`/`arm64` 或 universal），把 PyInstaller 产物和 tesseract 作为 `extraResources` 打进 `.app`；如需签名/公证再配 `mac.identity` / notarize（没有开发者证书可先出未签名 dmg，自用够了）
- **主进程 spawn**：`src/main/index.ts` 里 spawn Python 后端的可执行文件名/路径按平台区分（Win 是 `.exe`，Mac 无后缀），用 `process.platform` 分支
- **脚本**：`package.json` 里的 `build` 脚本目前是 `--win`，加一个 `build:mac`（`tesseract:setup` 的 Mac 变体 → `python:build` → `tsc` → `vite build` → `electron-builder --mac`）
- 路径分隔符、`process.platform === 'darwin'` 的窗口行为（无边框标题栏在 Mac 上的表现）等细节

## 构建与验证
- 在 Mac 上跑 `npm install` → `npm run test:all` → 你新增的 `npm run build:mac`
- 装上生成的 `.dmg`/`.app`，实测：拖入一个文字版 PDF、一个扫描版 PDF（验证 OCR）、一个 docx，确认都能正常转出 `.md` 且中文不乱码
- 有问题就修，直到 Mac 版能跑通

## 分支、版本与发布
- 在 `mac-build` 分支上工作（或从它拉新分支）。**先不要直接改 `master`**，等 Mac 版验证通过后再决定是否合并
- 决定版本号：如果 Mac 版与 Windows 功能对齐，可用 `v1.0.3-mac` 标签区分平台；若是新迭代则升到 `v1.0.4`。**先问我用哪个方案**
- 完成后：
  1. `git add` 改动，写清晰的中文 commit（如 `feat(mac): 适配 macOS 打包与 tesseract 绑定`）
  2. 推分支：`git push origin mac-build`（或新分支）
  3. 用 `gh pr create` 开 PR 让我 review，**先别直接推 master**
  4. 合并后打标签并推送：`git tag -a <版本> -m "..."`，`git push origin <版本>`
  5. 用 `gh release create <版本> <dmg路径> --title "..." --notes "..."` 发布，把 `.dmg` 作为 release 资产上传

## 约束
- 每完成一个阶段先跟我确认再进下一步，别一口气推到 master 或发 release
- 那几个未跟踪的营销文件（`marketing/`、`push-changes.bat`、`_*.png`）与本次无关，不要提交它们
- 所有 commit / PR / release 说明用中文

====
