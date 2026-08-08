#!/bin/bash
# Assemble portable Tesseract OCR for bundling with the Electron app.
# Run this once before building the installer.
set -euo pipefail

DEST_DIR="$(cd "$(dirname "$0")" && pwd)/tesseract-portable"

# --- Locate system Tesseract ---
TESSERACT_DIR=""
for candidate in \
  "/c/Program Files/Tesseract-OCR" \
  "/c/Program Files (x86)/Tesseract-OCR" \
  "C:/Program Files/Tesseract-OCR" \
  "C:/Program Files (x86)/Tesseract-OCR"; do
  if [ -f "$candidate/tesseract.exe" ]; then
    TESSERACT_DIR="$candidate"
    break
  fi
done

if [ -z "$TESSERACT_DIR" ]; then
  echo "ERROR: Tesseract OCR not found. Please install it first:"
  echo "  https://github.com/UB-Mannheim/tesseract/wiki"
  exit 1
fi

echo "Using Tesseract from: $TESSERACT_DIR"

# --- Copy tesseract.exe ---
cp -v "$TESSERACT_DIR/tesseract.exe" "$DEST_DIR/"

# --- Copy all DLLs (exclude .exe training tools to keep size down) ---
echo "Copying DLLs..."
copied=0
for dll in "$TESSERACT_DIR"/*.dll; do
  dll_name="$(basename "$dll")"
  cp -v "$dll" "$DEST_DIR/" 2>/dev/null && ((copied++)) || true
done
echo "Copied $copied DLL(s)"

# --- Copy tessdata ---
echo "Copying tessdata..."
for traineddata in "$TESSERACT_DIR/tessdata/"*.traineddata; do
  cp -v "$traineddata" "$DEST_DIR/tessdata/"
done

# Copy pdf.ttf (needed by some Tesseract configs)
if [ -f "$TESSERACT_DIR/tessdata/pdf.ttf" ]; then
  cp -v "$TESSERACT_DIR/tessdata/pdf.ttf" "$DEST_DIR/tessdata/"
fi

# --- Download chi_sim.traineddata if missing ---
if [ ! -f "$DEST_DIR/tessdata/chi_sim.traineddata" ]; then
  echo "Downloading chi_sim.traineddata (Chinese Simplified)..."
  curl -L -o "$DEST_DIR/tessdata/chi_sim.traineddata" \
    "https://github.com/tesseract-ocr/tessdata_fast/raw/main/chi_sim.traineddata"
  echo "Downloaded chi_sim.traineddata (fast)"
else
  echo "chi_sim.traineddata already present"
fi

# --- Report ---
echo ""
echo "=== Tesseract portable bundle assembled ==="
echo "Location: $DEST_DIR"
echo "Size: $(du -sh "$DEST_DIR" | cut -f1)"
echo "Files:"
ls -la "$DEST_DIR/tesseract.exe" "$DEST_DIR/tessdata/"
