# -*- mode: python ; coding: utf-8 -*-
import sys

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'fitz',
        'docx',
        'openpyxl',
        'pptx',
        'bs4',
        'html2text',
        'reportlab',
        'reportlab.lib',
        'reportlab.platypus',
        'reportlab.pdfbase',
        'reportlab.pdfbase.ttfonts',
        'pytesseract',
        'PIL',
        'markdown',
        'markitdown',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['weasyprint', 'pdfplumber', 'chardet', 'tkinter', 'matplotlib'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='markany-backend',
    debug=False,
    console=True,
    argv_emulation=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='markany-backend',
)
