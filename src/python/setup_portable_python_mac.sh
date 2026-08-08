#!/bin/bash
# Build a relocatable, self-contained CPython for bundling into the macOS .app.
#
# 自动从 python-build-standalone（astral-sh）最新发布中挑选匹配的 "install_only"
# 构建（可重定位），解压到 src/python/portable-python/，再装后端依赖。
# 运行时由 Electron 主进程调用 python-portable/bin/python3 跑 python-source/main.py。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST_DIR="$SCRIPT_DIR/portable-python"

ARCH="${ARCH:-aarch64}"          # aarch64 = Apple 芯片；Intel Mac 设 ARCH=x86_64
PY_SERIES="${PY_SERIES:-3.12}"   # CPython 主版本系列

echo "==> 解析 python-build-standalone 最新可用构建（$PY_SERIES, ${ARCH}-apple-darwin, install_only）"
URL="$(curl -fsSL https://api.github.com/repos/astral-sh/python-build-standalone/releases/latest 2>/dev/null \
  | python3 -c "
import sys, json, re
try:
    d = json.load(sys.stdin)
except Exception:
    print(''); sys.exit()
pat = re.compile(r'^cpython-' + re.escape('$PY_SERIES') + r'\.\d+\+.*-' + re.escape('$ARCH') + r'-apple-darwin-install_only\.tar\.gz$')
cands = [a['browser_download_url'] for a in d.get('assets', []) if pat.match(a['name'])]
print(cands[0] if cands else '')
" 2>/dev/null)"

if [ -z "$URL" ]; then
  echo "   未能从 latest 解析到匹配资产，回退到已知版本（如仍失败请把输出发我换版本）"
  URL="https://github.com/astral-sh/python-build-standalone/releases/download/20250612/cpython-3.12.11+20250612-${ARCH}-apple-darwin-install_only.tar.gz"
fi
echo "   下载: $URL"

echo "==> 清理 $DEST_DIR"
rm -rf "$DEST_DIR"; mkdir -p "$DEST_DIR"

TMP_TGZ="$SCRIPT_DIR/_pbs_download.tar.gz"
curl -fL "$URL" -o "$TMP_TGZ"

echo "==> 解压（install_only 包顶层为 python/，strip 掉一层）"
tar -xzf "$TMP_TGZ" -C "$DEST_DIR" --strip-components=1
rm -f "$TMP_TGZ"

PYBIN="$DEST_DIR/bin/python3"
if [ ! -x "$PYBIN" ]; then
  echo "ERROR: 未找到 $PYBIN，检查解压结构（应为 portable-python/bin/python3）"; exit 1
fi
echo "==> 便携 Python：$("$PYBIN" --version)"

echo "==> 升级 pip 并安装后端依赖"
"$PYBIN" -m pip install --upgrade pip
"$PYBIN" -m pip install -r "$SCRIPT_DIR/requirements.txt"

echo "==> 快速自检：关键模块可导入"
"$PYBIN" - <<'PY'
import importlib
for m in ("fitz","cv2","numpy","PIL","pytesseract","markitdown","docx","pptx","openpyxl","mammoth"):
    importlib.import_module(m); print("  ok:", m)
print("all imports ok")
PY

echo "==> 完成，便携 Python 已就绪：$DEST_DIR"
