# -*- mode: python ; coding: utf-8 -*-

import os
import sys

a = Analysis(
    ['PCBcoilV2.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pcbnew'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

# Add KiCad-specific files
kicad_files = [
    ('_pcbnew.so', '/usr/lib/python3.12/site-packages/_pcbnew.so', 'BINARY'),
    ('pcbnew.py', '/usr/lib/python3.12/site-packages/pcbnew.py', 'DATA'),
]

exe = EXE(
    pyz,
    a.scripts,
    a.binaries + kicad_files,
    a.datas,
    [],
    name='Coilgen_V3.6_3',  
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)