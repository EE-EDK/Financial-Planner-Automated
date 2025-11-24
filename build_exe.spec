# PyInstaller spec file for Financial Hub Builder
# Usage: pyinstaller build_exe.spec

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['run_financial_hub.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('financial_docs/build_all.py', 'financial_docs'),
        ('financial_docs/scripts/*.py', 'financial_docs/scripts'),
        ('financial_docs/Archive', 'financial_docs/Archive'),
    ],
    hiddenimports=[],
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
    name='FinancialHub',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console visible to see errors
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None  # Add icon path here if you have one
)
