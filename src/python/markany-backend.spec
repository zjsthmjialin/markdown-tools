# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Get the directory where this spec file is located
script_dir = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    [os.path.join(script_dir, 'main.py')],
    pathex=[script_dir],
    binaries=[],
    datas=[],
    hiddenimports=[
        'http.server',
        'converters.markitdown_converter',
        'converters.pdf_converter',
        'utils.image_extractor',
        'markitdown',
        'pymupdf',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='markany-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)