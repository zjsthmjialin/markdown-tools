# MarkAny 项目问题清单

> 检查日期：2026-07-07 · 版本 v1.0.3
> 修复日期：2026-07-07
> 背景：项目已重构为「文档 → Markdown」单向转换，反向转换（Markdown → 文档）功能被移除，但存在重构遗留的引用未清理。

---

## 🔴 阻断级（会导致功能报错）

### 1. `markdown` 包导入失败 — ✅ 已修复
- **位置**：`src/python/markdown/__init__.py`
- **问题**：`from .to_document import MarkdownToDocument`，但 `to_document.py` 已删除。
- **处理**：`__init__.py` 已清空为注释占位（不再导入已删除模块）。
- **遗留**：目录本身及旧 `__pycache__/*.pyc` 因沙箱挂载禁止删除未能移除，**建议你在本机手动删除整个 `src/python/markdown/` 目录**（已无任何代码引用它，纯死代码）。

### 2. Python 测试无法运行 — ✅ 已修复
- **位置**：`src/python/tests/test_converters.py`
- **处理**：移除 `from markdown.to_document import ...` 及整个 `TestMarkdownToDocument` 类，仅保留 `TestMarkItDownConverter`、`TestPDFConverter`。文件已整体重写为干净版本。

---

## 🟡 潜在风险 / 死依赖

### 3. 冗余依赖 `markdown` — ✅ 已修复
- **位置**：`src/python/requirements.txt`
- **处理**：已删除 `markdown>=3.5.0`（正向转换不再使用）。删除本机 `markdown/` 目录后，命名遮蔽问题一并消除。

---

## 🟢 文档 / 文案过时（不影响运行）

### 4. `CLAUDE.md` 架构描述 — ✅ 无需修改（原判定有误）
- 复查后 `CLAUDE.md` 的 converters 列表（`pdf_converter` / `markitdown_converter` / `base`）与实际一致，不存在 `docx_converter` 等虚构项。初次检查时误将 `__pycache__` 中的历史 `.pyc` 当成了文档内容。

### 5. UI 标语仍称「双向转换」 — ✅ 已修复
- **位置**：`src/renderer/components/Header.tsx`
- **处理**：标语改为「将 PDF、Word、Excel、PPT、HTML 等格式转换为 Markdown」。

---

## ⚪ 未提交改动（需你确认，未处理）

### 6. 工作区有未提交文件
- 含 `dist-electron/main/index.js`（构建产物）、`test_files/*`（测试输出）等。
- **建议**：将 `dist-electron/`、`test_output/`、测试产物加入 `.gitignore` 而非入库；确认无误后再连同本次修复一起提交。

---

## 修复验证
- 四处源码改动均已通过 Windows 侧读取确认内容干净、正确。
- 在干净副本上验证 `import markdown` 不再报错、`test_converters.py` 语法通过、已无 `to_document` 残留引用。
- 完整 `npm run test:python` / `npm run test`（需安装依赖）建议在本机执行以做端到端确认；正向转换主链路与前端 TS 类型检查此前已通过。
