# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Get the directory where this spec file is located
script_dir = os.path.dirname(os.path.abspath(SPEC))

# Collect magika model data needed by markitdown for file type detection
def _collect_magika_data():
    datas = []
    try:
        import magika
        magika_dir = os.path.dirname(magika.__file__)
        models_dir = os.path.join(magika_dir, 'models')
        config_dir = os.path.join(magika_dir, 'config')
        if os.path.isdir(models_dir):
            datas.append((models_dir, 'magika/models'))
        if os.path.isdir(config_dir):
            datas.append((config_dir, 'magika/config'))
    except ImportError:
        pass
    return datas

a = Analysis(
    [os.path.join(script_dir, 'main.py')],
    pathex=[script_dir],
    binaries=[],
    datas=_collect_magika_data(),
    hiddenimports=[
        'http.server',
        'converters.markitdown_converter',
        'converters.pdf_converter',
        'utils.image_extractor',
        'ocr.tesseract_ocr',
        'markitdown',
        'pymupdf',
        'PIL',
        'pytesseract',
        'magika',
        'cv2',
        'numpy',
        'html2text',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Exclude chardet: its mypyc-compiled .pyd modules crash (0xC0000005) when
    # frozen by PyInstaller. charset_normalizer (pure Python) covers charset
    # detection for requests/markitdown, so chardet is redundant here.
    excludes=['chardet'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# onedir build: keep native libraries (cv2 / numpy / pymupdf / onnxruntime) as
# real files next to the exe instead of packing them into a single-file archive.
# Single-file mode extracts everything to a temp dir at startup, which can trigger
# 0xC0000005 access-violation crashes with these heavy native deps. onedir avoids
# that and also starts much faster (no per-launch extraction).
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='markany-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='markany-backend',
)
