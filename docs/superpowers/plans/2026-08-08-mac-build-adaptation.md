# MarkAny macOS 适配计划（v1.0.3-mac）

> **For agentic workers:** 本计划配套逐条命令见仓库根目录 `MAC_BUILD_STEPS.md`。步骤用 checkbox（`- [ ]`）跟踪。
> 因为需 macOS 原生打包 + 已认证 `gh`，阶段 1 起的构建/推送/发布均需在 **Mac 本机终端**执行。

**目标：** 在不重写的前提下，把 `mac-build` 分支合并 `master` 的 v1.0.3 核心改进后适配为可用的 macOS 版本，产出未签名 `.dmg` 并发布 `v1.0.3-mac`。

**非目标：**
- 不做 Apple 开发者签名 / 公证（自用，未签名 dmg + `xattr` 去隔离即可）
- 不改动 Windows 版行为；不合并进 `master`（由 owner review PR 后自行决定）
- 不新增转换功能（Mac 与 Windows 共用同一套 Python 核心，功能对齐即可）

**边界文档（以这些为准，不另造）：**
- `MAC_BUILD_PROMPT.md` —— 本次任务指令与约束
- `CLAUDE.md` —— 项目上下文/边界（`master` 有，`mac-build` 被删；**合并后回归，以其为准**）
- `docs/ISSUES.md` —— 已知问题清单（含死代码 `src/python/markdown/` 需删除）
- `docs/superpowers/specs/2026-05-12-markany-design.md` —— 原始设计 spec

**架构要点（Mac 与 Windows 的差异）：**
- 后端运行方式：Windows = PyInstaller `markany-backend.exe`；macOS = 便携 CPython 直接跑 `python-source/main.py`（`ipc-handlers.ts` 按 `process.platform` 分支）
- OCR：Windows 绑定 `tesseract.exe`+DLL；macOS 绑定 Homebrew tesseract 二进制 + dylib（`install_name_tool` 重定位）+ `tessdata`（chi_sim+eng）
- 打包：`electron-builder` 分平台 `extraResources`；新增 `mac(dmg/arm64)` 目标

---

## 合并冲突处置（merge master → mac-build）

分叉点 `52551c0` 之后两边都改过的文件仅 6 个；处置原则：**Python 核心取 master v1.0.3，Electron/打包保留 mac-build 的 Mac 适配。**

- [ ] `electron-builder.yml` → 用定稿覆盖（分平台 extraResources；修复 python-source 漏打 `ocr/`）
- [ ] `package.json` → 用定稿覆盖（version=1.0.3；新增 build:mac / tesseract:setup:mac / python:portable:mac）
- [ ] `.gitignore` → 用定稿覆盖（新增 portable-python/、tesseract-portable-mac/）
- [ ] `README.md` → 用定稿覆盖（补 macOS 安装说明 + v1.0.3-mac 更新日志）
- [ ] `src/main/ipc-handlers.ts` → 用定稿覆盖（保留 darwin 便携 Python 分支 + 30 分钟超时）
- [ ] `src/python/main.py` → 取 master（`git checkout --theirs`，v1.0.3 http.server + options + 健康检查）
- [ ] `src/python/requirements.txt` → 覆盖（markitdown 改 `[docx,pptx,xlsx]` extra，修复 docx 转换缺依赖）
- [ ] `dist-electron/main/index.js` 及 `*.pyc` 冲突 → 取 master（构建会重生成）
- [ ] **死代码目录 `src/python/markdown/`** → 若出现 modify/delete 冲突，直接删除（`git rm -r src/python/markdown`）；依据 `docs/ISSUES.md`，已无任何引用

## 新增 / 改写的 Mac 专属代码

- [ ] `src/python/ocr/tesseract_ocr.py` → 覆盖为含 macOS 路径发现分支的版本
- [ ] `src/python/setup_tesseract_mac.sh` → 新增（Homebrew tesseract → 可重定位捆绑）
- [ ] `src/python/setup_portable_python_mac.sh` → 新增（便携 CPython + 依赖）

---

## 阶段与验收（详见 MAC_BUILD_STEPS.md）

- [ ] **阶段 0**：`brew install tesseract tesseract-lang`；`npm install`；确认芯片架构（arm64 / Intel 改两行）
- [ ] **阶段 1**：`git merge master` + 按上表解决冲突 + 放入新文件（**先不 commit，待实测通过**）
      · ✅ 已在沙箱预跑验证：冲突解决无残留、Python 7/7 单测通过、转换器与 main.py 可导入
- [ ] **阶段 2**：`npm run build:mac` 产出 `release/MarkAny-1.0.3-mac-arm64.dmg`
  - 验收：`setup_tesseract_mac.sh` 末尾 `otool -L` 无绝对 Homebrew 路径 + `tesseract --version` 自检通过；便携 Python 自检 `all imports ok`
- [ ] **阶段 3**：装 dmg（`xattr -rd com.apple.quarantine`）实测：文字版 PDF / 扫描版 PDF(OCR) / docx 均转出 `.md` 且中文不乱码
- [ ] **阶段 4**：`git commit`（中文说明）+ `git push origin mac-build`（**不推 master**）
- [ ] **阶段 5**：`gh pr create --base master --head mac-build`，交 owner review
- [ ] **阶段 6**（合并/确认后）：`git tag -a v1.0.3-mac` + `git push` + `gh release create v1.0.3-mac release/*.dmg`

## 风险 / 需在 Mac 上迭代的点

- dylib 重定位：`setup_tesseract_mac.sh` 若自检失败，按 `otool -L` 补缺失 dylib 重跑
- `python-build-standalone` 下载 URL 若 404：改 `PBS_TAG`/`PY_VERSION` 重跑
- `electron-builder` 平台级 `extraResources` 已改为分平台声明，避免 mac 构建误拷 Windows 产物
