#!/bin/bash
# Assemble a portable, relocatable Tesseract OCR for bundling into the macOS .app.
#
# 用 dylibbundler 递归收集 tesseract 的全部 dylib 依赖（含通过 @rpath 间接引用的传递依赖），
# 拷进 lib/ 并把加载路径改写为 @executable_path/lib/；随后 ad-hoc 重签名（install_name_tool/
# dylibbundler 改过 Mach-O 会使签名失效 → Apple 芯片 Killed/Abort）。语言包 chi_sim + eng 一并拷入。
#
# 前置：brew install tesseract tesseract-lang dylibbundler
# 产出：src/python/tesseract-portable-mac/{tesseract, lib/*.dylib, tessdata/*.traineddata}
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST_DIR="$SCRIPT_DIR/tesseract-portable-mac"
LIB_DIR="$DEST_DIR/lib"
TESSDATA_DIR="$DEST_DIR/tessdata"
BREW_PREFIX="$(brew --prefix 2>/dev/null || echo /opt/homebrew)"

# --- 定位 tesseract ---
TESS_BIN="$(command -v tesseract || true)"
if [ -z "$TESS_BIN" ]; then
  echo "ERROR: 未找到 tesseract。请先：brew install tesseract tesseract-lang"; exit 1
fi
TESS_BIN="$(python3 -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' "$TESS_BIN")"
echo "Using tesseract: $TESS_BIN"

# --- 确保 dylibbundler 可用 ---
if ! command -v dylibbundler >/dev/null 2>&1; then
  echo "==> 安装 dylibbundler"; brew install dylibbundler
fi

rm -rf "$DEST_DIR"; mkdir -p "$DEST_DIR" "$LIB_DIR" "$TESSDATA_DIR"
cp -v "$TESS_BIN" "$DEST_DIR/tesseract"; chmod +w "$DEST_DIR/tesseract"

# --- 递归打包依赖并改写路径 ---
echo "==> dylibbundler 收集依赖"
dylibbundler --overwrite-dir --bundle-deps --create-dir \
  --fix-file "$DEST_DIR/tesseract" \
  --dest-dir "$LIB_DIR" \
  --install-path "@executable_path/lib/" \
  --search-path "$BREW_PREFIX/lib"

# --- ad-hoc 重签名（改过 Mach-O 后必须重签，否则 Killed/Abort）---
echo "==> ad-hoc 重签名"
for lib in "$LIB_DIR"/*.dylib; do [ -e "$lib" ] && codesign --force -s - "$lib" 2>/dev/null || true; done
codesign --force -s - "$DEST_DIR/tesseract" 2>/dev/null || true

# --- 拷贝语言数据（优先 brew --prefix 的聚合 tessdata）---
CANDS=("$BREW_PREFIX/share/tessdata" "/opt/homebrew/share/tessdata" "/usr/local/share/tessdata"
       "$(cd "$(dirname "$TESS_BIN")/.." && pwd)/share/tessdata")
BREW_SHARE=""
for c in "${CANDS[@]}"; do
  if [ -f "$c/chi_sim.traineddata" ] || [ -f "$c/eng.traineddata" ]; then BREW_SHARE="$c"; break; fi
done
echo "tessdata 来源: ${BREW_SHARE:-未找到}"
for lang in eng chi_sim chi_sim_vert osd; do
  if [ -n "$BREW_SHARE" ] && [ -f "$BREW_SHARE/$lang.traineddata" ]; then
    cp "$BREW_SHARE/$lang.traineddata" "$TESSDATA_DIR/" && echo "  + $lang"
  else
    [ "$lang" = "chi_sim" ] && echo "  !! 缺 chi_sim：brew install tesseract-lang"
  fi
done

# --- 校验 ---
echo "==> 校验（--list-langs）"
if TESSDATA_PREFIX="$TESSDATA_DIR" "$DEST_DIR/tesseract" --list-langs >/tmp/_tess_check 2>&1; then
  echo "OK: 可独立运行"; sed 's/^/    /' /tmp/_tess_check
else
  echo "WARN: 仍无法独立运行。otool -L 与运行输出如下："
  otool -L "$DEST_DIR/tesseract" | sed 's/^/    /'
  echo "---- 运行输出 ----"; sed 's/^/    /' /tmp/_tess_check
fi
echo "==> 完成，产出目录: $DEST_DIR"
